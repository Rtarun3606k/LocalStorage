# Quick Reference: Authentication & API Keys

## Cookie Names for Frontend

### Cookies Set on Login
- **`access_token`** - Short-lived JWT (20 minutes)
- **`refresh_token`** - Long-lived JWT (14 days)

### Frontend Must Use
```javascript
credentials: 'include'  // In all fetch requests
```

---

## API Endpoints Summary

### User Authentication
```bash
# Login (sets cookies)
POST /api/users/login
Body: { "email": "user@example.com", "password": "password123" }
Returns: JWT tokens + Sets cookies (access_token, refresh_token)

# Logout (clears cookies)
POST /api/users/logout

# Refresh access token
POST /api/users/refresh
Uses: refresh_token cookie
Returns: New access token + Updates cookie
```

### API Key Management
```bash
# Generate API key for StorageEngine
POST /api/apikeys/generate
Body: {
  "userId": "user-uuid",
  "serviceId": "storage-engine-uuid",
  "scopes": ["read", "write"],
  "expiresInDays": 30
}
Returns: API key (shown only once!)

# List user's API keys
GET /api/apikeys/list?userId=user-uuid

# Revoke API key
POST /api/apikeys/revoke/{api-key-id}

# Validate API key (StorageEngine calls this)
POST /api/apikeys/validate
Body: { "apiKey": "key-string" }
OR
Header: Authorization: Bearer key-string
```

### Service Management
```bash
# Create service
POST /api/services/create

# List services
GET /api/services/list

# Assign service to user
POST /api/services/assign
```

---

## Frontend Integration Example

### Login
```javascript
const response = await fetch('http://localhost:5000/api/users/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',  // REQUIRED
  body: JSON.stringify({ email, password })
});

const data = await response.json();
// Cookies are automatically set: access_token, refresh_token
```

### Generate API Key
```javascript
const response = await fetch('http://localhost:5000/api/apikeys/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',  // Sends access_token cookie
  body: JSON.stringify({
    userId: data.userId,
    serviceId: 'storage-engine-service-id',
    scopes: ['read', 'write']
  })
});

const { apiKey } = await response.json();
// Save this API key - it won't be shown again!
```

### Use API Key with StorageEngine
```javascript
const formData = new FormData();
formData.append('file', file);

await fetch('http://localhost:8080/api/v1/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`
  },
  body: formData
});
```

---

## StorageEngine Integration

### Validate API Key (Go)
```go
func ValidateAPIKey(apiKey string) (bool, error) {
    authURL := "http://localhost:5000/api/apikeys/validate"
    
    payload := map[string]string{"apiKey": apiKey}
    jsonData, _ := json.Marshal(payload)
    
    resp, err := http.Post(authURL, "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        return false, err
    }
    defer resp.Body.Close()
    
    var result struct {
        Valid  bool   `json:"valid"`
        UserID string `json:"userId"`
        Role   string `json:"role"`
    }
    
    json.NewDecoder(resp.Body).Decode(&result)
    return result.Valid, nil
}

// Use in middleware
func AuthMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        apiKey := r.Header.Get("Authorization")
        if apiKey == "" {
            http.Error(w, "Unauthorized", 401)
            return
        }
        
        // Remove "Bearer " prefix
        if strings.HasPrefix(apiKey, "Bearer ") {
            apiKey = apiKey[7:]
        }
        
        valid, _ := ValidateAPIKey(apiKey)
        if !valid {
            http.Error(w, "Invalid API key", 401)
            return
        }
        
        next.ServeHTTP(w, r)
    })
}
```

---

## CORS Configuration

Frontend origin allowed: `http://localhost:3000`

To change, update in `authModule/app.py`:
```python
response.headers.add('Access-Control-Allow-Origin', 'https://your-frontend.com')
```

---

## Security Notes

✅ **HttpOnly Cookies** - JavaScript cannot access tokens (XSS protection)
✅ **SameSite=Lax** - CSRF protection
✅ **API Keys Hashed** - Stored with Argon2 hashing
✅ **Rate Limiting** - All endpoints protected
✅ **Expiration** - Both tokens and API keys expire

⚠️ **In Production:**
- Set `secure=True` for cookies (HTTPS only)
- Update CORS origin to actual frontend URL
- Use environment variables for secrets

---

## Complete Flow

```
1. User logs in via frontend
   ↓
2. authModule sets JWT cookies (access_token, refresh_token)
   ↓
3. Frontend generates API key for StorageEngine access
   ↓
4. Frontend sends API key to StorageEngine
   ↓
5. StorageEngine validates API key with authModule
   ↓
6. authModule confirms: valid + returns user info
   ↓
7. StorageEngine processes request
```

---

## Documentation Files

- **API_KEY_AND_COOKIES_GUIDE.md** - Complete guide with examples
- **STORAGEENGINE_INTEGRATION.md** - Service registration guide
- **SERVICE_ARCHITECTURE.md** - Database schema and architecture
- **QUICKSTART.md** - Getting started guide
- **This file** - Quick reference

---

## Troubleshooting

### Cookies not being set?
- Add `credentials: 'include'` to fetch
- Check CORS origin matches frontend URL
- Verify browser allows cookies

### API key validation fails?
- Check StorageEngine can reach authModule
- Verify API key not expired/revoked
- Check Authorization header format

### Token expired?
- Use `/api/users/refresh` to get new access token
- Refresh token valid for 14 days
