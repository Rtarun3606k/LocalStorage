package database

import "time"

type FolderStructure struct {
	ID        string    `json:"id"`
	UserId    string    `json:"user_id"`
	ParentID  string    `json:"parent_id"`
	Name      string    `json:"name"`
	CreatedAT time.Time `json:"created_at"`
}
