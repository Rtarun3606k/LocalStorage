package routes

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"storageEngine/configs"
	"storageEngine/database"
	"storageEngine/utils"
	"strings"

	"github.com/gorilla/mux"
)

func OtherUploadHandler(w http.ResponseWriter, r *http.Request) {

	userId := "fcee8517-8c07-406f-bf8f-9d11295a223c" // Mock User
	// Ensure it's a POST request

	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}
	//check for other file size limit
	r.Body = http.MaxBytesReader(w, r.Body, configs.MaxUploadSizeOther)
	if err := r.ParseMultipartForm(configs.MaxUploadSizeOther); err != nil {
		http.Error(w, "File too big or malformed", http.StatusBadRequest)
		return
	}

	// Get the file from the request
	files := r.MultipartForm.File["files"]
	if len(files) == 0 {
		http.Error(w, "No files uploaded", http.StatusBadRequest)
		return
	}

	var uploadedFileIDs []string
	var failedFiles []string

	for _, fileHeader := range files {
		//block all hiden files
		if strings.HasPrefix(fileHeader.Filename, ".") {
			failedFiles = append(failedFiles, fileHeader.Filename)
			continue
		}

		// open the file and check for errors
		file, err := fileHeader.Open()
		if err != nil {
			failedFiles = append(failedFiles, fileHeader.Filename)
			continue
		}

		// Call the StoreFiles utility function
		fileID, err := utils.StoreFiles(file, fileHeader, userId)
		file.Close()
		if err != nil {
			fmt.Printf("❌ Upload Error for %s: %v\n", fileHeader.Filename, err)
			failedFiles = append(failedFiles, fileHeader.Filename)
			continue
		}
		uploadedFileIDs = append(uploadedFileIDs, fileID)
	}

	//return response json
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]any{
		"status":            "completed",
		"uploaded_file_ids": uploadedFileIDs,
		"failed_files":      failedFiles,
		"count":             len(uploadedFileIDs),
		"message": map[string]string{
			"success": fmt.Sprintf("%d files uploaded successfully", len(uploadedFileIDs)),
			"failed":  fmt.Sprintf("%d files failed to upload", len(failedFiles)),
		},
	})
}

func FileDownloadHandler(w http.ResponseWriter, r *http.Request) {
	// 1. Get the File ID from the URL
	vars := mux.Vars(r)
	fileID := vars["id"]

	if fileID == "" {
		http.Error(w, "Missing file ID", http.StatusBadRequest)
		return
	}

	// 2. Look up Metadata in DB
	meta, err := database.OtherGetFileMetadataByID(fileID)
	if err != nil {
		http.Error(w, "File not found", http.StatusNotFound)
		return
	}

	hash := meta["hash"]
	originalName := meta["name"]
	mimeType := meta["mime"]

	// 3. Reconstruct the Physical Path
	ext := filepath.Ext(originalName)
	filePath := filepath.Join(configs.UploadDir, hash[:2], hash[2:4], hash, "original"+ext)

	// 4. Verify File Exists on Disk
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		http.Error(w, "File missing from storage", http.StatusInternalServerError)
		return
	}

	// ---------------------------------------------------------
	// 5. MODIFIED: Smart Disposition (Download vs Preview)
	// ---------------------------------------------------------

	// Default to "attachment" (Force Download)
	disposition := "attachment"

	// IF the user specifically asks for ?preview=true, switch to "inline"
	if r.URL.Query().Get("preview") == "true" {
		disposition = "inline"
	}

	// Set the header dynamically
	w.Header().Set("Content-Disposition", disposition+"; filename=\""+originalName+"\"")
	w.Header().Set("Content-Type", mimeType)

	// 6. Serve the File
	http.ServeFile(w, r, filePath)
}
