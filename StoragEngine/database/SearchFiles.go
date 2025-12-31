package database

import (
	"fmt"
	"log"
	"storageEngine/configs"
	"time"
)

type SearchFilesParams struct {
	UserID   string
	Query    string
	FileType string
	SortBy   string
	FolderID string
}

func SearchFiles(params SearchFilesParams) ([]map[string]any, error) {

	query := `
        SELECT id, content_hash, original_name, mime_type, size_bytes, created_at, status 
        FROM file_metadata 
        WHERE user_id = $1
    `

	args := []any{params.UserID}
	argCounter := 2

	if params.Query != "" {
		query += fmt.Sprintf(" AND original_name ILIKE $%d", argCounter)
		args = append(args, "%"+params.Query+"%") // Add % for fuzzy match
		argCounter++
	}

	if params.FileType != "" {
		if params.FileType == "other" {
			// Special Case: NOT Image AND NOT Video
			query += " AND mime_type NOT ILIKE 'image%' AND mime_type NOT ILIKE 'video%'"
		} else {
			// Normal Case: 'image' or 'video'
			query += fmt.Sprintf(" AND mime_type ILIKE $%d", argCounter)
			args = append(args, params.FileType+"%")
			argCounter++
		}
	}

	if params.FolderID == "root" {
		query += fmt.Sprintf(" AND folder_id IS NULL")
	} else if len(params.FolderID) == 36 {
		// Scenario B: If FolderID is a UUID, we want specific folder
		query += fmt.Sprintf(" AND folder_id = $%d", argCounter)
		args = append(args, params.FolderID)
		argCounter++
	}

	// 3. Dynamic Sorting
	switch params.SortBy {
	case "name_asc":
		query += " ORDER BY original_name ASC"
	case "name_desc":
		query += " ORDER BY original_name DESC"
	case "size_asc":
		query += " ORDER BY size_bytes ASC"
	case "size_desc":
		query += " ORDER BY size_bytes DESC"
	case "date_asc":
		query += " ORDER BY created_at ASC"
	default:
		// Default to newest first
		query += " ORDER BY created_at DESC"
	}
	// log.Println(query)
	// 4. Execute
	rows, err := configs.DB.Query(query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	// log.Println(rows)
	// 5. Scan Results
	var results []map[string]any
	for rows.Next() {
		var id, hash, name, mime, status string
		var size int64
		var createdAt time.Time // Or time.Time

		if err := rows.Scan(&id, &hash, &name, &mime, &size, &createdAt, &status); err != nil {
			log.Println(err)
			continue
		}

		results = append(results, map[string]any{
			"id":            id,
			"original_name": name,
			"mime_type":     mime,
			"size":          size,
			"created_at":    createdAt,
			"status":        status,
			// "hash": hash, // Optional: usually frontend doesn't need hash
		})
	}

	return results, nil

}
