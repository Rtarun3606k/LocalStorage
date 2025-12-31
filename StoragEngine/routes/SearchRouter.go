package routes

import (
	"encoding/json"
	"log"
	"net/http"
	"storageEngine/database"
)

func SearchFileshandler(w http.ResponseWriter, r *http.Request) {

	userID := "fcee8517-8c07-406f-bf8f-9d11295a223c"

	query := r.URL.Query()

	params := database.SearchFilesParams{
		UserID:   userID,
		Query:    query.Get("q"),
		FileType: query.Get("type"),
		SortBy:   query.Get("sort"),
	}
	log.Println("logs params", params.Query, params.FileType, params.SortBy)

	files, err := database.SearchFiles(params)
	if err != nil {
		http.Error(w, "database ERROR", http.StatusInternalServerError)
	}

	w.Header().Set("Content-Type", "application/json")

	if files == nil {
		files = []map[string]any{}
	}
	json.NewEncoder(w).Encode(map[string]any{
		"status": "scussess",
		"count":  len(files),
		"data":   files,
	})

}
