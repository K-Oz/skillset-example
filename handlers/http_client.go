package handlers

import (
	"net/http"
)

// httpClientCreator is a function that creates an HTTP client
// It can be overridden in tests to provide a mock client
var httpClientCreator = func() *http.Client {
	return &http.Client{}
}