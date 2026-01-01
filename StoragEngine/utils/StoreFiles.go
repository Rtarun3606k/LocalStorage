package utils

import (
	"crypto/sha256"
	"encoding/hex"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"storageEngine/configs"
	"storageEngine/database"
)

func StoreFiles(file multipart.File, header *multipart.FileHeader, userId string) (string, error) {
	// 1. EARLY VALIDATION: Check MimeType BEFORE doing anything expensive
	mimeType := header.Header.Get("Content-Type")
	// Make sure your AllowedTypes map uses lowercase keys if you normalize.
	if !configs.AllowedTypes[mimeType] {
		// Optional: Allow "application/octet-stream" if you want to allow generic uploads
		return "", http.ErrNotSupported
	}

	// 2. Create Temp File
	tempFile, err := os.CreateTemp("", "upload-*.tmp")
	if err != nil {
		return "", err
	}
	defer os.Remove(tempFile.Name())

	// 3. Hash & Write
	hasher := sha256.New()
	multiWriter := io.MultiWriter(tempFile, hasher)

	if _, err := io.Copy(multiWriter, file); err != nil {
		return "", err
	}
	tempFile.Close()

	// 4. Final Hash
	fileHash := hex.EncodeToString(hasher.Sum(nil))

	// 5. Deduplication Check

	// Detect if Video (We need this logic for both New and Duplicate files)
	// 5. Deduplication Check
	checkExistingFile, err := database.GetFIleMetadataByHash(fileHash)

	// Detect if Video
	isVideo := strings.HasPrefix(mimeType, "video/") || strings.Contains(mimeType, "video")

	if err == nil && checkExistingFile != nil {
		// --- DUPLICATE FOUND ---

		// FIX: Don't blindly set "Processing".
		// Instead, grab the status from the OLD file.
		status := configs.StatusReady // Default

		// Check if the DB map actually has the "status" key
		if val, ok := checkExistingFile["status"]; ok {
			status = val.(string)
		}

		// Only if the old file is somehow MISSING a status, we might force one.
		// But usually, if the old file is "ready", newId becomes "ready" instantly.

		newId, err := database.InsertFileMetadata(
			userId,
			fileHash,
			header.Filename,
			mimeType,
			header.Size,
			status, // <--- Use the COPIED status
		)

		if err != nil {
			return "", err
		}
		// If status is "ready", the user gets the link instantly.
		// If status is "processing" (rare, means 1st upload is still running),
		// the user sees "processing" too.

		return newId, nil
	}

	// 6. Move to Permanent Storage
	targetDir := filepath.Join(configs.UploadDir, fileHash[:2], fileHash[2:4], fileHash)
	if err := os.MkdirAll(targetDir, 0755); err != nil {
		return "", err
	}

	ext := filepath.Ext(header.Filename)
	targetPath := filepath.Join(targetDir, "original"+ext)

	if err := os.Rename(tempFile.Name(), targetPath); err != nil {
		return "", err
	}

	// 7. Insert Metadata (New File)
	var status string
	if isVideo {
		status = configs.StatusProcessing
	} else {
		status = configs.StatusReady
	}

	newFileId, err := database.InsertFileMetadata(userId, fileHash, header.Filename, mimeType, header.Size, status)
	if err != nil {
		return "", err
	}

	// 8. Queue Video Job (If Video)
	if isVideo {
		// Make sure VideoQueue is accessible here!
		configs.VideoQueue <- configs.VideoJob{
			FileId:     newFileId,
			SourcePath: targetPath, // Pass full path to file, not just dir
			OutputDir:  targetDir,
		}
	}

	return newFileId, nil
}

func SanitizeFilename(filename string) string {

	name := filepath.Base(filename)

	newName := configs.SafeRegex.ReplaceAllString(name, "-")

	if len(newName) > 200 {
		newName = newName[:200]
	}

	if newName == " " || newName == "." {
		newName = "renamed_file"
	}

	return newName

}
