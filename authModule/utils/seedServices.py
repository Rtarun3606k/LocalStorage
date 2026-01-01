"""
Seed script to initialize default services in the database.
This script should be run after database migration to populate initial data.
"""

from app import app, db, log
from database.services import ServicesModel, UserRoleEnum
from database.organization import OrganizationModel
from sqlalchemy.exc import IntegrityError
import uuid


def create_default_organization():
    """Create a default organization if it doesn't exist"""
    try:
        # Check if default organization exists
        default_org = OrganizationModel.query.filter_by(name="Default Organization").first()
        
        if not default_org:
            default_org = OrganizationModel(
                name="Default Organization"
            )
            db.session.add(default_org)
            db.session.commit()
            print(f"✓ Created default organization: {default_org.name} (ID: {default_org.id})")
        else:
            print(f"✓ Default organization already exists: {default_org.name} (ID: {default_org.id})")
        
        return default_org
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creating default organization: {str(e)}")
        raise


def create_storage_engine_service(organization_id):
    """Create the StorageEngine service"""
    try:
        # Check if StorageEngine service already exists
        storage_service = ServicesModel.query.filter_by(
            name="StorageEngine",
            organizationId=organization_id
        ).first()
        
        if not storage_service:
            storage_service = ServicesModel(
                name="StorageEngine",
                description="File storage and management service - handles upload, download, and management of files, images, and videos",
                role=UserRoleEnum.User,
                organizationId=organization_id
            )
            db.session.add(storage_service)
            db.session.commit()
            print(f"✓ Created StorageEngine service (ID: {storage_service.id})")
        else:
            print(f"✓ StorageEngine service already exists (ID: {storage_service.id})")
        
        return storage_service
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creating StorageEngine service: {str(e)}")
        raise


def seed_services():
    """Main function to seed all default services"""
    print("\n" + "="*50)
    print("Starting service seeding...")
    print("="*50 + "\n")
    
    try:
        with app.app_context():
            # Step 1: Create default organization
            print("Step 1: Creating default organization...")
            default_org = create_default_organization()
            
            # Step 2: Create StorageEngine service
            print("\nStep 2: Creating StorageEngine service...")
            storage_service = create_storage_engine_service(default_org.id)
            
            # You can add more services here in the future
            # Example:
            # print("\nStep 3: Creating AuthService...")
            # create_auth_service(default_org.id)
            
            print("\n" + "="*50)
            print("Service seeding completed successfully!")
            print("="*50)
            print("\nServices created:")
            print(f"  - {storage_service.name}: {storage_service.description}")
            print(f"    Organization: {default_org.name}")
            print(f"    Service ID: {storage_service.id}")
            print(f"    Organization ID: {default_org.id}")
            print("\nYou can now assign this service to users using the /api/services/assign endpoint")
            print("="*50 + "\n")
            
    except Exception as e:
        print(f"\n✗ Service seeding failed: {str(e)}")
        raise


if __name__ == "__main__":
    seed_services()
