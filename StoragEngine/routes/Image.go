package routes

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	config "storageEngine/configs"
	database "storageEngine/database"
)

// image upload handler
func UploadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// 1. Limit Request Size
	r.Body = http.MaxBytesReader(w, r.Body, config.MaxUploadSize)
	if err := r.ParseMultipartForm(config.MaxUploadSize); err != nil {
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
	if !config.AllowedTypes[mimeType] {
		http.Error(w, "Unsupported file type", http.StatusBadRequest)
		return
	}

	// 3. Create Temp File
	tempFile, err := os.CreateTemp(config.UploadDir, "upload-*-"+header.Filename)
	if err != nil {
		http.Error(w, "Unable to create temp file", http.StatusInternalServerError)
		return
	}
	// We handle cleanup manually based on success/failure
	defer os.Remove(tempFile.Name())

	// 4. Stream & Hash (Single Pass)
	hasher := sha256.New()
	multiWriter := io.MultiWriter(tempFile, hasher)

	// FIX 1: Only call io.Copy ONCE
	size, err := io.Copy(multiWriter, file)
	if err != nil {
		http.Error(w, "Failed to save file", http.StatusInternalServerError)
		return
	}

	// Optional: Double check size constraint (though MaxBytesReader usually catches it)
	if size > config.MaxUploadSize {
		http.Error(w, "File too big", http.StatusBadRequest)
		return
	}

	// 5. Calculate Hash & Paths
	hash := hex.EncodeToString(hasher.Sum(nil))
	filePathDir := filepath.Join(config.UploadDir, hash[:2], hash[2:4])
	finalPath := filepath.Join(filePathDir, hash)

	// 6. Deduplication Logic
	if _, err := os.Stat(finalPath); err == nil {
		// FIX 2: File exists? Great! We skip the write, BUT we proceed to DB insert.
		tempFile.Close()
		// os.Remove is handled by defer
		fmt.Println("Deduplication: File blob already exists. Skipping disk write.")
	} else {
		// File is new. Move it to permanent storage.
		if err := os.MkdirAll(filePathDir, 0755); err != nil {
			http.Error(w, "Failed to create directory", http.StatusInternalServerError)
			return
		}

		tempFile.Close() // Close before moving (Windows requirement)
		if err := os.Rename(tempFile.Name(), finalPath); err != nil {
			http.Error(w, "Failed to save file", http.StatusInternalServerError)
			return
		}
	}

	// 7. Database Insert (HAPPENS EVERY TIME)
	// TODO: Replace with real User ID from session/token
	validUserID := "fcee8517-8c07-406f-bf8f-9d11295a223c"

	fileID, err := database.InsertFileMetadata(
		validUserID,
		hash,
		header.Filename,
		header.Header.Get("Content-Type"),
		size,
	)

	if err != nil {
		// If DB fails, we don't delete the file from disk because
		// another user might own it. We just return error.
		fmt.Println("DB Insert Error:", err)
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	fmt.Fprintf(w, "File stored successfully. ID: %s\n", fileID)
} //image download handler

func DownloadHandler(w http.ResponseWriter, r *http.Request) {

	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Extract file ID from query parameters
	fileId := r.URL.Query().Get("id")
	if fileId == "" {
		http.Error(w, "File ID is required", http.StatusBadRequest)
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

	resulthash, okHash := result["content_hash"].(string)
	originalName, okName := result["original_name"].(string)
	if !okHash || !okName || resulthash == "" {
		http.Error(w, "Invalid file metadata", http.StatusInternalServerError)
		return
	}

	fmt.Println("Preparing to download file:", originalName, "with hash:", resulthash)
	// Construct file path
	filePath := filepath.Join(config.UploadDir, resulthash[:2], resulthash[2:4], resulthash)
	fmt.Println("Downloading file from path:", filePath)
	// Open the file
	file, err := os.Open(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			http.Error(w, "File not found", http.StatusNotFound)
		} else {
			http.Error(w, "Failed to open file", http.StatusInternalServerError)
		}
		return
	}
	defer file.Close()

	if result["original_name"].(string) != "" {
		w.Header().Set("Content-Disposition", "attachment; filename="+result["original_name"].(string))
	}

	//server the file
	http.ServeFile(w, r, filePath)
}
