package handlers

import (
	"encoding/json"
	"log"
	"net/http"
	"runtime"
	"time"
)

// HealthStatus represents the system health status
type HealthStatus struct {
	Status    string    `json:"status"`
	Version   string    `json:"version"`
	Timestamp time.Time `json:"timestamp"`
	Uptime    string    `json:"uptime"`
	GoVersion string    `json:"go_version"`
	Memory    MemStats  `json:"memory"`
}

// MemStats contains memory statistics
type MemStats struct {
	Alloc      uint64 `json:"alloc"`
	TotalAlloc uint64 `json:"total_alloc"`
	Sys        uint64 `json:"sys"`
	NumGC      uint32 `json:"num_gc"`
}

var startTime = time.Now()

// Health handles health check requests
func Health(w http.ResponseWriter, r *http.Request) {
	log.Println("Handling health check request")

	// Get runtime memory stats
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	// Build health status response
	status := HealthStatus{
		Status:    "ok",
		Version:   "1.0.0",
		Timestamp: time.Now(),
		Uptime:    time.Since(startTime).String(),
		GoVersion: runtime.Version(),
		Memory: MemStats{
			Alloc:      m.Alloc,
			TotalAlloc: m.TotalAlloc,
			Sys:        m.Sys,
			NumGC:      m.NumGC,
		},
	}

	// Set response headers
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)

	// Encode response to JSON
	if err := json.NewEncoder(w).Encode(status); err != nil {
		log.Printf("Error encoding health status: %v", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	log.Println("Successfully served health check")
}