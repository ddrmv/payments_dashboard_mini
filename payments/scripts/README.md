# Scripts Directory

This directory contains utility scripts for the payments dashboard project.

## Database Population Script

### `populate_database.py`

A script to populate the main database with sample data for development and testing purposes.

#### What it does:
- Clears all existing data from the database tables
- Creates 200 customers with random names, emails, and account statuses
- Creates 20 services with random names, types, prices, and billing cycles
- Creates 300 purchases using existing customers and services
- Creates 400 payments using existing customers and purchases

#### Usage:

From the project root directory:

```bash
# Run the script directly
python scripts/populate_database.py

# Or make it executable and run
chmod +x scripts/populate_database.py
./scripts/populate_database.py
```

#### Requirements:
- Django project must be properly configured
- Database must be migrated and accessible
- Required dependencies: `factory-boy`, `numpy`, `pandas`

#### Safety:
- **WARNING**: This script will delete ALL existing data in the database tables
- Only run this on development databases, never on production
- Make sure you have backups if needed

#### Output:
The script provides progress updates and final statistics showing the total count of each entity type created. 