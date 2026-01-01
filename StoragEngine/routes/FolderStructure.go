package routes

import (
	"encoding/json"
	"net/http"
	"storageEngine/database"
	"storageEngine/utils"
	"strings"

	"github.com/gorilla/mux"
)

type CreateFolderRequest struct {
	Name     string  `json:"name"`
	ParentID *string `json:"parent_id"` // Optional: null means Root
}

type MoveFolderRequest struct {
	FolderID string `json:"folder_id"`
}

type RenameFolderRequest struct {
	NewName string `json:"new_name"`
}

func CreateoFolderHandler(w http.ResponseWriter, r *http.Request) {
	userID := "fcee8517-8c07-406f-bf8f-9d11295a223c"

	var req CreateFolderRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	safename := utils.SanitizeFilename(req.Name)
	if strings.TrimSpace(safename) == "" {
		http.Error(w, "name cannot be empty", http.StatusBadRequest)
		return
	}

	folder, err := database.CreateFolder(userID, req.Name, req.ParentID)
	if err != nil {
		http.Error(w, " Database Error", http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type/", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":    "sucess",
		"folder_id": folder,
		"name":      safename})
}

//movefileHandler

func MoveFileHandler(w http.ResponseWriter, r *http.Request) {
	userID := "fcee8517-8c07-406f-bf8f-9d11295a223c"

	vars := mux.Vars(r)
	fileID := vars["id"]

	if r.Method != http.MethodPatch {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	var req MoveFolderRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	// 3. Determine Target (UUID or NULL)
	var targetID *string // Pointer allows us to set it to nil

	if req.FolderID == "root" || req.FolderID == "" {
		targetID = nil // Move to Root
	} else {
		// Simple UUID validation (length check)
		if len(req.FolderID) != 36 {
			http.Error(w, "Invalid folder ID", http.StatusBadRequest)
			return
		}
		targetID = &req.FolderID
	}

	// 4. Update Database
	err := database.MoveFile(fileID, userID, targetID)
	if err != nil {
		if err.Error() == "file not found or access denied" {
			http.Error(w, err.Error(), http.StatusNotFound)
		} else {
			http.Error(w, "Database error", http.StatusInternalServerError)
		}
		return
	}

	// 5. Success
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "success",
		"message": "File moved successfully",
	})

}

// 1. RENAME HANDLER
func RenameFolderHandler(w http.ResponseWriter, r *http.Request) {
	userID := "fcee8517-8c07-406f-bf8f-9d11295a223c" // Mock User
	vars := mux.Vars(r)
	folderID := vars["id"]

	var req RenameFolderRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	// Sanitize
	safeName := utils.SanitizeFilename(req.NewName)
	if safeName == "" {
		http.Error(w, "Name cannot be empty", http.StatusBadRequest)
		return
	}

	err := database.RenameFolder(folderID, userID, safeName)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":   "success",
		"message":  "Folder renamed successfully",
		"new_name": safeName,
	})
}

// 2. DELETE HANDLER
func DeleteFolderHandler(w http.ResponseWriter, r *http.Request) {
	userID := "fcee8517-8c07-406f-bf8f-9d11295a223c" // Mock User
	vars := mux.Vars(r)
	folderID := vars["id"]

	err := database.DeleteFolder(folderID, userID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "success",
		"message": "Folder deleted (files moved to root)",
	})
}
