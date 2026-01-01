package database

import (
	"database/sql"
	"slices"
	"storageEngine/configs"
	"time"

	"github.com/lib/pq"
)

func CreateShareLink(fileID, userID, token string, isPublic bool, emails []string, expiresAt *time.Time) (string, error) {
	query := `
        INSERT INTO share_links (file_id, created_by, token, is_public, allowed_emails, expires_at)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING token
    `
	// usage of pq.Array() converts Go slice to Postgres {a,b,c}
	var newToken string
	err := configs.DB.QueryRow(query, fileID, userID, token, isPublic, pq.Array(emails), expiresAt).Scan(&newToken)

	return newToken, err
}

func GetFileByShareToken(token string) (map[string]any, error) {
	// Added f.content_hash to the SELECT
	query := `
	SELECT f.id, f.original_name, f.mime_type, f.size_bytes, f.content_hash, s.expires_at, s.is_public,s.allowed_emails::text[]
        FROM share_links s
        JOIN file_metadata f ON s.file_id = f.id
        WHERE s.token = $1
    `
	var id, name, mime, hash string
	var size int64
	var expiresAt *time.Time
	var isPublic bool
	var allowedEmails []string

	err := configs.DB.QueryRow(query, token).Scan(&id, &name, &mime, &size, &hash, &expiresAt, &isPublic, (*pq.StringArray)(&allowedEmails))
	if err != nil {
		return nil, err
	}

	// Check Expiration
	if expiresAt != nil && time.Now().After(*expiresAt) {
		return nil, sql.ErrNoRows // Link Expired
	}

	return map[string]any{
		"file_id":        id,
		"file_name":      name,
		"mime_type":      mime,
		"content_hash":   hash, // We need this to read the disk!
		"is_public":      isPublic,
		"allowed_emails": allowedEmails,
	}, nil
}

func CheckAccess(currentEmail string, allowedEmails []string, isPublic bool) bool {

	if len(currentEmail) < 5 {
		return false
	}

	if isPublic {
		return true
	}

	if slices.Contains(allowedEmails, currentEmail) {
		return true
	}
	return false

}
