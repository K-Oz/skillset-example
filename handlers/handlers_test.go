package handlers

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

// setupMockServer creates a test HTTP server that returns predefined responses
func setupMockServer() *httptest.Server {
	handler := http.NewServeMux()
	
	// Mock the whatthecommit.com endpoint
	handler.HandleFunc("/index.txt", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("This is a test commit message"))
	})
	
	// Mock the randomuser.me endpoint
	handler.HandleFunc("/api/user", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"results":[{"name":{"first":"Test","last":"User"}}]}`))
	})
	
	// Mock the loripsum.net endpoint with a catch-all handler
	handler.HandleFunc("/api/lorem", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("<p>Lorem ipsum dolor sit amet.</p>"))
	})
	
	return httptest.NewServer(handler)
}

// createTransport returns an http.RoundTripper that redirects requests to the mockServer
func createTransport(mockServer *httptest.Server) http.RoundTripper {
	return roundTripperFunc(func(req *http.Request) (*http.Response, error) {
		// Replace the original URLs with the mock server URL
		url := req.URL.String()
		var newURL string

		switch {
		case strings.Contains(url, "whatthecommit.com"):
			newURL = mockServer.URL + "/index.txt"
		case strings.Contains(url, "randomuser.me"):
			newURL = mockServer.URL + "/api/user"
		case strings.Contains(url, "loripsum.net"):
			newURL = mockServer.URL + "/api/lorem"
		}
		
		newReq, err := http.NewRequestWithContext(req.Context(), req.Method, newURL, req.Body)
		if err != nil {
			return nil, err
		}
		
		// Copy headers from original request
		for k, v := range req.Header {
			newReq.Header[k] = v
		}
		
		// Use standard HTTP client to make the request to our mock server
		return http.DefaultClient.Do(newReq)
	})
}

// roundTripperFunc allows us to convert a function to a RoundTripper
type roundTripperFunc func(*http.Request) (*http.Response, error)

func (f roundTripperFunc) RoundTrip(req *http.Request) (*http.Response, error) {
	return f(req)
}

// TestCommitMessage tests the CommitMessage handler
func TestCommitMessage(t *testing.T) {
	mockServer := setupMockServer()
	defer mockServer.Close()
	
	// Create a client with our custom transport
	client := &http.Client{
		Transport: createTransport(mockServer),
	}
	
	// Save the original client creator
	originalClient := httpClientCreator
	
	// Override the client creator temporarily
	httpClientCreator = func() *http.Client {
		return client
	}
	
	// Restore the original client creator when the test is done
	defer func() {
		httpClientCreator = originalClient
	}()

	// Test the handler
	req := httptest.NewRequest("GET", "/random-commit-message", nil)
	w := httptest.NewRecorder()

	CommitMessage(w, req)

	resp := w.Result()
	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status OK; got %v", resp.StatusCode)
	}

	body, _ := io.ReadAll(resp.Body)
	if string(body) != "This is a test commit message" {
		t.Errorf("Unexpected response body: %s", string(body))
	}
}

// TestUser tests the User handler
func TestUser(t *testing.T) {
	mockServer := setupMockServer()
	defer mockServer.Close()
	
	// Create a client with our custom transport
	client := &http.Client{
		Transport: createTransport(mockServer),
	}
	
	// Save the original client creator
	originalClient := httpClientCreator
	
	// Override the client creator temporarily
	httpClientCreator = func() *http.Client {
		return client
	}
	
	// Restore the original client creator when the test is done
	defer func() {
		httpClientCreator = originalClient
	}()

	// Test the handler
	req := httptest.NewRequest("GET", "/random-user", nil)
	w := httptest.NewRecorder()

	User(w, req)

	resp := w.Result()
	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status OK; got %v", resp.StatusCode)
	}

	body, _ := io.ReadAll(resp.Body)
	if !strings.Contains(string(body), "Test") {
		t.Errorf("Expected response to contain 'Test', got: %s", string(body))
	}
}

// TestLoripsum tests the Loripsum handler
func TestLoripsum(t *testing.T) {
	mockServer := setupMockServer()
	defer mockServer.Close()
	
	// Create a client with our custom transport
	client := &http.Client{
		Transport: createTransport(mockServer),
	}
	
	// Save the original client creator
	originalClient := httpClientCreator
	
	// Override the client creator temporarily
	httpClientCreator = func() *http.Client {
		return client
	}
	
	// Restore the original client creator when the test is done
	defer func() {
		httpClientCreator = originalClient
	}()

	// Create a basic request with minimal parameters
	params := struct {
		NumberOfParagraphs int    `json:"number_of_paragraphs"`
		ParagraphLength    string `json:"paragraph_length"`
	}{
		NumberOfParagraphs: 1,
		ParagraphLength:    "short",
	}

	bodyBytes, err := json.Marshal(params)
	if err != nil {
		t.Fatalf("Failed to marshal request body: %v", err)
	}

	req := httptest.NewRequest("POST", "/random-lorem-ipsum", bytes.NewReader(bodyBytes))
	w := httptest.NewRecorder()

	Loripsum(w, req)

	resp := w.Result()
	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status OK; got %v", resp.StatusCode)
	}

	body, _ := io.ReadAll(resp.Body)
	if !strings.Contains(string(body), "Lorem ipsum") {
		t.Errorf("Expected response to contain 'Lorem ipsum', got: %s", string(body))
	}
}