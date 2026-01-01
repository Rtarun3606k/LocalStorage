# Service Architecture

## Overview

This document describes the architecture of the service management system in authModule.

## Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│                     OrganizationModel                        │
├─────────────────────────────────────────────────────────────┤
│ • id (UUID, PK)                                              │
│ • name (String)                                              │
│ • createdAt (String)                                         │
│ • updatedAt (String)                                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ 1:N relationship
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      ServicesModel                           │
├─────────────────────────────────────────────────────────────┤
│ • id (UUID, PK)                                              │
│ • name (String) - e.g., "StorageEngine"                      │
│ • description (String)                                       │
│ • role (Enum) - Admin/User/Developer                         │
│ • organizationId (UUID, FK) → OrganizationModel              │
│ • createdAt (String)                                         │
│ • updatedAt (String)                                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ N:M relationship via UserService
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                       UserService                            │
│                    (Junction Table)                          │
├─────────────────────────────────────────────────────────────┤
│ • id (UUID, PK)                                              │
│ • user_id (UUID, FK) → UserModel                             │
│ • service_id (UUID, FK) → ServicesModel                      │
│ • role (String)                                              │
│ • enabled (Boolean)                                          │
│ • created_at (DateTime)                                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Belongs to
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                        UserModel                             │
├─────────────────────────────────────────────────────────────┤
│ • id (UUID, PK)                                              │
│ • name (String)                                              │
│ • email (String, Unique)                                     │
│ • passwordHash (String)                                      │
│ • dataOfBirth (String)                                       │
│ • createdAt (String)                                         │
│ • updatedAt (String)                                         │
└─────────────────────────────────────────────────────────────┘
```

## API Flow

### 1. Service Creation Flow
```
Client → POST /api/services/create
    ↓
[Validate Input]
    ↓
[Check Organization Exists]
    ↓
[Check Service Doesn't Exist]
    ↓
[Create ServicesModel Record]
    ↓
Response: Service Created
```

### 2. Service Assignment Flow
```
Client → POST /api/services/assign
    ↓
[Validate userId & serviceId]
    ↓
[Check User Exists]
    ↓
[Check Service Exists]
    ↓
[Check Not Already Assigned]
    ↓
[Create UserService Record]
    ↓
Response: Service Assigned
```

### 3. Seed Script Flow
```
Run: python utils/seedServices.py
    ↓
[Create/Get Default Organization]
    ↓
[Create StorageEngine Service]
    ↓
Output: Service ID & Organization ID
```

## API Endpoints

### Service Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/services/health` | Health check | No |
| POST | `/api/services/create` | Create new service | Yes* |
| GET | `/api/services/list` | List all services | Yes* |
| GET | `/api/services/<id>` | Get service details | Yes* |
| POST | `/api/services/assign` | Assign service to user | Yes* |

*Note: Auth middleware should be added in production

## Rate Limits

- `POST /api/services/create`: 10 requests/hour
- `POST /api/services/assign`: 10 requests/hour
- `GET /api/services/list`: 30 requests/minute
- `GET /api/services/<id>`: 30 requests/minute
- `GET /api/services/health`: 5 requests/minute

## Example: StorageEngine Service

### Service Record
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "StorageEngine",
  "description": "File storage and management service - handles upload, download, and management of files, images, and videos",
  "role": "User",
  "organizationId": "660e8400-e29b-41d4-a716-446655440000",
  "createdAt": "2026-01-01T15:00:00Z",
  "updatedAt": "2026-01-01T15:00:00Z"
}
```

### User-Service Assignment
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "user_id": "880e8400-e29b-41d4-a716-446655440000",
  "service_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "User",
  "enabled": true,
  "created_at": "2026-01-01T15:05:00Z"
}
```

## Integration with StorageEngine

### Current State
- StorageEngine service can be registered in authModule
- Users can be assigned to StorageEngine service
- Service metadata is stored and retrievable via API

### Future Enhancements
1. **API Key Generation**: Users generate API keys for StorageEngine access
2. **Token Validation**: StorageEngine validates API keys with authModule
3. **Permission Scopes**: Define what operations users can perform
4. **Audit Logging**: Track all service access attempts
5. **Usage Metrics**: Monitor service usage per user/organization

## Security Considerations

1. **Input Validation**: All inputs are validated before database operations
2. **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
3. **Rate Limiting**: Prevents abuse of API endpoints
4. **Error Handling**: Proper error messages without exposing sensitive data
5. **Logging**: All operations are logged for audit purposes

## File Structure

```
authModule/
├── routes/
│   └── serviceRoutes.py         # Service management endpoints
├── utils/
│   └── seedServices.py          # Database initialization
├── database/
│   ├── services.py              # ServicesModel definition
│   ├── userServices.py          # UserService junction table
│   ├── organization.py          # OrganizationModel
│   └── UserModel.py             # User model
├── STORAGEENGINE_INTEGRATION.md # Integration guide
├── USAGE_EXAMPLES.py            # Usage examples
└── SERVICE_ARCHITECTURE.md      # This file
```

## Deployment Checklist

- [ ] PostgreSQL database configured
- [ ] Environment variables set
- [ ] Database migrations run
- [ ] Seed script executed
- [ ] API endpoints tested
- [ ] Rate limiting verified
- [ ] Logging configured
- [ ] Authentication middleware added (production)
- [ ] HTTPS enabled (production)
- [ ] CORS properly configured
