package routes

import (
	"encoding/json"
	"net/http"
	"storageEngine/database"

	"github.com/gorilla/mux"
)

func ResolveTokenHandler(w http.ResponseWriter, r *http.Request) {
	//todo get userid from middleware

	//mock userid for now

	// validUserID := "fcee8517-8c07-406f-bf8f-9d11295a223c"
	mockEmail := "Alice@gmail.com"
	vars := mux.Vars(r)
	sharedID := vars["id"]

	if len(sharedID) < 6 {
		http.Error(w, "Invalid Access ID", http.StatusBadRequest)
		return
	}

	satatus, err := database.GetFileByShareToken(sharedID)
	if err != nil {
		http.Error(w, "database Error", http.StatusInternalServerError)
		return
	}

	//check asscess of ther current user
	isUserAllowed := database.CheckAccess(mockEmail, satatus["allowed_emails"].([]string), satatus["is_public"].(bool))

	if isUserAllowed == false {
		http.Error(w, "Not autorised", 401)

	}

	response := map[string]any{
		"file_id":   satatus["file_id"],
		"file_name": satatus["file_name"],
		"mime_type": satatus["mime_type"],
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}
