package configs

import (
	"database/sql"
	_ "github.com/lib/pq"
	"log"
)

var DB *sql.DB

func ConnectToDatabase() error {
	// Implement database connection logic here
	connectStr := "postgresql://postgres:1234@localhost:5432/localstoragedb?sslmode=disable"
	var err error
	DB, err = sql.Open("postgres", connectStr)
	if err != nil {
		log.Fatal("Failed to connect to database: ", err)
		return err
	}
	if err = DB.Ping(); err != nil {
		log.Fatal("Database ping failed: ", err)
		return err
	}
	log.Println("Successfully connected to the database")
	return nil
}
