package routes

import (
	"database/sql"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"storageEngine/configs"

	"github.com/gorilla/mux"
)

func DeleteUniversalHandler(w http.ResponseWriter, r *http.Request) {

	vars := mux.Vars(r)
	fileID := vars["id"]
	userId := ""

	if fileID == "" || len(fileID) < 5 {
		http.Error(w, "Missing File ID ", http.StatusBadRequest)
		return
	}

	if r.Method != http.MethodDelete {
		http.Error(w, "Invalid Method Formmat need DELETE", http.StatusMethodNotAllowed)
		return
	}

	query := `
        DELETE FROM file_metadata 
        WHERE id = $1 AND user_id = $2 
        RETURNING content_hash
    `
	var contentHash string
	err := configs.DB.QueryRow(query, fileID, userId).Scan(&contentHash)
	if err != nil {
		log.Fatal(err)
		http.Error(w, "Invalid File ID or request denied", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusAccepted)
	w.Write([]byte("File deleted Sucessfully"))

	go func(contentHash string) {
		var exists int
		checkQuery := `SELECT 1 FROM file_metadata WHERE content_hash = $1 LIMIT 1`

		err := configs.DB.QueryRow(checkQuery, contentHash).Scan(&exists)

		if err == sql.ErrNoRows {
			// Safe to physical delete!

			// Reconstruct path: uploads/aa/bb/aabb...
			targetDir := filepath.Join(configs.UploadDir, contentHash[:2], contentHash[2:4], contentHash)

			// B. Remove the entire directory (original + thumbnail + etc)
			removeErr := os.RemoveAll(targetDir)
			if removeErr != nil {
				// Log this error properly in prod
				log.Fatal("Failed to delete from disk:", removeErr)
			} else {
				log.Fatal("Garbage Collected:", contentHash)
			}
		}
	}(contentHash)

}
