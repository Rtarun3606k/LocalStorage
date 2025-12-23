package database

import (
	"fmt"
	configs "storageEngine/configs"
)

func InsertFileMetadata(userID, contentHash, originalName, mimeType string, size int64, status string) (string, error) {
	var newId string
	query := `
		INSERT INTO file_metadata (user_id, content_hash, original_name, mime_type, size_bytes,status)
		VALUES ($1, $2, $3, $4, $5,$6)
		RETURNING id
	`
	err := configs.DB.QueryRow(query, userID, contentHash, originalName, mimeType, size, status).Scan(&newId)
	if err != nil {
		return "", err
	}
	return newId, nil

}

func GetFileMetadataByID(fileID string) (map[string]any, error) {
	var err error
	query := `
		SELECT id, user_id, content_hash, original_name, mime_type, size_bytes, created_at,status
		FROM file_metadata
		WHERE id = $1
	`
	row := configs.DB.QueryRow(query, fileID)

	var id, userID, contentHash, originalName, mimeType, status string
	var sizeBytes int64
	var createdAt string

	err = row.Scan(&id, &userID, &contentHash, &originalName, &mimeType, &sizeBytes, &createdAt, &status)
	if err != nil {
		return nil, err
	}

	result := map[string]any{
		"id":            id,
		"user_id":       userID,
		"content_hash":  contentHash,
		"original_name": originalName,
		"mime_type":     mimeType,
		"size_bytes":    sizeBytes,
		"created_at":    createdAt,
		"status":        status,
	}
	fmt.Println("Retrieved metadata for file ID and user id :", fileID, result["user_id"])

	return result, nil
}

func UpdateFileMetaDataStatus(fileId string, status string) error {

	_, err := configs.DB.Exec("UPDATE file_metadata SET status = $1 WHERE id = $2", status, fileId)
	return err

}

func GetFIleMetadataByHash(contentHash string) (map[string]any, error) {
	var err error
	query := `
		SELECT id, user_id, content_hash, original_name, mime_type, size_bytes, created_at,status
		FROM file_metadata
		WHERE content_hash = $1
	`
	row := configs.DB.QueryRow(query, contentHash)

	var id, userID, contentHashDB, originalName, mimeType, status string
	var sizeBytes int64
	var createdAt string

	err = row.Scan(&id, &userID, &contentHashDB, &originalName, &mimeType, &sizeBytes, &createdAt, &status)
	if err != nil {
		return nil, err
	}

	result := map[string]any{
		"id":            id,
		"user_id":       userID,
		"content_hash":  contentHashDB,
		"original_name": originalName,
		"mime_type":     mimeType,
		"size_bytes":    sizeBytes,
		"created_at":    createdAt,
		"status":        status,
	}
	fmt.Println("Retrieved metadata for content hash :", contentHash, result["id"])

	return result, nil
}
