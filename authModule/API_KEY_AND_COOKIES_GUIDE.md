# API Key and Cookie Authentication Guide

## Overview

The authModule now supports two authentication methods:
1. **JWT Tokens with Cookies** - For frontend applications
2. **API Keys** - For service-to-service communication (e.g., StorageEngine)

## Cookie-Based Authentication (Frontend)

### Login Flow

When a user logs in, the server returns JWT tokens both in the response body AND sets them as HTTP-only cookies:

```bash
POST /api/users/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "User user@example.com logged in successfully",
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "userName": "John Doe",
  "email": "user@example.com",
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Cookies Set:**
- `access_token` - HttpOnly, 20 minutes expiration
- `refresh_token` - HttpOnly, 14 days expiration

### Cookie Names and Settings

#### Access Token Cookie
- **Name:** `access_token`
- **Duration:** 20 minutes
- **HttpOnly:** Yes (JavaScript cannot access)
- **SameSite:** Lax (CSRF protection)
- **Secure:** No (set to Yes in production with HTTPS)
- **Path:** `/`

#### Refresh Token Cookie
- **Name:** `refresh_token`
- **Duration:** 14 days
- **HttpOnly:** Yes
- **SameSite:** Lax
- **Secure:** No (set to Yes in production)
- **Path:** `/`

### Frontend Integration

#### JavaScript/React Example

```javascript
// Login request - credentials: 'include' is required to send/receive cookies
const login = async (email, password) => {
  const response = await fetch('http://localhost:5000/api/users/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // IMPORTANT: This sends and receives cookies
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  // Tokens are also in response body (optional to store in localStorage)
  // BUT cookies are automatically set by the browser
  console.log('User logged in:', data);
  return data;
};

// Making authenticated requests
const fetchUserData = async () => {
  const response = await fetch('http://localhost:5000/api/some-protected-route', {
    method: 'GET',
    credentials: 'include', // Automatically sends cookies
  });
  
  return response.json();
};

// Logout
const logout = async () => {
  const response = await fetch('http://localhost:5000/api/users/logout', {
    method: 'POST',
    credentials: 'include',
  });
  
  // Cookies are automatically cleared
  return response.json();
};

// Refresh access token
const refreshToken = async () => {
  const response = await fetch('http://localhost:5000/api/users/refresh', {
    method: 'POST',
    credentials: 'include',
  });
  
  // New access token cookie is automatically set
  return response.json();
};
```

### CORS Configuration

The authModule is configured to allow cookies from:
- `http://localhost:3000` (default frontend)

To allow your frontend domain, update the CORS settings in `app.py`:

```python
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://your-frontend.com')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    # ...
```

### Additional Endpoints

#### Logout
```bash
POST /api/users/logout
```
Clears both `access_token` and `refresh_token` cookies.

#### Refresh Token
```bash
POST /api/users/refresh
```
Uses the `refresh_token` cookie to generate a new `access_token`.

---

## API Key Authentication (StorageEngine)

### Workflow

1. **User logs in** → Gets JWT tokens in cookies
2. **User generates API key** → For StorageEngine access
3. **Frontend sends API key to StorageEngine** → StorageEngine validates with authModule
4. **StorageEngine validates** → Makes request to authModule's `/api/apikeys/validate` endpoint

### API Key Endpoints

#### 1. Generate API Key

```bash
POST /api/apikeys/generate
Content-Type: application/json

{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "serviceId": "660e8400-e29b-41d4-a716-446655440000",
  "scopes": ["read", "write"],
  "expiresInDays": 30
}
```

**Response:**
```json
{
  "message": "API key generated successfully",
  "apiKey": "xRtP3k9mN2vL8hQ1wY5sT7jK4bG6fD0zA9cX",
  "apiKeyId": "770e8400-e29b-41d4-a716-446655440000",
  "serviceName": "StorageEngine",
  "scopes": ["read", "write"],
  "expiresAt": "2026-01-31T15:00:00Z",
  "warning": "Store this API key securely. It will not be shown again."
}
```

⚠️ **Important:** The raw API key is only shown once! Store it securely.

#### 2. List User's API Keys

```bash
GET /api/apikeys/list?userId=550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "apiKeys": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "serviceId": "660e8400-e29b-41d4-a716-446655440000",
      "serviceName": "StorageEngine",
      "role": "User",
      "scopes": ["read", "write"],
      "revoked": false,
      "expiresAt": "2026-01-31T15:00:00Z",
      "createdAt": "2026-01-01T15:00:00Z",
      "isExpired": false
    }
  ],
  "count": 1
}
```

#### 3. Revoke API Key

```bash
POST /api/apikeys/revoke/770e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "message": "API key revoked successfully",
  "apiKeyId": "770e8400-e29b-41d4-a716-446655440000"
}
```

#### 4. Validate API Key (StorageEngine calls this)

```bash
POST /api/apikeys/validate
Content-Type: application/json

{
  "apiKey": "xRtP3k9mN2vL8hQ1wY5sT7jK4bG6fD0zA9cX"
}
```

OR

```bash
GET /api/apikeys/validate
Authorization: Bearer xRtP3k9mN2vL8hQ1wY5sT7jK4bG6fD0zA9cX
```

**Valid Response:**
```json
{
  "valid": true,
  "apiKeyId": "770e8400-e29b-41d4-a716-446655440000",
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "serviceId": "660e8400-e29b-41d4-a716-446655440000",
  "serviceName": "StorageEngine",
  "role": "User",
  "scopes": ["read", "write"],
  "userEmail": "user@example.com",
  "userName": "John Doe"
}
```

**Invalid Response:**
```json
{
  "valid": false,
  "error": "Invalid API key"
}
```

---

## StorageEngine Integration

### How StorageEngine Should Validate Requests

In your StorageEngine (Go) middleware, validate the API key:

```go
package middleware

import (
    "bytes"
    "encoding/json"
    "io/ioutil"
    "net/http"
)

type ValidationResponse struct {
    Valid       bool   `json:"valid"`
    UserID      string `json:"userId"`
    ServiceID   string `json:"serviceId"`
    ServiceName string `json:"serviceName"`
    UserEmail   string `json:"userEmail"`
    UserName    string `json:"userName"`
    Role        string `json:"role"`
    Scopes      []string `json:"scopes"`
}

func ValidateAPIKey(apiKey string) (*ValidationResponse, error) {
    authModuleURL := "http://localhost:5000/api/apikeys/validate"
    
    payload := map[string]string{"apiKey": apiKey}
    jsonData, _ := json.Marshal(payload)
    
    resp, err := http.Post(authModuleURL, "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    body, _ := ioutil.ReadAll(resp.Body)
    
    var validation ValidationResponse
    json.Unmarshal(body, &validation)
    
    return &validation, nil
}

// Middleware example
func AuthMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        apiKey := r.Header.Get("Authorization")
        if apiKey == "" {
            http.Error(w, "API key required", http.StatusUnauthorized)
            return
        }
        
        // Remove "Bearer " prefix if present
        if len(apiKey) > 7 && apiKey[:7] == "Bearer " {
            apiKey = apiKey[7:]
        }
        
        validation, err := ValidateAPIKey(apiKey)
        if err != nil || !validation.Valid {
            http.Error(w, "Invalid API key", http.StatusUnauthorized)
            return
        }
        
        // Add user info to request context
        // ctx := context.WithValue(r.Context(), "userId", validation.UserID)
        // next.ServeHTTP(w, r.WithContext(ctx))
        
        next.ServeHTTP(w, r)
    })
}
```

---

## Complete Flow Example

### Frontend → StorageEngine Integration

1. **User logs in to authModule:**
   ```javascript
   await fetch('http://localhost:5000/api/users/login', {
     method: 'POST',
     credentials: 'include',
     body: JSON.stringify({ email, password })
   });
   // Cookies: access_token, refresh_token are set
   ```

2. **Frontend generates API key for StorageEngine:**
   ```javascript
   const response = await fetch('http://localhost:5000/api/apikeys/generate', {
     method: 'POST',
     credentials: 'include', // Sends access_token cookie for auth
     body: JSON.stringify({
       userId: "user-id",
       serviceId: "storage-engine-service-id",
       scopes: ["read", "write"]
     })
   });
   const { apiKey } = await response.json();
   // Store apiKey in localStorage or state
   ```

3. **Frontend sends request to StorageEngine with API key:**
   ```javascript
   await fetch('http://localhost:8080/api/v1/upload', {
     method: 'POST',
     headers: {
       'Authorization': `Bearer ${apiKey}`
     },
     body: formData
   });
   ```

4. **StorageEngine validates API key with authModule:**
   ```go
   // StorageEngine middleware calls authModule
   validation, err := ValidateAPIKey(apiKey)
   if !validation.Valid {
       http.Error(w, "Unauthorized", 401)
       return
   }
   // Process upload...
   ```

---

## Security Best Practices

### Frontend
- ✅ Always use `credentials: 'include'` when making requests
- ✅ Cookies are HttpOnly (JavaScript cannot access them)
- ✅ Store API keys securely if needed in localStorage
- ✅ Use HTTPS in production
- ✅ Handle token refresh automatically

### StorageEngine
- ✅ Always validate API keys with authModule
- ✅ Check API key expiration
- ✅ Respect scopes (read/write permissions)
- ✅ Log all authentication attempts
- ✅ Use HTTPS in production

### Production Settings
- Set `secure=True` for cookies (HTTPS only)
- Update CORS origin to your actual frontend domain
- Use environment variables for secrets
- Enable HTTPS on all services
- Implement rate limiting
- Add request logging and monitoring

---

## Environment Variables

Add these to your production configuration:

```bash
# authModule
FRONTEND_URL=https://your-frontend.com
JWT_SECRET=your-super-secret-jwt-key
JWT_REFRESH_SECRET=your-refresh-secret-key
COOKIE_SECURE=true
COOKIE_SAMESITE=Strict

# StorageEngine
AUTH_MODULE_URL=https://auth.your-domain.com
```

---

## Troubleshooting

### Cookies not being set
- Check `credentials: 'include'` in fetch requests
- Verify CORS origin matches your frontend URL
- Check browser console for CORS errors

### API key validation fails
- Ensure StorageEngine can reach authModule
- Check API key hasn't expired
- Verify API key hasn't been revoked
- Check network connectivity

### Token expired
- Use `/api/users/refresh` endpoint to get new access token
- Refresh token valid for 14 days
