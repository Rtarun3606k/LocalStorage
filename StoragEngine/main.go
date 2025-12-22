package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"storageEngine/configs"
	config "storageEngine/configs"
	imageRoute "storageEngine/routes"
)

func main() { // Entry point for the Storage Engine application

	if err := configs.ConnectToDatabase(); err != nil {
		log.Fatal("Could not connect to database:", err)
	}
	if err := os.MkdirAll(config.UploadDir, 0755); err != nil {
		log.Fatal(err)
		panic("Failed to create upload directory: " + err.Error())
	}
	log.Printf("%s v%s started. Upload directory: %s", config.AppName, config.AppVersion, config.UploadDir)

	v1Mux := http.NewServeMux()
	// Register v1 routes
	v1Mux.HandleFunc("/upload", imageRoute.UploadHandler)
	v1Mux.HandleFunc("/download", imageRoute.DownloadHandler)
	// v1Mux.HandleFunc("/download", downloadHandler)

	http.Handle("/api/v1/", http.StripPrefix("/api/v1", v1Mux))
	fmt.Println("Starting server on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal("Server failed to start: ", err)
	}
}
