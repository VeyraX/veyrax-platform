package main

import (
	"bytes"
	"context"
	"database/sql"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"reflect"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/mdp/qrterminal"

	"go.mau.fi/whatsmeow"
	waProto "go.mau.fi/whatsmeow/binary/proto"
	"go.mau.fi/whatsmeow/store/sqlstore"
	"go.mau.fi/whatsmeow/types"
	"go.mau.fi/whatsmeow/types/events"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/protobuf/proto"
)

// Global client manager to store active WhatsApp clients
var (
	clients      = make(map[string]*ClientInfo)
	clientsMutex sync.RWMutex

	// Add tracking for active QR sessions
	qrSessions      = make(map[string]*QRSession)
	qrSessionsMutex sync.RWMutex

	// Track active authentication processes
	authProcesses      = make(map[string]bool)
	authProcessesMutex sync.Mutex
)

// QRSession tracks an active WhatsApp authentication session
type QRSession struct {
	QRCode        string
	QRImageBase64 string
	ExpiresAt     time.Time
	Client        *whatsmeow.Client
}

// Message represents a chat message for our client
type Message struct {
	Time     time.Time
	Sender   string
	Content  string
	IsFromMe bool
}

// Database handler for storing message history
type MessageStore struct {
	db *sql.DB
}

// ClientInfo contains client-specific data
type ClientInfo struct {
	Client       *whatsmeow.Client
	Logger       waLog.Logger
	MessageStore *MessageStore
	UserID       string
}

