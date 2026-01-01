package database

import (
	"fmt"
	"storageEngine/configs"
)

func CreateFolder(userID string, name string, parentID *string) (string, error) {
	var newID string

	// Logic: Insert a folder. parentID can be null (root) or a UUID (nested).
	query := `
        INSERT INTO folders (user_id, name, parent_id)
        VALUES ($1, $2, $3)
        RETURNING id
    `

	// We pass 'parentID' directly. The driver handles the nil pointer => NULL conversion.
	err := configs.DB.QueryRow(query, userID, name, parentID).Scan(&newID)
	if err != nil {
		return "", err
	}

	return newID, nil
}

// MoveFile updates the folder_id.
// Pass targetFolderID as nil to move to Root.
func MoveFile(fileID string, userID string, targetFolderID *string) error {
	query := `
        UPDATE file_metadata 
        SET folder_id = $1 
        WHERE id = $2 AND user_id = $3
    `
	// If targetFolderID is nil, Postgres sets the column to NULL (Root)
	result, err := configs.DB.Exec(query, targetFolderID, fileID, userID)
	if err != nil {
		return err
	}

	rowsAffected, _ := result.RowsAffected()
	if rowsAffected == 0 {
		return fmt.Errorf("file not found or access denied")
	}

	return nil
}

// --- RENAME FOLDER ---
func RenameFolder(folderID string, userID string, newName string) error {
	query := `
        UPDATE folders 
        SET name = $1 
        WHERE id = $2 AND user_id = $3
    `
	result, err := configs.DB.Exec(query, newName, folderID, userID)
	if err != nil {
		return err
	}

	rows, _ := result.RowsAffected()
	if rows == 0 {
		return fmt.Errorf("folder not found or access denied")
	}
	return nil
}

// --- DELETE FOLDER ---
func DeleteFolder(folderID string, userID string) error {
	// Note: Due to your Schema:
	// 1. Files inside will have folder_id set to NULL (Move to Root)
	// 2. Sub-folders inside will be DELETED (Cascade)
	query := `
        DELETE FROM folders 
        WHERE id = $1 AND user_id = $2
    `
	result, err := configs.DB.Exec(query, folderID, userID)
	if err != nil {
		return err
	}

	rows, _ := result.RowsAffected()
	if rows == 0 {
		return fmt.Errorf("folder not found or access denied")
	}
	return nil
}
