package handlers

import (
	"encoding/json"
	"log"
	"net/http"
)

// ErrorResponse represents an error response
type ErrorResponse struct {
	Error   string `json:"error"`
	Message string `json:"message,omitempty"`
	Code    int    `json:"code"`
}

// RespondWithError sends a JSON error response
func RespondWithError(w http.ResponseWriter, message string, code int) {
	log.Printf("Error response: %s (code: %d)", message, code)
	
	response := ErrorResponse{
		Error:   http.StatusText(code),
		Message: message,
		Code:    code,
	}
	
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	
	if err := json.NewEncoder(w).Encode(response); err != nil {
		log.Printf("Error encoding error response: %v", err)
		// If we can't encode the error, fall back to plain text
		w.Header().Set("Content-Type", "text/plain")
		w.Write([]byte(message))
	}
}

// RespondWithJSON sends a JSON response
func RespondWithJSON(w http.ResponseWriter, data interface{}, code int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	
	if err := json.NewEncoder(w).Encode(data); err != nil {
		log.Printf("Error encoding JSON response: %v", err)
		RespondWithError(w, "Internal server error", http.StatusInternalServerError)
		return
	}
}