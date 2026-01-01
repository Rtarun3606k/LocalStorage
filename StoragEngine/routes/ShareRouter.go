package routes

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/gorilla/mux"
	"storageEngine/database"
	"storageEngine/utils"
)

type ShareRequest struct {
	ExpiresInHours int      `json:"expires_in_hours"` // 0 = No Expiration
	IsPublic       bool     `json:"is_public"`
	AllowedEmails  []string `json:"allowed_emails"` // Optional
}

func CreateShareLinkHandler(w http.ResponseWriter, r *http.Request) {
	userID := "fcee8517-8c07-406f-bf8f-9d11295a223c"
	vars := mux.Vars(r)
	fileID := vars["id"]

	var req ShareRequest
	_ = json.NewDecoder(r.Body).Decode(&req) // Ignore error, defaults are fine

	// 1. Generate Token
	token, err := utils.GenerateRandomToken()
	if err != nil {
		http.Error(w, "Error generating token", http.StatusInternalServerError)
		return
	}

	// 2. Calculate Expiration
	var expiresAt *time.Time
	if req.ExpiresInHours > 0 {
		t := time.Now().Add(time.Duration(req.ExpiresInHours) * time.Hour)
		expiresAt = &t
	}

	// 3. Save to DB
	savedToken, err := database.CreateShareLink(fileID, userID, token, req.IsPublic, req.AllowedEmails, expiresAt)
	if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	// 4. Return the Link
	shareURL := "http://localhost:8080/s/" + savedToken

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":     "success",
		"share_link": shareURL,
		"token":      savedToken,
	})
}

func AccessSharedFiles(w http.ResponseWriter, r *http.Response) {

}
