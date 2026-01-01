#!/usr/bin/env python3
"""
Example usage script for StorageEngine service management

This script demonstrates how to:
1. Initialize the database with the StorageEngine service
2. Create users
3. Assign services to users
4. Generate API keys for service access

Note: This requires a running PostgreSQL database
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(title)
    print("="*60)


def print_response(response):
    """Print formatted response"""
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def example_workflow():
    """Demonstrate the complete workflow"""
    
    print_section("StorageEngine Service Management - Example Workflow")
    
    # Step 1: Check health
    print_section("Step 1: Health Check")
    print("Checking service routes health...")
    print(f"GET {API_BASE}/services/health")
    # response = requests.get(f"{API_BASE}/services/health")
    # print_response(response)
    print("\nCommand:")
    print(f"curl -X GET {API_BASE}/services/health")
    
    
    # Step 2: Seed the database
    print_section("Step 2: Seed Database with StorageEngine Service")
    print("\nRun the seed script:")
    print("cd authModule && python utils/seedServices.py")
    print("\nThis will create:")
    print("  - Default Organization")
    print("  - StorageEngine Service")
    
    
    # Step 3: Register a user
    print_section("Step 3: Register a User")
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "dateOfBirth": "1990-01-01",
        "password": "SecurePassword123!",
        "password_confirm": "SecurePassword123!"
    }
    print(f"POST {API_BASE}/users/register")
    print(f"Data: {json.dumps(user_data, indent=2)}")
    print("\nCommand:")
    print(f"""curl -X POST {API_BASE}/users/register \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(user_data)}'""")
    
    
    # Step 4: List services
    print_section("Step 4: List Available Services")
    print(f"GET {API_BASE}/services/list")
    print("\nCommand:")
    print(f"curl -X GET {API_BASE}/services/list")
    print("\nExpected response will include StorageEngine service with its ID")
    
    
    # Step 5: Assign service to user
    print_section("Step 5: Assign StorageEngine to User")
    assign_data = {
        "userId": "<user-id-from-step-3>",
        "serviceId": "<service-id-from-step-4>",
        "role": "User"
    }
    print(f"POST {API_BASE}/services/assign")
    print(f"Data: {json.dumps(assign_data, indent=2)}")
    print("\nCommand:")
    print(f"""curl -X POST {API_BASE}/services/assign \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(assign_data)}'""")
    
    
    # Step 6: Get service details
    print_section("Step 6: Get Service Details")
    print(f"GET {API_BASE}/services/<service-id>")
    print("\nCommand:")
    print(f"curl -X GET {API_BASE}/services/<service-id>")
    
    
    # Summary
    print_section("Integration Summary")
    print("""
The StorageEngine service is now integrated with the authModule!

Next Steps:
1. Run the seed script to initialize the service
2. Register users via the API
3. Assign the StorageEngine service to users
4. Users can now generate API keys for accessing StorageEngine
5. Implement authentication middleware in StorageEngine to verify API keys

Architecture:
  User → UserService → Service (StorageEngine) → Organization
            ↓
         ApiKey (for API access)

For more details, see: STORAGEENGINE_INTEGRATION.md
    """)


def api_endpoint_reference():
    """Print API endpoint reference"""
    print_section("API Endpoint Reference")
    
    endpoints = [
        ("GET", "/api/services/health", "Health check"),
        ("POST", "/api/services/create", "Create a new service"),
        ("GET", "/api/services/list", "List all services"),
        ("GET", "/api/services/<id>", "Get specific service"),
        ("POST", "/api/services/assign", "Assign service to user"),
    ]
    
    print("\nAvailable Endpoints:")
    print("-" * 60)
    for method, endpoint, description in endpoints:
        print(f"{method:6} {endpoint:30} - {description}")
    
    print("\n" + "-" * 60)


if __name__ == "__main__":
    example_workflow()
    api_endpoint_reference()
