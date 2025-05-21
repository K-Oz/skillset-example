package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"path"
	"time"
)

type LoripsumParams struct {
	NumberOfParagraphs int    `json:"number_of_paragraphs"`
	ParagraphLength    string `json:"paragraph_length"`
	Decorate           bool   `json:"decorate"`
	Link               bool   `json:"link"`
	UnorderedLists     bool   `json:"unordered_lists"`
	NumberedLists      bool   `json:"numbered_lists"`
	DescriptionLists   bool   `json:"description_lists"`
	Blockquotes        bool   `json:"blockquotes"`
	Code               bool   `json:"code"`
	Headers            bool   `json:"headers"`
	AllCaps            bool   `json:"all_caps"`
	Prude              bool   `json:"prude"`
}

func Loripsum(w http.ResponseWriter, r *http.Request) {
	log.Println("Handling request for random lorem ipsum")

	// Check method
	if r.Method != http.MethodPost && r.Method != http.MethodOptions {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Handle CORS preflight
	if r.Method == http.MethodOptions {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		w.WriteHeader(http.StatusOK)
		return
	}

	// Parse request body
	params := &LoripsumParams{}
	if err := json.NewDecoder(r.Body).Decode(params); err != nil {
		log.Printf("Error decoding request body: %v", err)
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Construct API URL
	p := "api"
	if params.NumberOfParagraphs != 0 {
		if params.NumberOfParagraphs < 0 {
			p = path.Join(p, "1")
		} else if params.NumberOfParagraphs > 10 {
			p = path.Join(p, "10")
		} else {
			p = path.Join(p, fmt.Sprintf("%v", params.NumberOfParagraphs))
		}
	}

	if params.ParagraphLength == "short" || params.ParagraphLength == "medium" || params.ParagraphLength == "long" || params.ParagraphLength == "verylong" {
		p = path.Join(p, params.ParagraphLength)
	}

	if params.Decorate {
		p = path.Join(p, "decorate")
	}

	if params.Link {
		p = path.Join(p, "link")
	}

	if params.UnorderedLists {
		p = path.Join(p, "ul")
	}

	if params.NumberedLists {
		p = path.Join(p, "ol")
	}

	if params.DescriptionLists {
		p = path.Join(p, "dl")
	}

	if params.Blockquotes {
		p = path.Join(p, "bq")
	}

	if params.Code {
		p = path.Join(p, "code")
	}

	if params.Headers {
		p = path.Join(p, "headers")
	}

	if params.AllCaps {
		p = path.Join(p, "allcaps")
	}

	if params.Prude {
		p = path.Join(p, "prude")
	}

	u, _ := url.Parse("https://loripsum.net")
	u.Path = p

	// Set up context with timeout
	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()

	// Create request
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, u.String(), nil)
	if err != nil {
		log.Printf("Error creating request: %v", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	// Send request
	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Error fetching lorem ipsum: %v", err)
		http.Error(w, "Error fetching lorem ipsum", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	// Check response status
	if resp.StatusCode != http.StatusOK {
		log.Printf("API returned non-200 status: %d", resp.StatusCode)
		http.Error(w, "Upstream API error", http.StatusInternalServerError)
		return
	}

	// Set headers
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	// Copy response body to client
	if _, err := io.Copy(w, resp.Body); err != nil {
		log.Printf("Error copying response: %v", err)
		// Cannot write error to client at this point
		return
	}

	log.Println("Successfully served random lorem ipsum")
}