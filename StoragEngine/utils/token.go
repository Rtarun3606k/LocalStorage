package utils

import (
	"crypto/rand"
	"encoding/base64"
)

func GenerateRandomToken() (string, error) {

	randomNumber := make([]byte, 12)
	_, err := rand.Read(randomNumber)
	if err != nil {
		return "", err
	}

	result := base64.URLEncoding.EncodeToString(randomNumber)
	return result, nil

}
