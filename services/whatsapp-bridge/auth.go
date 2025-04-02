package main

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

// contextKey is a private type for context keys
type contextKey string

// userIDKey is the key for user ID value in the request context
const userIDKey contextKey = "userID"

// WithUserID returns a new context with the given user ID
func WithUserID(ctx context.Context, userID string) context.Context {
	return context.WithValue(ctx, userIDKey, userID)
}

// GetUserIDFromContext extracts the user ID from the context
func GetUserIDFromContext(ctx context.Context) string {
	userID, ok := ctx.Value(userIDKey).(string)
	if !ok {
		return ""
	}
	return userID
}

type SupabaseResponse struct {
	Data []map[string]interface{} `json:"data"`
}

// AuthMiddleware checks if the request is authenticated and returns the user ID.
// It supports both Bearer token and VEYRAX API key authentication methods.
func AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Check for VEYRAX_API_KEY in headers
		apiKey := r.Header.Get("VEYRAX_API_KEY")
		if apiKey != "" {
			// Validate API key against Supabase
			userID, err := validateAPIKey(apiKey)
			if err != nil {
				http.Error(w, fmt.Sprintf("Invalid API key: %v", err), http.StatusUnauthorized)
				return
			}

			// Set the userID in the request context
			ctx := r.Context()
			ctx = WithUserID(ctx, userID)
			next.ServeHTTP(w, r.WithContext(ctx))
			return
		}

		// Check for Bearer token
		authHeader := r.Header.Get("Authorization")
		if authHeader != "" && strings.HasPrefix(authHeader, "Bearer ") {
			token := strings.TrimPrefix(authHeader, "Bearer ")
			userID, err := extractUserIDFromToken(token)
			if err != nil {
				http.Error(w, fmt.Sprintf("Invalid token: %v", err), http.StatusUnauthorized)
				return
			}

			// Set the userID in the request context
			ctx := r.Context()
			ctx = WithUserID(ctx, userID)
			next.ServeHTTP(w, r.WithContext(ctx))
			return
		}

		// No authentication provided
		http.Error(w, "Missing or invalid authentication. Use 'Bearer <token>' or provide 'VEYRAX_API_KEY' header", http.StatusUnauthorized)
	})
}

// validateAPIKey checks if the API key is valid by querying the Supabase users_api_keys table
func validateAPIKey(apiKey string) (string, error) {
	supabaseURL := os.Getenv("SUPABASE_URL")
	supabaseServiceKey := os.Getenv("SUPABASE_SERVICE_KEY")

	if supabaseURL == "" || supabaseServiceKey == "" {
		return "", fmt.Errorf("missing Supabase credentials")
	}

	// Create API request
	url := fmt.Sprintf("%s/rest/v1/users_api_keys?select=user_id&api_key=eq.%s", supabaseURL, apiKey)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", fmt.Errorf("failed to create request: %v", err)
	}

	// Add Supabase headers
	req.Header.Add("apikey", supabaseServiceKey)
	req.Header.Add("Authorization", "Bearer "+supabaseServiceKey)
	req.Header.Add("Content-Type", "application/json")

	// Send request
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("failed to send request: %v", err)
	}
	defer resp.Body.Close()

	// Read response
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response: %v", err)
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("Supabase returned non-OK status: %d - %s", resp.StatusCode, string(body))
	}

	// Parse response
	var response SupabaseResponse
	if err := json.Unmarshal(body, &response.Data); err != nil {
		return "", fmt.Errorf("failed to parse response: %v", err)
	}

	if len(response.Data) == 0 {
		return "", fmt.Errorf("invalid API key")
	}

	userID, ok := response.Data[0]["user_id"].(string)
	if !ok {
		return "", fmt.Errorf("invalid user ID format")
	}

	return userID, nil
}

// extractUserIDFromToken extracts the user ID from a JWT token
func extractUserIDFromToken(token string) (string, error) {
	// Split token into parts
	parts := strings.Split(token, ".")
	if len(parts) != 3 {
		return "", fmt.Errorf("invalid token format")
	}

	// Decode payload
	payload := parts[1]
	// Ensure padding
	if len(payload)%4 != 0 {
		payload += strings.Repeat("=", 4-len(payload)%4)
	}

	decodedBytes, err := base64.URLEncoding.DecodeString(payload)
	if err != nil {
		return "", fmt.Errorf("failed to decode token payload: %v", err)
	}

	// Parse JSON payload
	var userData map[string]interface{}
	if err := json.Unmarshal(decodedBytes, &userData); err != nil {
		return "", fmt.Errorf("failed to parse token payload: %v", err)
	}

	// Extract user ID from the "sub" field
	userID, ok := userData["sub"].(string)
	if !ok {
		return "", fmt.Errorf("missing or invalid 'sub' field in token")
	}

	return userID, nil
}

// ValidateUserMatch checks if the authenticated user matches the user_id in the request
func ValidateUserMatch(r *http.Request, requestUserID string) error {
	authenticatedUserID := GetUserIDFromContext(r.Context())
	if authenticatedUserID == "" {
		return fmt.Errorf("no authenticated user found in context")
	}

	if authenticatedUserID != requestUserID {
		return fmt.Errorf("authenticated user (%s) does not match requested user (%s)", authenticatedUserID, requestUserID)
	}

	return nil
}

// ApplyAuthMiddleware wraps the REST API handlers with the auth middleware
func ApplyAuthMiddleware(mux *http.ServeMux) http.Handler {
	return AuthMiddleware(mux)
}

// CheckAuth is a handler function that checks if a user is authenticated
func CheckAuth(w http.ResponseWriter, r *http.Request) {
	userID := GetUserIDFromContext(r.Context())
	if userID == "" {
		http.Error(w, "Not authenticated", http.StatusUnauthorized)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(fmt.Sprintf(`{"authenticated": true, "user_id": "%s"}`, userID)))
}

// GetRequestBody reads and returns the request body while preserving it for future reads
func GetRequestBody(r *http.Request) ([]byte, error) {
	if r.Body == nil {
		return nil, fmt.Errorf("request body is empty")
	}

	// Read the body
	body, err := io.ReadAll(r.Body)
	if err != nil {
		return nil, err
	}

	// Replace the body with a new io.ReadCloser to allow multiple reads
	r.Body = io.NopCloser(bytes.NewBuffer(body))

	return body, nil
}
