package routes

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gorilla/mux"
	"storageEngine/configs"
	config "storageEngine/configs"
	database "storageEngine/database"
)

func VideoUploadHandler(w http.ResponseWriter, r *http.Request) {
	userID := "fcee8517-8c07-406f-bf8f-9d11295a223c" // Mock User
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// 1. Limit Request Size
	r.Body = http.MaxBytesReader(w, r.Body, config.MaxUploadSizeVideo)
	if err := r.ParseMultipartForm(config.MaxUploadSizeVideo); err != nil {
		http.Error(w, "File too big or malformed", http.StatusBadRequest)
		return
	}

	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Invalid file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// 2. Validate Content-Type
	mimeType := header.Header.Get("Content-Type")
	// Assuming config.AllowedTypes is a map[string]bool
	if !config.AllowedTypes[mimeType] {
		http.Error(w, "Unsupported file type", http.StatusBadRequest)
		return
	}

	// 3. Create Temp File
	tempFile, err := os.CreateTemp("", "upload-*.tmp")
	if err != nil {
		http.Error(w, "Unable to create temp file", http.StatusInternalServerError)
		return
	}
	// Clean up temp file ONLY if renaming fails later (manual cleanup)
	defer os.Remove(tempFile.Name())

	// 4. Stream & Hash (Single Pass)
	hasher := sha256.New()
	multiWriter := io.MultiWriter(tempFile, hasher)

	if _, err := io.Copy(multiWriter, file); err != nil {
		http.Error(w, "Stream copy failed", http.StatusInternalServerError)
		return
	}

	// Close temp file so we can rename it (Windows lock fix)
	tempFile.Close()

	// 5. Finalize Hash
	contentHash := hex.EncodeToString(hasher.Sum(nil))
	fmt.Println("Content Hash:", contentHash)

	checkHashExists, err := database.GetFIleMetadataByHash(contentHash)
	if err == nil && checkHashExists != nil {
		fileId, err := database.InsertFileMetadata(userID, contentHash, header.Filename, mimeType, header.Size, configs.StatusReady)
		if err != nil {
			http.Error(w, "Failed to store metadata", http.StatusInternalServerError)
			return
		}
		w.Write([]byte("File uploaded successfully with ID: " + fileId))
		return
	}
	// 6. Define Paths
	// Folder: uploads/aa/bb/aabb.../
	targetDir := filepath.Join(config.UploadDir, contentHash[:2], contentHash[2:4], contentHash)

	// Create the directory
	if err := os.MkdirAll(targetDir, 0755); err != nil {
		http.Error(w, "Storage error", http.StatusInternalServerError)
		return
	}

	// Determine extension based on original file or mime type?
	// For HLS source, let's stick to a standard name or keep extension.
	ext := filepath.Ext(header.Filename)
	finalFilePath := filepath.Join(targetDir, "original"+ext)

	// 7. Move File (Rename)
	if err := os.Rename(tempFile.Name(), finalFilePath); err != nil {
		// Fallback: If rename fails (different partitions), use Copy
		fmt.Println("Rename failed, trying copy...", err)
		http.Error(w, "Failed to store file", http.StatusInternalServerError)
		return
	}

	// 8. DB Insertion

	// Determine Status
	status := config.StatusReady
	isVideo := strings.HasPrefix(mimeType, "video/")
	if isVideo {
		status = config.StatusPending
	}
	fmt.Println("File status set to:", status)
	// Assuming InsertFileMetadata accepts status
	fileId, err := database.InsertFileMetadata(userID, contentHash, header.Filename, mimeType, header.Size, status)
	if err != nil {
		http.Error(w, "Failed to store metadata", http.StatusInternalServerError)
		return
	}

	// 9. Enqueue Job (If Video)
	if isVideo {
		select {
		case config.VideoQueue <- config.VideoJob{
			FileId:     fileId,
			SourcePath: finalFilePath,
			OutputDir:  targetDir,
		}:
			fmt.Println("Job enqueued for:", fileId)
		default:
			fmt.Println("Queue full! Video accepted but processing delayed.")
			// Ideally, you might want to fail or have a secondary buffer
		}
	}

	w.Write([]byte("File uploaded successfully with ID: " + fileId))
}

func VideoDownloadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Extract file ID from query parameters
	muxVars := mux.Vars(r)
	fileId := muxVars["id"]
	filename := muxVars["filename"]

	if fileId == "" || filename == "" {
		http.Error(w, "File ID and filename are required", http.StatusBadRequest)
		return
	}

	if len(fileId) < 10 {
		http.Error(w, "Invalid File ID", http.StatusBadRequest)
		return
	}
	// Verify file exists in DB
	result, err := database.GetFileMetadataByID(fileId)
	if err != nil {
		http.Error(w, "File not found in database", http.StatusNotFound)
		return
	}

	if result["status"] != configs.StatusReady {
		http.Error(w, "File is not ready its still being processed", http.StatusForbidden)
		return
	}

	resulthash, okHash := result["content_hash"].(string)
	originalName, okName := result["original_name"].(string)
	if !okHash || !okName || resulthash == "" {
		http.Error(w, "Invalid file metadata", http.StatusInternalServerError)
		return
	}
	log.Println("Preparing to download file:", originalName, "with hash:", resulthash)

	absConfigDir, err := filepath.Abs(config.UploadDir)
	if err != nil {
		http.Error(w, "Server Configuration Error", http.StatusInternalServerError)
		return
	}

	// B. Construct the full path to the requested file
	rawFilePath := filepath.Join(
		config.UploadDir,
		resulthash[:2],
		resulthash[2:4],
		resulthash,
		"hls",
		filename,
	)

	// C. Resolve the absolute path of the requested file
	// This resolves any ".." or "." in the path
	absFilePath, err := filepath.Abs(rawFilePath)
	if err != nil {
		http.Error(w, "Path Resolution Error", http.StatusInternalServerError)
		return
	}

	// D. Perform the Security Check
	// We compare the ABSOLUTE paths. This guarantees safety.
	if !strings.HasPrefix(absFilePath, absConfigDir) {
		fmt.Println("SECURITY BLOCK: Path Traversal Attempt")
		fmt.Println("Target:", absFilePath)
		fmt.Println("Allowed Prefix:", absConfigDir)
		http.Error(w, "Access denied", http.StatusForbidden)
		return
	} // 5. Set Content-Type (Browsers are picky about this for HLS)
	if strings.HasSuffix(filename, ".m3u8") {
		w.Header().Set("Content-Type", "application/vnd.apple.mpegurl")
	} else if strings.HasSuffix(filename, ".ts") {
		w.Header().Set("Content-Type", "video/MP2T")
	}

	// 6. Serve the file
	http.ServeFile(w, r, absFilePath)
}
