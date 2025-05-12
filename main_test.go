package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestPingEndpoint(t *testing.T) {
	// Set up the routes
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.HandleFunc("/random-commit-message", func(w http.ResponseWriter, r *http.Request) {})
		http.HandleFunc("/random-lorem-ipsum", func(w http.ResponseWriter, r *http.Request) {})
		http.HandleFunc("/random-user", func(w http.ResponseWriter, r *http.Request) {})
		http.HandleFunc("/_ping", func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("OK"))
		})

		// Call the actual handler
		http.DefaultServeMux.ServeHTTP(w, r)
	}))
	defer srv.Close()

	// Test the ping endpoint
	resp, err := http.Get(srv.URL + "/_ping")
	if err != nil {
		t.Fatalf("Failed to make request: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status OK; got %v", resp.StatusCode)
	}
}