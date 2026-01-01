# StorageEngine Service Integration

This document explains how to add and manage the StorageEngine service in the authModule.

## Overview

The authModule now includes service management functionality that allows you to:
- Create services (like StorageEngine)
- List available services
- Assign services to users
- Manage user permissions for each service

## Quick Start

### 1. Initialize the Database

First, make sure your database is set up and running:

```bash
cd authModule
python server.py
```

This will create all necessary tables.

### 2. Seed the StorageEngine Service

Run the seed script to automatically create the default organization and StorageEngine service:

```bash
cd authModule
python utils/seedServices.py
```

This will:
- Create a "Default Organization" if it doesn't exist
- Create the "StorageEngine" service linked to that organization
- Output the service ID and organization ID for future reference

### 3. API Endpoints

#### Health Check
```bash
GET /api/services/health
```

#### Create a Service (Manual)
```bash
POST /api/services/create
Content-Type: application/json

{
  "name": "StorageEngine",
  "description": "File storage and management service",
  "role": "User",
  "organizationId": "your-organization-uuid"
}
```

#### List All Services
```bash
GET /api/services/list
# Optional: filter by organization
GET /api/services/list?organizationId=your-organization-uuid
```

#### Get a Specific Service
```bash
GET /api/services/{service_id}
```

#### Assign Service to User
```bash
POST /api/services/assign
Content-Type: application/json

{
  "userId": "user-uuid",
  "serviceId": "service-uuid",
  "role": "User"
}
```

## Integration with StorageEngine

Once the StorageEngine service is registered in the authModule:

1. Users can be assigned access to the StorageEngine service
2. API keys can be generated for users to access the StorageEngine
3. The authModule can validate requests to the StorageEngine based on user permissions

## Architecture

```
┌─────────────┐
│ UserModel   │
└──────┬──────┘
       │
       │ has many
       ▼
┌──────────────┐      ┌────────────────┐
│ UserService  │─────▶│ ServicesModel  │
└──────────────┘      └────────┬───────┘
       │                       │
       │                       │ belongs to
       │                       ▼
       │              ┌─────────────────────┐
       │              │ OrganizationModel   │
       │              └─────────────────────┘
       │
       │ for API access
       ▼
┌─────────────┐
│   ApiKey    │
└─────────────┘
```

## Database Models

### ServicesModel
- `id`: UUID (primary key)
- `name`: Service name (e.g., "StorageEngine")
- `description`: Service description
- `role`: User role required (Admin/User/Developer)
- `organizationId`: Foreign key to organization
- `createdAt`, `updatedAt`: Timestamps

### UserService (Junction table)
- Links users to services they can access
- Includes role and enabled status

### ApiKey
- Allows users to generate API keys for specific services
- Includes scopes and expiration

## Example Workflow

1. **Setup**: Run `python utils/seedServices.py` to create StorageEngine service
2. **Register User**: User registers via `/api/users/register`
3. **Assign Service**: Admin assigns StorageEngine to user via `/api/services/assign`
4. **Generate API Key**: User generates API key for StorageEngine
5. **Access**: User uses API key to access StorageEngine endpoints

## Notes

- All endpoints use rate limiting to prevent abuse
- Services are organization-scoped for multi-tenancy support
- The same user can have different roles for different services
