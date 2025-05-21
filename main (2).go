package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/github/testdatabot/handlers"
)

func main() {
	if err := run(); err != nil {
		log.Printf("Error: %v", err)
		os.Exit(1)
	}
}

func run() error {
	// Set up logging
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	log.Println("Starting TestDataBot API server...")

	// Register routes
	mux := http.NewServeMux()
	mux.HandleFunc("/random-commit-message", handlers.CommitMessage)
	mux.HandleFunc("/random-lorem-ipsum", handlers.Loripsum)
	mux.HandleFunc("/random-user", handlers.User)
	mux.HandleFunc("/_ping", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("OK"))
	})

	// Configure the HTTP server
	port := getEnvOrDefault("PORT", "8080")
	server := &http.Server{
		Addr:         ":" + port,
		Handler:      mux,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Start the server
	log.Printf("Server listening on port %s", port)
	if err := server.ListenAndServe(); err != http.ErrServerClosed {
		return fmt.Errorf("server error: %w", err)
	}

	return nil
}

// getEnvOrDefault gets an environment variable or returns a default value
func getEnvOrDefault(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}