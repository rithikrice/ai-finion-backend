package middlewares

// AuthMiddleware simply tracks sessionID→phoneNumber mappings.
type AuthMiddleware struct {
    sessionStore map[string]string
}

func NewAuthMiddleware() *AuthMiddleware {
    return &AuthMiddleware{sessionStore: make(map[string]string)}
}

// AddSession registers a session.
func (m *AuthMiddleware) AddSession(sessionID, phoneNumber string) {
    m.sessionStore[sessionID] = phoneNumber
}

// GetPhoneNumber looks up the phone for a sessionID (or "" if none).
func (m *AuthMiddleware) GetPhoneNumber(sessionID string) string {
    return m.sessionStore[sessionID]
}
