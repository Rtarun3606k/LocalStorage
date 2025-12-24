package utils

import (
	"crypto/sha256"
	"encoding/hex"
	"io"
	"mime/multipart"
	"os"
	"path/filepath"
	"storageEngine/configs"
	"storageEngine/database"
)

func StoreFiles(file multipart.File, header *multipart.FileHeader, userId string) (string, error) {
	//cresate a temp file
	tempFile, err := os.CreateTemp("", "upload-*.tmp")
	if err != nil {
		return "", err
	}
	defer os.Remove(tempFile.Name())

	//hash
	hasher := sha256.New()
	multiWriter := io.MultiWriter(tempFile, hasher)

	//stream the file
	if _, err := io.Copy(multiWriter, file); err != nil {
		return "", err
	}

	tempFile.Close()

	//final hash
	fileHash := hex.EncodeToString(hasher.Sum(nil))

	//check for existing StoreFiles
	checkExistingFile, err := database.GetFIleMetadataByHash(fileHash)

	if err == nil && checkExistingFile != nil {
		// --- DUPLICATE FOUND: SHARE STORAGE ---
		// Create a NEW ID, but point to EXISTING Hash
		newId, err := database.InsertFileMetadata(
			userId,
			fileHash,
			header.Filename,
			header.Header.Get("Content-Type"),
			header.Size,
			configs.StatusReady,
		)
		if err != nil {
			return "", err
		}
		return newId, nil
	}

	//rename the file to content hash
	ext := filepath.Ext(header.Filename)
	
	targetDir := filepath.Join(configs.UploadDir, fileHash[:2], fileHash[2:4], fileHash)
	if err := os.MkdirAll(targetDir, 0755); err != nil {
		return "", err
	}
	targetPath := filepath.Join(targetDir, "original"+ext)

	//move the file
	if err := os.Rename(tempFile.Name(), targetPath); err != nil {
		return "", err
	}

	//insert metadata
	newFileId, err := database.InsertFileMetadata(userId, fileHash, header.Filename, header.Header.Get("Content-Type"), header.Size, configs.StatusReady)
	if err != nil {
		return "", err
	}

	return newFileId, nil

}