// Initialize message store for a specific user
func NewMessageStore(userID string) (*MessageStore, error) {
	// Use the new user-specific directory structure
	dbPath := getUserDBPath(userID)
	log.Printf("Creating message store with DB path: %s", dbPath)

	// Create directory if it doesn't exist (handled in getUserDBPath)

	// Open the database
	db, err := sql.Open("sqlite3", fmt.Sprintf("file:%s?_foreign_keys=on", dbPath))
	if err != nil {
		log.Printf("Error opening database at %s: %v", dbPath, err)
		return nil, fmt.Errorf("error opening database: %w", err)
	}

	// Verify connection is working
	if err := db.Ping(); err != nil {
		log.Printf("Error pinging database at %s: %v", dbPath, err)
		db.Close()
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	log.Printf("Successfully connected to database at %s", dbPath)

	// Create tables if they don't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS chats (
			jid TEXT PRIMARY KEY,
			name TEXT,
			last_message_time TIMESTAMP
		);
		
		CREATE TABLE IF NOT EXISTS messages (
			id TEXT,
			chat_jid TEXT,
			sender TEXT,
			content TEXT,
			timestamp TIMESTAMP,
			is_from_me BOOLEAN,
			PRIMARY KEY (id, chat_jid),
			FOREIGN KEY (chat_jid) REFERENCES chats(jid)
		);
	`)
	if err != nil {
		log.Printf("Error creating tables in database at %s: %v", dbPath, err)
		db.Close()
		return nil, fmt.Errorf("failed to create tables: %v", err)
	}

	log.Printf("Successfully created tables in database at %s", dbPath)
	return &MessageStore{db: db}, nil
}

// Close the database connection
func (store *MessageStore) Close() error {
	return store.db.Close()
}

// Store a chat in the database
func (store *MessageStore) StoreChat(jid, name string, lastMessageTime time.Time) error {
	_, err := store.db.Exec(
		"INSERT OR REPLACE INTO chats (jid, name, last_message_time) VALUES (?, ?, ?)",
		jid, name, lastMessageTime,
	)
	return err
}

// Store a message in the database
func (store *MessageStore) StoreMessage(id, chatJID, sender, content string, timestamp time.Time, isFromMe bool) error {
	// Only store if there's actual content
	if content == "" {
		return nil
	}

	// First check if the message already exists
	var count int
	err := store.db.QueryRow("SELECT COUNT(*) FROM messages WHERE id = ? AND chat_jid = ?", id, chatJID).Scan(&count)
	if err != nil {
		return fmt.Errorf("failed to check message existence: %v", err)
	}

	// If message already exists, don't insert again
	if count > 0 {
		return nil
	}

	_, err = store.db.Exec(
		"INSERT OR REPLACE INTO messages (id, chat_jid, sender, content, timestamp, is_from_me) VALUES (?, ?, ?, ?, ?, ?)",
		id, chatJID, sender, content, timestamp, isFromMe,
	)
	return err
}

// Get messages from a chat
func (store *MessageStore) GetMessages(chatJID string, limit int) ([]Message, error) {
	rows, err := store.db.Query(
		"SELECT sender, content, timestamp, is_from_me FROM messages WHERE chat_jid = ? ORDER BY timestamp DESC LIMIT ?",
		chatJID, limit,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var messages []Message
	for rows.Next() {
		var msg Message
		var timestamp time.Time
		err := rows.Scan(&msg.Sender, &msg.Content, &timestamp, &msg.IsFromMe)
		if err != nil {
			return nil, err
		}
		msg.Time = timestamp
		messages = append(messages, msg)
	}

	return messages, nil
}

// Get all chats
func (store *MessageStore) GetChats() (map[string]time.Time, error) {
	rows, err := store.db.Query("SELECT jid, last_message_time FROM chats ORDER BY last_message_time DESC")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	chats := make(map[string]time.Time)
	for rows.Next() {
		var jid string
		var lastMessageTime time.Time
		err := rows.Scan(&jid, &lastMessageTime)
		if err != nil {
			return nil, err
		}
		chats[jid] = lastMessageTime
	}

	return chats, nil
}

// Extract text content from a message
func extractTextContent(msg *waProto.Message) string {
	if msg == nil {
		return ""
	}

	// Try to get text content
	if text := msg.GetConversation(); text != "" {
		return text
	} else if extendedText := msg.GetExtendedTextMessage(); extendedText != nil {
		return extendedText.GetText()
	}

	// For now, we're ignoring non-text messages
	return ""
}

// Response types for API endpoints
type SendMessageResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

type SendMessageRequest struct {
	UserID    string `json:"user_id"`
	Recipient string `json:"recipient"`
	Message   string `json:"message"`
}

type AuthRequest struct {
	UserID string `json:"user_id"`
}

type AuthResponse struct {
	QRString      string `json:"qr_string,omitempty"`
	QRImageBase64 string `json:"qr_image_base64,omitempty"`
	Message       string `json:"message"`
	Success       bool   `json:"success"`
	IsLoggedIn    bool   `json:"is_logged_in"`
}

// New response types for messages and chats
type MessageResponse struct {
	ID        string `json:"id"`
	Timestamp string `json:"timestamp"`
	Sender    string `json:"sender"`
	Content   string `json:"content"`
	IsFromMe  bool   `json:"is_from_me"`
	ChatJID   string `json:"chat_jid"`
	ChatName  string `json:"chat_name,omitempty"`
}

type ChatResponse struct {
	JID             string `json:"jid"`
	Name            string `json:"name,omitempty"`
	LastMessageTime string `json:"last_message_time,omitempty"`
	LastMessage     string `json:"last_message,omitempty"`
	LastSender      string `json:"last_sender,omitempty"`
	LastIsFromMe    bool   `json:"last_is_from_me,omitempty"`
	IsGroup         bool   `json:"is_group"`
}

type ContactResponse struct {
	PhoneNumber string `json:"phone_number"`
	Name        string `json:"name,omitempty"`
	JID         string `json:"jid"`
}

type MessagesListResponse struct {
	Items []MessageResponse `json:"items"`
}

type ChatsListResponse struct {
	Items []ChatResponse `json:"items"`
}

type ContactsListResponse struct {
	Items []ContactResponse `json:"items"`
}

// DisconnectResponse represents the response for the disconnect endpoint
type DisconnectResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

// DisconnectRequest represents the request for the disconnect endpoint
type DisconnectRequest struct {
	UserID string `json:"user_id"`
}

// Function to send a WhatsApp message
func sendWhatsAppMessage(client *whatsmeow.Client, recipient string, message string) (bool, string) {
	if client == nil || !client.IsConnected() {
		return false, "Not connected to WhatsApp"
	}

	// Create JID for recipient
	var recipientJID types.JID
	var err error

	// Check if recipient is a JID
	isJID := strings.Contains(recipient, "@")

	if isJID {
		// Parse the JID string
		recipientJID, err = types.ParseJID(recipient)
		if err != nil {
			return false, fmt.Sprintf("Error parsing JID: %v", err)
		}
	} else {
		// Create JID from phone number
		recipientJID = types.JID{
			User:   recipient,
			Server: "s.whatsapp.net", // For personal chats
		}
	}

	// Send the message
	msgInfo, err := client.SendMessage(context.Background(), recipientJID, &waProto.Message{
		Conversation: proto.String(message),
	})

	if err != nil {
		return false, fmt.Sprintf("Error sending message: %v", err)
	}

	// Since we already have the client passed as a parameter,
	// we need to find which clientInfo it corresponds to
	// We'll iterate through all clients to find the matching one
	clientsMutex.RLock()
	var foundClientInfo *ClientInfo

	// Need to find the client in our map to get access to the message store
	for _, clientInfo := range clients {
		if clientInfo.Client == client {
			foundClientInfo = clientInfo
			break
		}
	}
	clientsMutex.RUnlock()

	if foundClientInfo != nil && foundClientInfo.MessageStore != nil {
		// Get chat JID as string
		chatJID := recipientJID.String()

		// Get sender from the phone number in the WhatsApp client
		var sender string
		if client.Store != nil && client.Store.ID != nil {
			sender = client.Store.ID.User
		} else {
			sender = foundClientInfo.UserID
		}

		log.Printf("Storing outgoing message from user %s (UUID: %s) to %s",
			sender, foundClientInfo.UserID, chatJID)

		// Get appropriate chat name
		name := GetChatName(foundClientInfo, recipientJID, chatJID, nil, "")

		// Update chat in database with the current timestamp
		timestamp := time.Now()
		err := foundClientInfo.MessageStore.StoreChat(chatJID, name, timestamp)
		if err != nil {
			log.Printf("Failed to store chat for outgoing message: %v", err)
		}

		// Store the message in database
		err = foundClientInfo.MessageStore.StoreMessage(
			msgInfo.ID, // Message ID from WhatsApp
			chatJID,    // Chat JID
			sender,     // Sender is the current user's phone number
			message,    // Message content
			timestamp,  // Current time
			true,       // IsFromMe = true for outgoing messages
		)
		if err != nil {
			log.Printf("Failed to store outgoing message: %v", err)
		} else {
			log.Printf("Stored outgoing message from %s to %s: %s",
				foundClientInfo.UserID, chatJID, message)
		}
	} else {
		log.Printf("Could not find matching client info for storing outgoing message")
	}

	return true, fmt.Sprintf("Message sent to %s", recipient)
}

// Get the database path for a specific user, creating directories if needed
func getUserDBPath(userID string) string {
	// First ensure the main store directory exists
	storeDir := "store"
	if _, err := os.Stat(storeDir); os.IsNotExist(err) {
		log.Printf("Creating main store directory: %s", storeDir)
		if err := os.MkdirAll(storeDir, 0755); err != nil {
			log.Printf("Error creating main store directory: %v", err)
		}
	}

	// Create user-specific directory
	userDir := fmt.Sprintf("%s/%s", storeDir, userID)
	if _, err := os.Stat(userDir); os.IsNotExist(err) {
		log.Printf("Creating user directory: %s", userDir)
		if err := os.MkdirAll(userDir, 0755); err != nil {
			log.Printf("Error creating user directory for %s: %v", userID, err)
		}
	}

	dbPath := fmt.Sprintf("%s/messages.db", userDir)
	log.Printf("Database path for user %s: %s", userID, dbPath)
	return dbPath
}

// Load or create a new WhatsApp client for a user
func loadClientForUser(userID string) (*ClientInfo, error, bool) {
	log.Printf("Loading WhatsApp client for user %s", userID)

	// Check if client already exists and is connected
	clientsMutex.RLock()
	if clientInfo, exists := clients[userID]; exists && clientInfo.Client.IsConnected() {
		log.Printf("Found existing connected client for user %s", userID)
		clientsMutex.RUnlock()
		return clientInfo, nil, true // Client exists and is connected
	}
	clientsMutex.RUnlock()

	// Create directory for database if it doesn't exist
	if err := os.MkdirAll("store", 0755); err != nil {
		log.Printf("Failed to create store directory: %v", err)
		return nil, fmt.Errorf("failed to create store directory: %v", err), false
	}

	// Logger for this client
	logger := waLog.Stdout(fmt.Sprintf("Client-%s", userID), "INFO", true)
	dbLog := waLog.Stdout(fmt.Sprintf("DB-%s", userID), "INFO", true)

	log.Printf("Creating store and client for user %s", userID)

	// DB path for this user's session
	dbPath := getUserDBPath(userID)

	// Create message store
	messageStore, err := NewMessageStore(userID)
	if err != nil {
		log.Printf("Failed to create message store for user %s: %v", userID, err)
		return nil, fmt.Errorf("failed to create message store: %v", err), false
	}

	// Create container for WhatsApp session data
	container, err := sqlstore.New("sqlite3", dbPath, dbLog)
	if err != nil {
		messageStore.Close()
		log.Printf("Failed to create WhatsApp container for user %s: %v", userID, err)
		return nil, fmt.Errorf("failed to connect to database: %v", err), false
	}

	// Try to get device from store, or create a new one
	deviceStore, err := container.GetFirstDevice()
	if err != nil {
		if err == sql.ErrNoRows {
			deviceStore = container.NewDevice()
			logger.Infof("Created new device for user %s", userID)
		} else {
			messageStore.Close()
			log.Printf("Failed to get device for user %s: %v", userID, err)
			return nil, fmt.Errorf("failed to get device: %v", err), false
		}
	}

	// Create client
	client := whatsmeow.NewClient(deviceStore, logger)
	clientInfo := &ClientInfo{
		Client:       client,
		Logger:       logger,
		MessageStore: messageStore,
		UserID:       userID,
	}

	log.Printf("Setting up event handlers for user %s", userID)

	// Set up event handling
	client.AddEventHandler(func(evt interface{}) {
		switch v := evt.(type) {
		case *events.Message:
			log.Printf("Received message event for user %s", userID)
			handleMessage(clientInfo, v)
		case *events.HistorySync:
			log.Printf("Received history sync event for user %s", userID)
			handleHistorySync(clientInfo, v)
		case *events.Connected:
			logger.Infof("Connected to WhatsApp for user %s", userID)
		case *events.LoggedOut:
			logger.Warnf("Device logged out for user %s", userID)
			// Could implement auto-reconnect here
		case *events.Receipt:
			if len(v.MessageIDs) > 0 {
				log.Printf("Received receipt event for user %s: messages %v were %s",
					userID, v.MessageIDs, v.Type)
			} else {
				log.Printf("Received receipt event for user %s with type %s",
					userID, v.Type)
			}
		case *events.Presence:
			log.Printf("Received presence event for user %s: %s is %s",
				userID, v.From.User, v.Unavailable)
		case *events.ChatPresence:
			log.Printf("Received chat presence event for user %s: %s",
				userID, v.State)
		}
	})

	// Store client in map
	clientsMutex.Lock()
	clients[userID] = clientInfo
	clientsMutex.Unlock()

	log.Printf("Client for user %s created and stored", userID)

	// Only connect if there's already a session
	isLoggedIn := client.Store.ID != nil
	if isLoggedIn {
		log.Printf("User %s is already logged in, connecting...", userID)
		go func() {
			if err := client.Connect(); err != nil {
				logger.Errorf("Failed to connect: %v", err)
			}
		}()
	} else {
		log.Printf("User %s is not logged in yet", userID)
	}

	return clientInfo, nil, isLoggedIn
}

// Start a REST API server to expose the WhatsApp client functionality
func startRESTServer(port int) {
	// Start background goroutine to clean up expired QR sessions
	go cleanupExpiredQRSessions()

	// Handler for sending messages
	http.HandleFunc("/api/send", func(w http.ResponseWriter, r *http.Request) {
		// Only allow POST requests
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		// Parse the request body
		var req SendMessageRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request format", http.StatusBadRequest)
			return
		}

		// Validate request
		if req.UserID == "" || req.Recipient == "" || req.Message == "" {
			http.Error(w, "User ID, recipient, and message are required", http.StatusBadRequest)
			return
		}

		log.Printf("Received message send request from user %s to recipient %s", req.UserID, req.Recipient)

		// Get client for the user
		clientsMutex.RLock()
		clientInfo, exists := clients[req.UserID]
		clientsMutex.RUnlock()

		if !exists || !clientInfo.Client.IsConnected() {
			log.Printf("User %s not connected, unable to send message", req.UserID)
			http.Error(w, "User not connected", http.StatusBadRequest)
			return
		}

		// Send the message
		log.Printf("Sending message from user %s to %s: %s", req.UserID, req.Recipient, req.Message)
		success, message := sendWhatsAppMessage(clientInfo.Client, req.Recipient, req.Message)
		log.Printf("Message send result: success=%v, message=%s", success, message)

		// Set response headers
		w.Header().Set("Content-Type", "application/json")

		// Set appropriate status code
		if !success {
			w.WriteHeader(http.StatusInternalServerError)
		}

		// Send response
		json.NewEncoder(w).Encode(SendMessageResponse{
			Success: success,
			Message: message,
		})
	})

	// Handler for user authentication/login
	http.HandleFunc("/api/auth", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var req AuthRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request format", http.StatusBadRequest)
			return
		}

		if req.UserID == "" {
			http.Error(w, "User ID is required", http.StatusBadRequest)
			return
		}

		// Check if we're already processing an auth request for this user
		authProcessesMutex.Lock()
		isProcessing := authProcesses[req.UserID]
		if !isProcessing {
			authProcesses[req.UserID] = true
		}
		authProcessesMutex.Unlock()

		if isProcessing {
			// Another process is already handling auth, check if QR is ready
			time.Sleep(500 * time.Millisecond) // Brief wait to let the other process generate QR

			qrSessionsMutex.RLock()
			session, hasQR := qrSessions[req.UserID]
			qrSessionsMutex.RUnlock()

			if hasQR && time.Now().Before(session.ExpiresAt) {
				// Return the existing QR code
				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(AuthResponse{
					Success:       true,
					QRString:      session.QRCode,
					QRImageBase64: session.QRImageBase64,
					Message:       "Please scan this QR code with your WhatsApp app",
					IsLoggedIn:    false,
				})
				return
			}

			// If we don't have a valid QR yet, continue and generate one
		}

		// Make sure we mark auth process as completed when done
		defer func() {
			authProcessesMutex.Lock()
			delete(authProcesses, req.UserID)
			authProcessesMutex.Unlock()
		}()

		// Check for existing valid QR session first
		qrSessionsMutex.RLock()
		session, hasQR := qrSessions[req.UserID]
		qrSessionsMutex.RUnlock()

		// Return existing QR if valid
		if hasQR && time.Now().Before(session.ExpiresAt) {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(AuthResponse{
				Success:       true,
				QRString:      session.QRCode,
				QRImageBase64: session.QRImageBase64,
				Message:       "Please scan this QR code with your WhatsApp app",
				IsLoggedIn:    false,
			})
			return
		}

		// Load or create client
		clientInfo, err, isLoggedIn := loadClientForUser(req.UserID)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to load client: %v", err), http.StatusInternalServerError)
			return
		}

		// If already logged in, just return success
		if isLoggedIn && clientInfo != nil && clientInfo.Client != nil && clientInfo.Client.Store != nil && clientInfo.Client.Store.ID != nil {
			// Try to connect (ignore already connected errors)
			err = clientInfo.Client.Connect()
			if err != nil && !strings.Contains(err.Error(), "websocket is already connected") {
				http.Error(w, fmt.Sprintf("Failed to connect: %v", err), http.StatusInternalServerError)
				return
			}

			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(AuthResponse{
				Success:    true,
				Message:    "Already logged in",
				IsLoggedIn: true,
			})
			return
		}

		// Not logged in, need to generate a new QR code
		if clientInfo == nil || clientInfo.Client == nil {
			http.Error(w, "Client initialization error", http.StatusInternalServerError)
			return
		}

		// Reset connection before requesting new QR code to avoid "already connected" errors
		resetClientConnection(req.UserID)

		// Get QR channel and connect
		qrChan, _ := clientInfo.Client.GetQRChannel(context.Background())
		err = clientInfo.Client.Connect()
		if err != nil {
			// Only treat as an error if it's not "already connected"
			if !strings.Contains(err.Error(), "websocket is already connected") {
				http.Error(w, fmt.Sprintf("Failed to connect: %v", err), http.StatusInternalServerError)
				return
			}
		}

		// Wait for QR code with timeout
		select {
		case evt := <-qrChan:
			if evt.Event == "code" {
				// Generate QR code as Base64 string
				qrCode := evt.Code
				qrBase64 := generateQRAsBase64(qrCode)

				// Store this QR session
				qrSessionsMutex.Lock()
				qrSessions[req.UserID] = &QRSession{
					QRCode:        qrCode,
					QRImageBase64: qrBase64,
					ExpiresAt:     time.Now().Add(55 * time.Second), // QR codes valid for ~60 seconds
					Client:        clientInfo.Client,
				}
				qrSessionsMutex.Unlock()

				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(AuthResponse{
					Success:       true,
					QRString:      qrCode,
					QRImageBase64: qrBase64,
					Message:       "Please scan this QR code with your WhatsApp app",
					IsLoggedIn:    false,
				})
				return
			}
		case <-time.After(10 * time.Second):
			http.Error(w, "Timeout waiting for QR code", http.StatusInternalServerError)
			return
		}
	})

	// Handler to check status of a user
	http.HandleFunc("/api/status", func(w http.ResponseWriter, r *http.Request) {
		userID := r.URL.Query().Get("user_id")
		if userID == "" {
			http.Error(w, "User ID is required", http.StatusBadRequest)
			return
		}

		clientsMutex.RLock()
		clientInfo, exists := clients[userID]
		clientsMutex.RUnlock()

		w.Header().Set("Content-Type", "application/json")
		if !exists || clientInfo == nil {
			json.NewEncoder(w).Encode(map[string]interface{}{
				"success":   true,
				"connected": false,
				"logged_in": false,
				"user_id":   userID,
				"message":   "User not found",
			})
			return
		}

		// Check for nil pointers
		if clientInfo.Client == nil {
			json.NewEncoder(w).Encode(map[string]interface{}{
				"success":   true,
				"connected": false,
				"logged_in": false,
				"user_id":   userID,
				"message":   "Client not initialized",
			})
			return
		}

		isConnected := clientInfo.Client.IsConnected()
		isLoggedIn := clientInfo.Client.Store != nil && clientInfo.Client.Store.ID != nil

		// If not connected but should be logged in, try to reconnect
		if !isConnected && isLoggedIn {
			err := clientInfo.Client.Connect()
			if err == nil {
				isConnected = true
			} else {
				fmt.Printf("Failed to reconnect client for user %s: %v\n", userID, err)
			}
		}

		// If user is logged in, we can clean up any QR sessions
		if isLoggedIn {
			qrSessionsMutex.Lock()
			delete(qrSessions, userID)
			qrSessionsMutex.Unlock()
		}

		// Get phone number safely
		var phoneNumber string
		if isLoggedIn && clientInfo.Client.Store != nil && clientInfo.Client.Store.ID != nil {
			phoneNumber = clientInfo.Client.Store.ID.User
		}

		json.NewEncoder(w).Encode(map[string]interface{}{
			"success":     true,
			"connected":   isConnected,
			"logged_in":   isLoggedIn,
			"user_id":     userID,
			"phone":       phoneNumber,
			"client_info": fmt.Sprintf("%p", clientInfo.Client),
		})
	})

	// Handler to list all active users
	http.HandleFunc("/api/users", func(w http.ResponseWriter, r *http.Request) {
		clientsMutex.RLock()
		userList := make([]map[string]interface{}, 0, len(clients))
		for userID, clientInfo := range clients {
			userList = append(userList, map[string]interface{}{
				"user_id":   userID,
				"connected": clientInfo.Client.IsConnected(),
				"logged_in": clientInfo.Client.Store.ID != nil,
				"phone":     clientInfo.Client.Store.ID.User,
			})
		}
		clientsMutex.RUnlock()

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"users": userList,
		})
	})

	// Handler for getting recent messages
	http.HandleFunc("/api/messages/recent", func(w http.ResponseWriter, r *http.Request) {
		userID := r.URL.Query().Get("user_id")
		if userID == "" {
			http.Error(w, "User ID is required", http.StatusBadRequest)
			return
		}

		limitStr := r.URL.Query().Get("limit")
		limit := 10 // Default limit
		if limitStr != "" {
			if parsedLimit, err := strconv.Atoi(limitStr); err == nil && parsedLimit > 0 {
				limit = parsedLimit
			}
		}

		clientsMutex.RLock()
		_, exists := clients[userID]
		clientsMutex.RUnlock()

		if !exists {
			http.Error(w, "User not found", http.StatusBadRequest)
			return
		}

		// Open user's message store
		messageStore, err := NewMessageStore(userID)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to open message store: %v", err), http.StatusInternalServerError)
			return
		}
		defer messageStore.Close()

		// Query recent messages
		db := messageStore.db
		rows, err := db.Query(`
			SELECT DISTINCT
				m.id,
				m.timestamp,
				m.sender,
				c.name,
				m.content,
				m.is_from_me,
				c.jid
			FROM messages m
			JOIN chats c ON m.chat_jid = c.jid
			ORDER BY m.timestamp DESC
			LIMIT ?
		`, limit)

		if err != nil {
			http.Error(w, fmt.Sprintf("Database error: %v", err), http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		var messages []MessageResponse
		// Track processed IDs to avoid duplicates
		processedIds := make(map[string]bool)

		for rows.Next() {
			var id, timestamp, sender, chatName, content, chatJID string
			var isFromMe bool
			if err := rows.Scan(&id, &timestamp, &sender, &chatName, &content, &isFromMe, &chatJID); err != nil {
				http.Error(w, fmt.Sprintf("Error scanning message row: %v", err), http.StatusInternalServerError)
				return
			}

			// Skip if we've already processed this message ID
			if processedIds[id] {
				continue
			}
			processedIds[id] = true

			messages = append(messages, MessageResponse{
				ID:        id,
				Timestamp: timestamp,
				Sender:    sender,
				Content:   content,
				IsFromMe:  isFromMe,
				ChatJID:   chatJID,
				ChatName:  chatName,
			})
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(MessagesListResponse{
			Items: messages,
		})
	})

	// Handler for listing chats
	http.HandleFunc("/api/chats/list", func(w http.ResponseWriter, r *http.Request) {
		userID := r.URL.Query().Get("user_id")
		if userID == "" {
			http.Error(w, "User ID is required", http.StatusBadRequest)
			return
		}

		query := r.URL.Query().Get("query")
		limitStr := r.URL.Query().Get("limit")
		pageStr := r.URL.Query().Get("page")
		includeLastMessageStr := r.URL.Query().Get("include_last_message")
		sortBy := r.URL.Query().Get("sort_by")

		limit := 20 // Default limit
		if limitStr != "" {
			if parsedLimit, err := strconv.Atoi(limitStr); err == nil && parsedLimit > 0 {
				limit = parsedLimit
			}
		}

		page := 0 // Default page
		if pageStr != "" {
			if parsedPage, err := strconv.Atoi(pageStr); err == nil && parsedPage >= 0 {
				page = parsedPage
			}
		}

		includeLastMessage := true // Default
		if includeLastMessageStr == "false" {
			includeLastMessage = false
		}

		if sortBy == "" {
			sortBy = "last_active" // Default sort
		}

		clientsMutex.RLock()
		_, exists := clients[userID]
		clientsMutex.RUnlock()

		if !exists {
			http.Error(w, "User not found", http.StatusBadRequest)
			return
		}

		// Open user's message store
		messageStore, err := NewMessageStore(userID)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to open message store: %v", err), http.StatusInternalServerError)
			return
		}
		defer messageStore.Close()

		// Build query
		queryParts := []string{`
			SELECT 
				chats.jid,
				chats.name,
				chats.last_message_time
		`}

		if includeLastMessage {
			queryParts = append(queryParts, `,
				messages.content as last_message,
				messages.sender as last_sender,
				messages.is_from_me as last_is_from_me
			FROM chats
			LEFT JOIN messages ON chats.jid = messages.chat_jid 
				AND chats.last_message_time = messages.timestamp
			`)
		} else {
			queryParts = append(queryParts, `
			FROM chats
			`)
		}

		var whereClause []string
		var params []interface{}

		if query != "" {
			whereClause = append(whereClause, "(LOWER(chats.name) LIKE LOWER(?) OR chats.jid LIKE ?)")
			params = append(params, "%"+query+"%", "%"+query+"%")
		}

		if len(whereClause) > 0 {
			queryParts = append(queryParts, "WHERE "+strings.Join(whereClause, " AND "))
		}

		// Add sorting
		orderBy := "chats.last_message_time DESC"
		if sortBy != "last_active" {
			orderBy = "chats.name"
		}
		queryParts = append(queryParts, "ORDER BY "+orderBy)

		// Add pagination
		offset := page * limit
		queryParts = append(queryParts, "LIMIT ? OFFSET ?")
		params = append(params, limit, offset)

		// Execute query
		db := messageStore.db
		rows, err := db.Query(strings.Join(queryParts, " "), params...)
		if err != nil {
			http.Error(w, fmt.Sprintf("Database error: %v", err), http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		var chats []ChatResponse
		for rows.Next() {
			var jid, name, lastMessageTime string
			var lastMessage, lastSender sql.NullString
			var lastIsFromMe sql.NullBool

			var scanErr error
			if includeLastMessage {
				scanErr = rows.Scan(&jid, &name, &lastMessageTime, &lastMessage, &lastSender, &lastIsFromMe)
			} else {
				scanErr = rows.Scan(&jid, &name, &lastMessageTime)
			}

			if scanErr != nil {
				http.Error(w, fmt.Sprintf("Error scanning chat row: %v", scanErr), http.StatusInternalServerError)
				return
			}

			isGroup := strings.HasSuffix(jid, "@g.us")

			chat := ChatResponse{
				JID:             jid,
				Name:            name,
				LastMessageTime: lastMessageTime,
				IsGroup:         isGroup,
			}

			if includeLastMessage {
				if lastMessage.Valid {
					chat.LastMessage = lastMessage.String
				}
				if lastSender.Valid {
					chat.LastSender = lastSender.String
				}
				if lastIsFromMe.Valid {
					chat.LastIsFromMe = lastIsFromMe.Bool
				}
			}

			chats = append(chats, chat)
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(ChatsListResponse{
			Items: chats,
		})
	})

	// Handler for searching contacts
	http.HandleFunc("/api/contacts/search", func(w http.ResponseWriter, r *http.Request) {
		userID := r.URL.Query().Get("user_id")
		query := r.URL.Query().Get("query")

		if userID == "" || query == "" {
			http.Error(w, "User ID and query are required", http.StatusBadRequest)
			return
		}

		clientsMutex.RLock()
		_, exists := clients[userID]
		clientsMutex.RUnlock()

		if !exists {
			http.Error(w, "User not found", http.StatusBadRequest)
			return
		}

		// Open user's message store
		messageStore, err := NewMessageStore(userID)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to open message store: %v", err), http.StatusInternalServerError)
			return
		}
		defer messageStore.Close()

		// Build search pattern
		searchPattern := "%" + query + "%"

		// Execute query
		db := messageStore.db
		rows, err := db.Query(`
			SELECT DISTINCT 
				jid,
				name
			FROM chats
			WHERE 
				(LOWER(name) LIKE LOWER(?) OR LOWER(jid) LIKE LOWER(?))
				AND jid NOT LIKE '%@g.us'
			ORDER BY name, jid
			LIMIT 50
		`, searchPattern, searchPattern)

		if err != nil {
			http.Error(w, fmt.Sprintf("Database error: %v", err), http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		var contacts []ContactResponse
		for rows.Next() {
			var jid, name string
			if err := rows.Scan(&jid, &name); err != nil {
				http.Error(w, fmt.Sprintf("Error scanning contact row: %v", err), http.StatusInternalServerError)
				return
			}

			phoneNumber := strings.Split(jid, "@")[0]

			contacts = append(contacts, ContactResponse{
				PhoneNumber: phoneNumber,
				Name:        name,
				JID:         jid,
			})
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(ContactsListResponse{
			Items: contacts,
		})
	})

	// Handler for listing messages with filters
	http.HandleFunc("/api/messages/list", func(w http.ResponseWriter, r *http.Request) {
		userID := r.URL.Query().Get("user_id")
		if userID == "" {
			http.Error(w, "User ID is required", http.StatusBadRequest)
			return
		}

		// Parse query parameters
		chatJID := r.URL.Query().Get("chat_jid")
		senderPhoneNumber := r.URL.Query().Get("sender_phone_number")
		messageQuery := r.URL.Query().Get("query")
		startDate := r.URL.Query().Get("start_date")
		endDate := r.URL.Query().Get("end_date")

		limitStr := r.URL.Query().Get("limit")
		pageStr := r.URL.Query().Get("page")
		includeContextStr := r.URL.Query().Get("include_context")
		contextBeforeStr := r.URL.Query().Get("context_before")
		contextAfterStr := r.URL.Query().Get("context_after")

		// Set defaults and parse parameters
		limit := 20
		if limitStr != "" {
			if parsedLimit, err := strconv.Atoi(limitStr); err == nil && parsedLimit > 0 {
				limit = parsedLimit
			}
		}

		page := 0
		if pageStr != "" {
			if parsedPage, err := strconv.Atoi(pageStr); err == nil && parsedPage >= 0 {
				page = parsedPage
			}
		}

		includeContext := true
		if includeContextStr == "false" {
			includeContext = false
		}

		contextBefore := 1
		if contextBeforeStr != "" {
			if parsedBefore, err := strconv.Atoi(contextBeforeStr); err == nil && parsedBefore >= 0 {
				contextBefore = parsedBefore
			}
		}

		contextAfter := 1
		if contextAfterStr != "" {
			if parsedAfter, err := strconv.Atoi(contextAfterStr); err == nil && parsedAfter >= 0 {
				contextAfter = parsedAfter
			}
		}

		// Open user's message store
		messageStore, err := NewMessageStore(userID)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to open message store: %v", err), http.StatusInternalServerError)
			return
		}
		defer messageStore.Close()

		// Build query
		queryParts := []string{"SELECT DISTINCT messages.id, messages.timestamp, messages.sender, chats.name, messages.content, messages.is_from_me, chats.jid FROM messages"}
		queryParts = append(queryParts, "JOIN chats ON messages.chat_jid = chats.jid")
		whereClause := []string{}
		var params []interface{}

		// Add filters to query
		if startDate != "" && endDate != "" {
			whereClause = append(whereClause, "messages.timestamp BETWEEN ? AND ?")
			params = append(params, startDate, endDate)
		}

		if senderPhoneNumber != "" {
			whereClause = append(whereClause, "messages.sender = ?")
			params = append(params, senderPhoneNumber)
		}

		if chatJID != "" {
			whereClause = append(whereClause, "messages.chat_jid = ?")
			params = append(params, chatJID)
		}

		if messageQuery != "" {
			whereClause = append(whereClause, "LOWER(messages.content) LIKE LOWER(?)")
			params = append(params, "%"+messageQuery+"%")
		}

		if len(whereClause) > 0 {
			queryParts = append(queryParts, "WHERE "+strings.Join(whereClause, " AND "))
		}

		// Add order, limit, offset
		offset := page * limit
		queryParts = append(queryParts, "ORDER BY messages.timestamp DESC")
		queryParts = append(queryParts, "LIMIT ? OFFSET ?")
		params = append(params, limit, offset)

		// Execute query
		db := messageStore.db
		rows, err := db.Query(strings.Join(queryParts, " "), params...)
		if err != nil {
			http.Error(w, fmt.Sprintf("Database error: %v", err), http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		messageIds := []string{}
		var messages []MessageResponse
		// Track processed IDs to avoid duplicates
		processedIds := make(map[string]bool)

		for rows.Next() {
			var id, timestamp, sender, chatName, content, chatJID string
			var isFromMe bool
			if err := rows.Scan(&id, &timestamp, &sender, &chatName, &content, &isFromMe, &chatJID); err != nil {
				http.Error(w, fmt.Sprintf("Error scanning message row: %v", err), http.StatusInternalServerError)
				return
			}

			// Skip if we've already processed this message ID
			if processedIds[id] {
				continue
			}
			processedIds[id] = true

			messages = append(messages, MessageResponse{
				ID:        id,
				Timestamp: timestamp,
				Sender:    sender,
				Content:   content,
				IsFromMe:  isFromMe,
				ChatJID:   chatJID,
				ChatName:  chatName,
			})

			if includeContext {
				messageIds = append(messageIds, id)
			}
		}

		// Add context for each message if requested
		if includeContext && len(messageIds) > 0 {
			var messagesWithContext []MessageResponse
			// Track IDs in context to avoid duplicates
			contextProcessedIds := make(map[string]bool)

			for _, id := range messageIds {
				// Get context for this message
				contextMessages, err := getMessageContextFromDB(messageStore.db, id, contextBefore, contextAfter)
				if err != nil {
					http.Error(w, fmt.Sprintf("Error getting message context: %v", err), http.StatusInternalServerError)
					return
				}

				// Add context messages to the result, skipping duplicates
				for _, contextMsg := range contextMessages {
					if !contextProcessedIds[contextMsg.ID] {
						messagesWithContext = append(messagesWithContext, contextMsg)
						contextProcessedIds[contextMsg.ID] = true
					}
				}
			}

			// Replace original messages with context-enhanced messages
			messages = messagesWithContext
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(MessagesListResponse{
			Items: messages,
		})
	})

	// Handler for getting message context
	http.HandleFunc("/api/messages/context", func(w http.ResponseWriter, r *http.Request) {
		userID := r.URL.Query().Get("user_id")
		messageID := r.URL.Query().Get("message_id")

		if userID == "" || messageID == "" {
			http.Error(w, "User ID and message ID are required", http.StatusBadRequest)
			return
		}

		// Parse context parameters
		beforeStr := r.URL.Query().Get("before")
		afterStr := r.URL.Query().Get("after")

		before := 5 // Default
		if beforeStr != "" {
			if parsedBefore, err := strconv.Atoi(beforeStr); err == nil && parsedBefore >= 0 {
				before = parsedBefore
			}
		}

		after := 5 // Default
		if afterStr != "" {
			if parsedAfter, err := strconv.Atoi(afterStr); err == nil && parsedAfter >= 0 {
				after = parsedAfter
			}
		}

		// Open user's message store
		messageStore, err := NewMessageStore(userID)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to open message store: %v", err), http.StatusInternalServerError)
			return
		}
		defer messageStore.Close()

		// Get message context
		contextMessages, err := getMessageContextFromDB(messageStore.db, messageID, before, after)
		if err != nil {
			http.Error(w, fmt.Sprintf("Error getting message context: %v", err), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(MessagesListResponse{
			Items: contextMessages,
		})
	})

	// Handler for getting a specific chat by JID
	http.HandleFunc("/api/chats/get", func(w http.ResponseWriter, r *http.Request) {
		userID := r.URL.Query().Get("user_id")
		chatJID := r.URL.Query().Get("chat_jid")
		includeLastMessageStr := r.URL.Query().Get("include_last_message")

		if userID == "" || chatJID == "" {
			http.Error(w, "User ID and chat JID are required", http.StatusBadRequest)
			return
		}

		includeLastMessage := true
		if includeLastMessageStr == "false" {
			includeLastMessage = false
		}

		// Open user's message store
		messageStore, err := NewMessageStore(userID)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to open message store: %v", err), http.StatusInternalServerError)
			return
		}
		defer messageStore.Close()

		// Build query
		query := `
			SELECT 
				c.jid,
				c.name,
				c.last_message_time`

		if includeLastMessage {
			query += `,
				m.content as last_message,
				m.sender as last_sender,
				m.is_from_me as last_is_from_me
			FROM chats c
			LEFT JOIN messages m ON c.jid = m.chat_jid 
				AND c.last_message_time = m.timestamp`
		} else {
			query += `
			FROM chats c`
		}

		query += " WHERE c.jid = ?"

		// Execute query
		db := messageStore.db
		var row *sql.Row

		if includeLastMessage {
			row = db.QueryRow(query, chatJID)
		} else {
			row = db.QueryRow(query, chatJID)
		}

		// Scan result
		var jid, name, lastMessageTime string
		var lastMessage, lastSender sql.NullString
		var lastIsFromMe sql.NullBool

		var scanErr error
		if includeLastMessage {
			scanErr = row.Scan(&jid, &name, &lastMessageTime, &lastMessage, &lastSender, &lastIsFromMe)
		} else {
			scanErr = row.Scan(&jid, &name, &lastMessageTime)
		}

		if scanErr == sql.ErrNoRows {
			http.Error(w, "Chat not found", http.StatusNotFound)
			return
		} else if scanErr != nil {
			http.Error(w, fmt.Sprintf("Database error: %v", scanErr), http.StatusInternalServerError)
			return
		}

		isGroup := strings.HasSuffix(jid, "@g.us")

		chat := ChatResponse{
			JID:             jid,
			Name:            name,
			LastMessageTime: lastMessageTime,
			IsGroup:         isGroup,
		}

		if includeLastMessage {
			if lastMessage.Valid {
				chat.LastMessage = lastMessage.String
			}
			if lastSender.Valid {
				chat.LastSender = lastSender.String
			}
			if lastIsFromMe.Valid {
				chat.LastIsFromMe = lastIsFromMe.Bool
			}
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(chat)
	})

	// Handler for getting direct chat by contact phone
	http.HandleFunc("/api/chats/get-by-contact", func(w http.ResponseWriter, r *http.Request) {
		userID := r.URL.Query().Get("user_id")
		phoneNumber := r.URL.Query().Get("phone_number")

		if userID == "" || phoneNumber == "" {
			http.Error(w, "User ID and phone number are required", http.StatusBadRequest)
			return
		}

		// Open user's message store
		messageStore, err := NewMessageStore(userID)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to open message store: %v", err), http.StatusInternalServerError)
			return
		}
		defer messageStore.Close()

		// Execute query
		db := messageStore.db
		row := db.QueryRow(`
			SELECT 
				c.jid,
				c.name,
				c.last_message_time,
				m.content as last_message,
				m.sender as last_sender,
				m.is_from_me as last_is_from_me
			FROM chats c
			LEFT JOIN messages m ON c.jid = m.chat_jid 
				AND c.last_message_time = m.timestamp
			WHERE c.jid LIKE ? AND c.jid NOT LIKE '%@g.us'
			LIMIT 1
		`, "%"+phoneNumber+"%")

		// Scan result
		var jid, name, lastMessageTime string
		var lastMessage, lastSender sql.NullString
		var lastIsFromMe sql.NullBool

		scanErr := row.Scan(&jid, &name, &lastMessageTime, &lastMessage, &lastSender, &lastIsFromMe)

		if scanErr == sql.ErrNoRows {
			http.Error(w, "Chat not found", http.StatusNotFound)
			return
		} else if scanErr != nil {
			http.Error(w, fmt.Sprintf("Database error: %v", scanErr), http.StatusInternalServerError)
			return
		}

		chat := ChatResponse{
			JID:             jid,
			Name:            name,
			LastMessageTime: lastMessageTime,
			IsGroup:         false,
		}

		if lastMessage.Valid {
			chat.LastMessage = lastMessage.String
		}
		if lastSender.Valid {
			chat.LastSender = lastSender.String
		}
		if lastIsFromMe.Valid {
			chat.LastIsFromMe = lastIsFromMe.Bool
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(chat)
	})

	// Handler for getting contact chats
	http.HandleFunc("/api/contacts/chats", func(w http.ResponseWriter, r *http.Request) {
		userID := r.URL.Query().Get("user_id")
		jid := r.URL.Query().Get("jid")

		if userID == "" || jid == "" {
			http.Error(w, "User ID and JID are required", http.StatusBadRequest)
			return
		}

		limitStr := r.URL.Query().Get("limit")
		pageStr := r.URL.Query().Get("page")

		limit := 20 // Default
		if limitStr != "" {
			if parsedLimit, err := strconv.Atoi(limitStr); err == nil && parsedLimit > 0 {
				limit = parsedLimit
			}
		}

		page := 0 // Default
		if pageStr != "" {
			if parsedPage, err := strconv.Atoi(pageStr); err == nil && parsedPage >= 0 {
				page = parsedPage
			}
		}

		// Open user's message store
		messageStore, err := NewMessageStore(userID)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to open message store: %v", err), http.StatusInternalServerError)
			return
		}
		defer messageStore.Close()

		// Execute query
		db := messageStore.db
		rows, err := db.Query(`
			SELECT DISTINCT
				c.jid,
				c.name,
				c.last_message_time,
				m.content as last_message,
				m.sender as last_sender,
				m.is_from_me as last_is_from_me
			FROM chats c
			JOIN messages m ON c.jid = m.chat_jid
			WHERE m.sender = ? OR c.jid = ?
			ORDER BY c.last_message_time DESC
			LIMIT ? OFFSET ?
		`, jid, jid, limit, page*limit)

		if err != nil {
			http.Error(w, fmt.Sprintf("Database error: %v", err), http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		var chats []ChatResponse
		for rows.Next() {
			var jid, name, lastMessageTime string
			var lastMessage, lastSender sql.NullString
			var lastIsFromMe sql.NullBool

			if err := rows.Scan(&jid, &name, &lastMessageTime, &lastMessage, &lastSender, &lastIsFromMe); err != nil {
				http.Error(w, fmt.Sprintf("Error scanning chat row: %v", err), http.StatusInternalServerError)
				return
			}

			isGroup := strings.HasSuffix(jid, "@g.us")

			chat := ChatResponse{
				JID:             jid,
				Name:            name,
				LastMessageTime: lastMessageTime,
				IsGroup:         isGroup,
			}

			if lastMessage.Valid {
				chat.LastMessage = lastMessage.String
			}
			if lastSender.Valid {
				chat.LastSender = lastSender.String
			}
			if lastIsFromMe.Valid {
				chat.LastIsFromMe = lastIsFromMe.Bool
			}

			chats = append(chats, chat)
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(ChatsListResponse{
			Items: chats,
		})
	})

	// Handler for getting last interaction with a contact
	http.HandleFunc("/api/contacts/last-interaction", func(w http.ResponseWriter, r *http.Request) {
		userID := r.URL.Query().Get("user_id")
		jid := r.URL.Query().Get("jid")

		if userID == "" || jid == "" {
			http.Error(w, "User ID and JID are required", http.StatusBadRequest)
			return
		}

		// Open user's message store
		messageStore, err := NewMessageStore(userID)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to open message store: %v", err), http.StatusInternalServerError)
			return
		}
		defer messageStore.Close()

		// Execute query
		db := messageStore.db
		row := db.QueryRow(`
			SELECT 
				m.timestamp,
				m.sender,
				c.name,
				m.content,
				m.is_from_me,
				c.jid,
				m.id
			FROM messages m
			JOIN chats c ON m.chat_jid = c.jid
			WHERE m.sender = ? OR c.jid = ?
			ORDER BY m.timestamp DESC
			LIMIT 1
		`, jid, jid)

		// Scan result
		var timestamp, sender, chatName, content, chatJID, id string
		var isFromMe bool

		scanErr := row.Scan(&timestamp, &sender, &chatName, &content, &isFromMe, &chatJID, &id)

		if scanErr == sql.ErrNoRows {
			http.Error(w, "No interaction found", http.StatusNotFound)
			return
		} else if scanErr != nil {
			http.Error(w, fmt.Sprintf("Database error: %v", scanErr), http.StatusInternalServerError)
			return
		}

		message := MessageResponse{
			ID:        id,
			Timestamp: timestamp,
			Sender:    sender,
			Content:   content,
			IsFromMe:  isFromMe,
			ChatJID:   chatJID,
			ChatName:  chatName,
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(message)
	})

	// Handler for disconnecting a user
	http.HandleFunc("/api/disconnect", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var req DisconnectRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		if req.UserID == "" {
			http.Error(w, "UserID is required", http.StatusBadRequest)
			return
		}

		success, message := disconnectUser(req.UserID)

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(DisconnectResponse{
			Success: success,
			Message: message,
		})
	})

	// Start the server
	serverAddr := fmt.Sprintf(":%d", port)
	fmt.Printf("Starting REST API server on %s...\n", serverAddr)

	// Run server in a goroutine so it doesn't block
	go func() {
		if err := http.ListenAndServe(serverAddr, nil); err != nil {
			fmt.Printf("REST API server error: %v\n", err)
		}
	}()
}

// Helper function to get message context
func getMessageContextFromDB(db *sql.DB, messageID string, before, after int) ([]MessageResponse, error) {
	// Get the target message first
	row := db.QueryRow(`
		SELECT messages.timestamp, messages.sender, chats.name, messages.content, messages.is_from_me, chats.jid, messages.id, messages.chat_jid
		FROM messages
		JOIN chats ON messages.chat_jid = chats.jid
		WHERE messages.id = ?
	`, messageID)

	var timestamp, sender, chatName, content, chatJID, id, chatJIDMsg string
	var isFromMe bool

	if err := row.Scan(&timestamp, &sender, &chatName, &content, &isFromMe, &chatJID, &id, &chatJIDMsg); err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("message with ID %s not found", messageID)
		}
		return nil, err
	}

	targetMessage := MessageResponse{
		ID:        id,
		Timestamp: timestamp,
		Sender:    sender,
		Content:   content,
		IsFromMe:  isFromMe,
		ChatJID:   chatJID,
		ChatName:  chatName,
	}

	// Get messages before
	rowsBefore, err := db.Query(`
		SELECT messages.timestamp, messages.sender, chats.name, messages.content, messages.is_from_me, chats.jid, messages.id
		FROM messages
		JOIN chats ON messages.chat_jid = chats.jid
		WHERE messages.chat_jid = ? AND messages.timestamp < ?
		ORDER BY messages.timestamp DESC
		LIMIT ?
	`, chatJIDMsg, timestamp, before)

	if err != nil {
		return nil, err
	}
	defer rowsBefore.Close()

	var beforeMessages []MessageResponse
	for rowsBefore.Next() {
		var msgTimestamp, msgSender, msgChatName, msgContent, msgChatJID, msgID string
		var msgIsFromMe bool

		if err := rowsBefore.Scan(&msgTimestamp, &msgSender, &msgChatName, &msgContent, &msgIsFromMe, &msgChatJID, &msgID); err != nil {
			return nil, err
		}

		beforeMessages = append(beforeMessages, MessageResponse{
			ID:        msgID,
			Timestamp: msgTimestamp,
			Sender:    msgSender,
			Content:   msgContent,
			IsFromMe:  msgIsFromMe,
			ChatJID:   msgChatJID,
			ChatName:  msgChatName,
		})
	}

	// Get messages after
	rowsAfter, err := db.Query(`
		SELECT messages.timestamp, messages.sender, chats.name, messages.content, messages.is_from_me, chats.jid, messages.id
		FROM messages
		JOIN chats ON messages.chat_jid = chats.jid
		WHERE messages.chat_jid = ? AND messages.timestamp > ?
		ORDER BY messages.timestamp ASC
		LIMIT ?
	`, chatJIDMsg, timestamp, after)

	if err != nil {
		return nil, err
	}
	defer rowsAfter.Close()

	var afterMessages []MessageResponse
	for rowsAfter.Next() {
		var msgTimestamp, msgSender, msgChatName, msgContent, msgChatJID, msgID string
		var msgIsFromMe bool

		if err := rowsAfter.Scan(&msgTimestamp, &msgSender, &msgChatName, &msgContent, &msgIsFromMe, &msgChatJID, &msgID); err != nil {
			return nil, err
		}

		afterMessages = append(afterMessages, MessageResponse{
			ID:        msgID,
			Timestamp: msgTimestamp,
			Sender:    msgSender,
			Content:   msgContent,
			IsFromMe:  msgIsFromMe,
			ChatJID:   msgChatJID,
			ChatName:  msgChatName,
		})
	}

	// Combine all messages
	var allMessages []MessageResponse
	// Reverse the before messages to be in chronological order
	for i := len(beforeMessages) - 1; i >= 0; i-- {
		allMessages = append(allMessages, beforeMessages[i])
	}
	allMessages = append(allMessages, targetMessage)
	allMessages = append(allMessages, afterMessages...)

	return allMessages, nil
}

func main() {
	// Set up logger
	logger := waLog.Stdout("Main", "INFO", true)
	logger.Infof("Starting WhatsApp client manager...")

	// Create store directory
	if err := os.MkdirAll("store", 0755); err != nil {
		logger.Errorf("Failed to create store directory: %v", err)
		return
	}

	// Start REST API server
	startRESTServer(8080)

	// Create a channel to keep the main goroutine alive
	exitChan := make(chan os.Signal, 1)
	signal.Notify(exitChan, syscall.SIGINT, syscall.SIGTERM)

	fmt.Println("REST server is running. Press Ctrl+C to disconnect and exit.")

	// Wait for termination signal
	<-exitChan

	fmt.Println("Disconnecting all clients...")
	// Disconnect all clients
	clientsMutex.Lock()
	for _, clientInfo := range clients {
		clientInfo.Client.Disconnect()
		clientInfo.MessageStore.Close()
	}
	clientsMutex.Unlock()
}

// GetChatName determines the appropriate name for a chat based on JID and other info
func GetChatName(clientInfo *ClientInfo, jid types.JID, chatJID string, conversation interface{}, sender string) string {
	// First, check if chat already exists in database with a name
	var existingName string
	err := clientInfo.MessageStore.db.QueryRow("SELECT name FROM chats WHERE jid = ?", chatJID).Scan(&existingName)
	if err == nil && existingName != "" {
		// Chat exists with a name, use that
		clientInfo.Logger.Infof("Using existing chat name for %s: %s", chatJID, existingName)
		return existingName
	}

	// Need to determine chat name
	var name string

	if jid.Server == "g.us" {
		// This is a group chat
		clientInfo.Logger.Infof("Getting name for group: %s", chatJID)

		// Use conversation data if provided (from history sync)
		if conversation != nil {
			// Extract name from conversation if available
			// This uses type assertions to handle different possible types
			var displayName, convName *string
			// Try to extract the fields we care about regardless of the exact type
			v := reflect.ValueOf(conversation)
			if v.Kind() == reflect.Ptr && !v.IsNil() {
				v = v.Elem()

				// Try to find DisplayName field
				if displayNameField := v.FieldByName("DisplayName"); displayNameField.IsValid() && displayNameField.Kind() == reflect.Ptr && !displayNameField.IsNil() {
					dn := displayNameField.Elem().String()
					displayName = &dn
				}

				// Try to find Name field
				if nameField := v.FieldByName("Name"); nameField.IsValid() && nameField.Kind() == reflect.Ptr && !nameField.IsNil() {
					n := nameField.Elem().String()
					convName = &n
				}
			}

			// Use the name we found
			if displayName != nil && *displayName != "" {
				name = *displayName
			} else if convName != nil && *convName != "" {
				name = *convName
			}
		}

		// If we didn't get a name, try group info
		if name == "" {
			groupInfo, err := clientInfo.Client.GetGroupInfo(jid)
			if err == nil && groupInfo.Name != "" {
				name = groupInfo.Name
			} else {
				// Fallback name for groups
				name = fmt.Sprintf("Group %s", jid.User)
			}
		}

		clientInfo.Logger.Infof("Using group name: %s", name)
	} else {
		// This is an individual contact
		clientInfo.Logger.Infof("Getting name for contact: %s", chatJID)

		// Just use contact info (full name)
		contact, err := clientInfo.Client.Store.Contacts.GetContact(jid)
		if err == nil && contact.FullName != "" {
			name = contact.FullName
		} else if sender != "" {
			// Fallback to sender
			name = sender
		} else {
			// Last fallback to JID
			name = jid.User
		}

		clientInfo.Logger.Infof("Using contact name: %s", name)
	}

	return name
}

// Handle regular incoming messages
func handleMessage(clientInfo *ClientInfo, msg *events.Message) {
	// Log that we've received a message to help with debugging
	clientInfo.Logger.Infof("Received message event from %s in chat %s",
		msg.Info.Sender.User, msg.Info.Chat.String())

	// Extract text content
	content := extractTextContent(msg.Message)
	if content == "" {
		clientInfo.Logger.Infof("Skipping non-text message from %s", msg.Info.Sender.User)
		return // Skip non-text messages
	}

	// Save message to database
	chatJID := msg.Info.Chat.String()
	sender := msg.Info.Sender.User

	// Get appropriate chat name (pass nil for conversation since we don't have one for regular messages)
	name := GetChatName(clientInfo, msg.Info.Chat, chatJID, nil, sender)

	// Update chat in database with the message timestamp (keeps last message time updated)
	err := clientInfo.MessageStore.StoreChat(chatJID, name, msg.Info.Timestamp)
	if err != nil {
		clientInfo.Logger.Errorf("Failed to store chat: %v", err)
	}

	// Check if this message already exists in database before storing it
	exists, err := messageExists(clientInfo.MessageStore.db, msg.Info.ID, chatJID)
	if err != nil {
		clientInfo.Logger.Errorf("Failed to check if message exists: %v", err)
	}

	if !exists {
		// Store message in database only if it doesn't already exist
		err = clientInfo.MessageStore.StoreMessage(
			msg.Info.ID,
			chatJID,
			sender,
			content,
			msg.Info.Timestamp,
			msg.Info.IsFromMe,
		)
		if err != nil {
			clientInfo.Logger.Errorf("Failed to store message: %v", err)
		} else {
			// Log message reception
			timestamp := msg.Info.Timestamp.Format("2006-01-02 15:04:05")
			direction := "←"
			if msg.Info.IsFromMe {
				direction = "→"
			}
			fmt.Printf("[User: %s][%s] %s %s: %s\n", clientInfo.UserID, timestamp, direction, sender, content)
		}
	} else {
		clientInfo.Logger.Infof("Message %s already exists, skipping", msg.Info.ID)
	}
}

// Helper function to check if a message exists
func messageExists(db *sql.DB, id string, chatJID string) (bool, error) {
	if db == nil {
		log.Printf("ERROR: Database connection is nil in messageExists")
		return false, fmt.Errorf("database connection is nil")
	}

	if id == "" || chatJID == "" {
		log.Printf("WARNING: Empty message ID (%s) or chat JID (%s) in messageExists", id, chatJID)
		return false, nil
	}

	log.Printf("Checking if message %s exists in chat %s", id, chatJID)

	var count int
	err := db.QueryRow("SELECT COUNT(*) FROM messages WHERE id = ? AND chat_jid = ?", id, chatJID).Scan(&count)
	if err != nil {
		log.Printf("Error checking if message exists: %v", err)
		return false, err
	}

	exists := count > 0
	log.Printf("Message %s in chat %s exists: %v", id, chatJID, exists)
	return exists, nil
}

// Handle history sync events
func handleHistorySync(clientInfo *ClientInfo, historySync *events.HistorySync) {
	fmt.Printf("[User: %s] Received history sync event with %d conversations\n",
		clientInfo.UserID, len(historySync.Data.Conversations))

	syncedCount := 0
	for _, conversation := range historySync.Data.Conversations {
		// Parse JID from the conversation
		if conversation.ID == nil {
			continue
		}

		chatJID := *conversation.ID

		// Try to parse the JID
		jid, err := types.ParseJID(chatJID)
		if err != nil {
			clientInfo.Logger.Warnf("Failed to parse JID %s: %v", chatJID, err)
			continue
		}

		// Get appropriate chat name by passing the history sync conversation directly
		name := GetChatName(clientInfo, jid, chatJID, conversation, "")

		// Process messages
		messages := conversation.Messages
		if len(messages) > 0 {
			// Update chat with latest message timestamp
			latestMsg := messages[0]
			if latestMsg == nil || latestMsg.Message == nil {
				continue
			}

			// Get timestamp from message info
			timestamp := time.Time{}
			if ts := latestMsg.Message.GetMessageTimestamp(); ts != 0 {
				timestamp = time.Unix(int64(ts), 0)
			} else {
				continue
			}

			clientInfo.MessageStore.StoreChat(chatJID, name, timestamp)

			// Store messages
			for _, msg := range messages {
				if msg == nil || msg.Message == nil {
					continue
				}

				// Extract text content
				var content string
				if msg.Message.Message != nil {
					if conv := msg.Message.Message.GetConversation(); conv != "" {
						content = conv
					} else if ext := msg.Message.Message.GetExtendedTextMessage(); ext != nil {
						content = ext.GetText()
					}
				}

				// Skip non-text messages
				if content == "" {
					continue
				}

				// Determine sender
				var sender string
				isFromMe := false
				if msg.Message.Key != nil {
					if msg.Message.Key.FromMe != nil {
						isFromMe = *msg.Message.Key.FromMe
					}
					if !isFromMe && msg.Message.Key.Participant != nil && *msg.Message.Key.Participant != "" {
						sender = *msg.Message.Key.Participant
					} else if isFromMe {
						sender = clientInfo.Client.Store.ID.User
					} else {
						sender = jid.User
					}
				} else {
					sender = jid.User
				}

				// Store message
				msgID := ""
				if msg.Message.Key != nil && msg.Message.Key.ID != nil {
					msgID = *msg.Message.Key.ID
				}

				// Get message timestamp
				timestamp := time.Time{}
				if ts := msg.Message.GetMessageTimestamp(); ts != 0 {
					timestamp = time.Unix(int64(ts), 0)
				} else {
					continue
				}

				// Check if this message already exists in database before storing it
				exists, checkErr := messageExists(clientInfo.MessageStore.db, msgID, chatJID)
				if checkErr != nil {
					clientInfo.Logger.Warnf("Failed to check if message exists: %v", checkErr)
				}

				if !exists {
					// Store message in database only if it doesn't already exist
					err = clientInfo.MessageStore.StoreMessage(
						msgID,
						chatJID,
						sender,
						content,
						timestamp,
						isFromMe,
					)
					if err != nil {
						clientInfo.Logger.Warnf("Failed to store history message: %v", err)
					} else {
						syncedCount++
						// Log successful message storage
						clientInfo.Logger.Infof("Stored message: [%s] %s -> %s: %s", timestamp.Format("2006-01-02 15:04:05"), sender, chatJID, content)
					}
				} else {
					clientInfo.Logger.Infof("History message %s already exists, skipping", msgID)
				}
			}
		}
	}

	fmt.Printf("[User: %s] History sync complete. Stored %d text messages.\n", clientInfo.UserID, syncedCount)
}

// Generate a QR code as a base64 string
func generateQRAsBase64(text string) string {
	// Create a buffer to hold the QR code image
	var buf bytes.Buffer

	// Generate the QR code to the buffer
	qrterminal.GenerateHalfBlock(text, qrterminal.L, &buf)

	// Convert to base64
	return base64.StdEncoding.EncodeToString(buf.Bytes())
}

// Helper function to check if a user already has an active QR session
func getActiveQRSession(userID string) *QRSession {
	qrSessionsMutex.RLock()
	defer qrSessionsMutex.RUnlock()

	session, exists := qrSessions[userID]
	if !exists {
		return nil
	}

	// Check if session has expired
	if time.Now().After(session.ExpiresAt) {
		// Clean up expired session
		delete(qrSessions, userID)
		return nil
	}

	return session
}

// Helper function to store a new QR session
func storeQRSession(userID string, qrCode string, qrBase64 string, client *whatsmeow.Client) {
	qrSessionsMutex.Lock()
	defer qrSessionsMutex.Unlock()

	// QR codes are typically valid for 60 seconds, but we'll use 55 to be safe
	qrSessions[userID] = &QRSession{
		QRCode:        qrCode,
		QRImageBase64: qrBase64,
		ExpiresAt:     time.Now().Add(55 * time.Second),
		Client:        client,
	}
}

// Periodically clean up expired QR sessions
func cleanupExpiredQRSessions() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			now := time.Now()

			// Get a list of expired sessions to avoid holding lock during cleanup
			var expiredSessions []string

			qrSessionsMutex.RLock()
			for userID, session := range qrSessions {
				if now.After(session.ExpiresAt) {
					expiredSessions = append(expiredSessions, userID)
				}
			}
			qrSessionsMutex.RUnlock()

			// Process expired sessions
			for _, userID := range expiredSessions {
				fmt.Printf("Cleaning up expired QR session for user %s\n", userID)

				// Check if the client is logged in before disconnecting
				clientsMutex.RLock()
				clientInfo, exists := clients[userID]
				clientsMutex.RUnlock()

				// If the client exists but is not logged in, disconnect it
				if exists && clientInfo != nil && clientInfo.Client != nil {
					isLoggedIn := clientInfo.Client.Store != nil && clientInfo.Client.Store.ID != nil

					if !isLoggedIn && clientInfo.Client.IsConnected() {
						// Disconnect the client to free up the socket
						fmt.Printf("Disconnecting abandoned client for user %s\n", userID)
						clientInfo.Client.Disconnect()
					}
				}

				// Remove the session
				qrSessionsMutex.Lock()
				delete(qrSessions, userID)
				qrSessionsMutex.Unlock()
			}
		}
	}
}

// Reset client connection to ensure we can get a fresh QR code
func resetClientConnection(userID string) {
	clientsMutex.Lock()
	defer clientsMutex.Unlock()

	clientInfo, exists := clients[userID]
	if !exists || clientInfo == nil || clientInfo.Client == nil {
		return
	}

	// Only disconnect if not logged in
	if clientInfo.Client.Store == nil || clientInfo.Client.Store.ID == nil {
		if clientInfo.Client.IsConnected() {
			clientInfo.Client.Disconnect()
			fmt.Printf("Disconnected client for user %s to reset connection\n", userID)
		}
	}
}

// disconnectUser removes the WhatsApp connection and deletes the database for a user
func disconnectUser(userID string) (bool, string) {
	// Get client info
	clientInfo, exists := clients[userID]
	if !exists {
		// If client doesn't exist in active connections, just delete the database
		dbPath := getUserDBPath(userID)
		userDir := fmt.Sprintf("store/%s", userID)

		if _, err := os.Stat(dbPath); err == nil {
			// Delete the database file
			if err := os.Remove(dbPath); err != nil {
				return false, fmt.Sprintf("Failed to delete database: %v", err)
			}

			// Remove directory if empty
			if files, err := os.ReadDir(userDir); err == nil && len(files) == 0 {
				if err := os.Remove(userDir); err != nil {
					log.Printf("Failed to remove empty user directory: %v", err)
				}
			}

			return true, "User disconnected and database deleted"
		}
		return false, "User not connected"
	}

	// Logout the client if it exists and is connected
	if clientInfo.Client != nil {
		// Check if the client is logged in
		if clientInfo.Client.IsConnected() {
			err := clientInfo.Client.Logout()
			if err != nil {
				log.Printf("Error logging out user %s: %v", userID, err)
				// Continue anyway to clean up resources
			}
		}

		// Disconnect the client
		clientInfo.Client.Disconnect()
	}

	// Close the message store
	if clientInfo.MessageStore != nil {
		if err := clientInfo.MessageStore.Close(); err != nil {
			log.Printf("Error closing message store for user %s: %v", userID, err)
		}
	}

	// Remove from active connections
	delete(clients, userID)

	// Delete the QR session if it exists
	delete(qrSessions, userID)

	// Skip device store deletion since we don't have access to the correct container variable
	// This will be handled on next connection attempt

	// Delete the database file using the new path structure
	dbPath := getUserDBPath(userID)
	userDir := fmt.Sprintf("store/%s", userID)

	if _, err := os.Stat(dbPath); err == nil {
		if err := os.Remove(dbPath); err != nil {
			return false, fmt.Sprintf("User disconnected but failed to delete database: %v", err)
		}
	}

	// Optionally remove the user directory if it's empty
	if files, err := os.ReadDir(userDir); err == nil && len(files) == 0 {
		if err := os.Remove(userDir); err != nil {
			log.Printf("Failed to remove empty user directory: %v", err)
		}
	}

	return true, "User disconnected and database deleted"
}
