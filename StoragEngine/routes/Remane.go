package routes

import (
	"encoding/json"
	"github.com/gorilla/mux"
	"net/http"
	"storageEngine/database"
	"storageEngine/utils"
	"strings"
)

type RenameRequest struct {
	NewName string `json:"new_name"`
}

func Remane(w http.ResponseWriter, r *http.Request) {
	userID := "fcee8517-8c07-406f-bf8f-9d11295a223c" // Mock User

	if r.Method != http.MethodPatch {
		http.Error(w, "Method not allwoed", http.StatusMethodNotAllowed)
		return
	}
	vars := mux.Vars(r)
	fileId := vars["id"]

	if fileId == "" {
		http.Error(w, "File ID is required", http.StatusBadRequest)
		return
	}

	// 3. Header Check (FIXED: Handles 'application/json; charset=utf-8')
	contentType := r.Header.Get("Content-Type")
	if !strings.Contains(contentType, "application/json") {
		http.Error(w, "Content-Type must be application/json", http.StatusUnsupportedMediaType)
		return
	}

	var newName RenameRequest
	if err := json.NewDecoder(r.Body).Decode(&newName); err != nil {
		http.Error(w, " Invalid JSON body", http.StatusBadRequest)
		return
	}

	newname := utils.SanitizeFilename(newName.NewName)

	//db quer y to rename file
	err := database.RemaneFile(fileId, userID, newname)
	if err != nil {
		// Check exact error string from your DB function
		if err.Error() == "file not found or access denied" {
			http.Error(w, "File not found", http.StatusNotFound)
		} else {
			http.Error(w, "Database error", http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"message":  "File renamed successfully",
		"status":   "success",
		"new_name": newname,
	})

}
