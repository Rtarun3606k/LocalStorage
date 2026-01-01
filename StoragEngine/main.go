package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	// IMP: You MUST use Gorilla Mux for {id} variables to work
	"github.com/gorilla/mux"

	config "storageEngine/configs"
	route "storageEngine/routes"
	"storageEngine/workers"
)

// CORS Middleware: Adds headers to every response so the browser accepts it
func enableCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 1. Set Headers
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		// 2. Handle Preflight Browser Requests
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		// 3. Continue to the Handler
		next.ServeHTTP(w, r)
	})
}

func main() {
	// 1. Database & Config Setup
	if err := config.ConnectToDatabase(); err != nil {
		log.Fatal("DB Error:", err)
	}
	if err := os.MkdirAll(config.UploadDir, 0755); err != nil {
		log.Fatal("Upload Dir Error:", err)
	}

	// 2. Start Background Workers
	for i := 0; i < config.NumVideoWorkers; i++ {
		go workers.StartVideoWorker(i)
	}

	// 3. Router Setup (Using Gorilla Mux)
	r := mux.NewRouter()
	// r.HandleFunc("/s/{token}", route.).Methods("GET")

	// Create API v1 subrouter
	v1 := r.PathPrefix("/api/v1").Subrouter()

	// Register Routes
	v1.HandleFunc("/image/upload", route.UploadHandler).Methods("POST")
	v1.HandleFunc("/image/download", route.DownloadHandler).Methods("GET")

	// Video Routes
	v1.HandleFunc("/video/upload", route.VideoUploadHandler).Methods("POST")
	// THIS LINE requires Gorilla Mux to parse {id} and {filename}
	v1.HandleFunc("/video/{id}/{filename}", route.VideoDownloadHandler).Methods("GET")

	// Universal File Routes
	v1.HandleFunc("/upload", route.OtherUploadHandler).Methods("POST")
	v1.HandleFunc("/download/{id}", route.FileDownloadHandler).Methods("GET")
	v1.HandleFunc("/rename/{id}", route.Remane).Methods("PATCH")
	v1.HandleFunc("/delete/{id}", route.DeleteUniversalHandler).Methods("DELETE")
	v1.HandleFunc("/search", route.SearchFileshandler).Methods("GET")
	v1.HandleFunc("/folders", route.CreateoFolderHandler).Methods("POST")
	v1.HandleFunc("/file/move/{id}", route.MoveFileHandler).Methods("PATCH")
	v1.HandleFunc("/folder/rename/{id}", route.RenameFolderHandler).Methods("PATCH")
	v1.HandleFunc("/folder/delete/{id}", route.DeleteFolderHandler).Methods("DELETE")
	// Create Share Link
	v1.HandleFunc("/file/share/{id}", route.CreateShareLinkHandler).Methods("POST")
	//	 Start Message
	fmt.Println("Storage Engine v1.0.0 is running on :8080")

	// 4. Start Server with CORS Middleware
	// We wrap the router 'r' with enableCORS
	if err := http.ListenAndServe(":8080", enableCORS(r)); err != nil {
		log.Fatal(err)
	}
}
