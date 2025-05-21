package tests

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/github/testdatabot/handlers"
)

func TestCommitMessageHandler(t *testing.T) {
	// Create a request to pass to our handler
	req, err := http.NewRequest("GET", "/random-commit-message", nil)
	if err != nil {
		t.Fatal(err)
	}

	// Create a ResponseRecorder to record the response
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(handlers.CommitMessage)

	// Call the handler directly and pass in our request/recorder
	handler.ServeHTTP(rr, req)

	// Check the status code
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Check that the response is not empty
	if body := rr.Body.String(); body == "" {
		t.Errorf("handler returned empty body")
	}
}

func TestLoripsumHandler(t *testing.T) {
	// Create a test request body
	body := `{"number_of_paragraphs":2,"paragraph_length":"short"}`
	
	// Create a request to pass to our handler
	req, err := http.NewRequest("POST", "/random-lorem-ipsum", strings.NewReader(body))
	if err != nil {
		t.Fatal(err)
	}
	req.Header.Set("Content-Type", "application/json")

	// Create a ResponseRecorder to record the response
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(handlers.Loripsum)

	// Call the handler directly and pass in our request/recorder
	handler.ServeHTTP(rr, req)

	// Check the status code
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Check that the response contains HTML paragraphs
	if body := rr.Body.String(); !strings.Contains(body, "<p>") {
		t.Errorf("handler returned unexpected body: %v", body)
	}
}

func TestUserHandler(t *testing.T) {
	// Create a request to pass to our handler
	req, err := http.NewRequest("GET", "/random-user", nil)
	if err != nil {
		t.Fatal(err)
	}

	// Create a ResponseRecorder to record the response
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(handlers.User)

	// Call the handler directly and pass in our request/recorder
	handler.ServeHTTP(rr, req)

	// Check the status code
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Check that the response content type is application/json
	contentType := rr.Header().Get("Content-Type")
	if contentType != "application/json" {
		t.Errorf("handler returned wrong content type: got %v want %v",
			contentType, "application/json")
	}

	// Check that the response contains required fields
	if body := rr.Body.String(); !strings.Contains(body, "results") {
		t.Errorf("handler returned unexpected body: %v", body)
	}
}