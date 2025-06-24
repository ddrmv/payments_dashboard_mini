# Payments Dashboard

A practice project for a Payments Dashboard for a telecom, built with Django, Django ORM, SQLAlchemy for advanced queries, DTL, Bootstrap, and PostgreSQL. The project focuses on Pandas for analytics, pytest for testing, and a user-friendly dashboard for transaction lists and reports.

## Project Overview
- **Objective**: Build a dashboard to display and analyze telecom payment transactions.
- **Technologies**:
  - Django (web framework, ORM for primary database operations)
  - SQLAlchemy (advanced queries, e.g., aggregations, filters)
  - Pandas (transaction analysis, e.g., daily totals)
  - pytest (>80% test coverage)
  - TDL (templates)
  - Bootstrap (frontend styling)
  - PostgreSQL (database)
- **Features**:
  - Models for customers, services, purchases, and payments.
  - Dashboard with transaction lists and analytics (e.g., daily totals).
  - Advanced queries via SQLAlchemy for performance-critical tasks.
  - Unit and integration tests.
  - Local deployment with Docker.

## Setup Instructions
### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- Docker (optional, for deployment)
- Git

### Installation
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd payments_dashboard_mini
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install django psycopg2-binary sqlalchemy pandas pytest pytest-django django-bootstrap-v5
   ```

4. **Configure PostgreSQL**:
   - Create a database: `createdb payments_dashboard_mini`
   - Update `settings.py` with your database credentials:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql',
             'NAME': 'payments_dashboard',
             'USER': '<your-user>',
             'PASSWORD': '<your-password>',
             'HOST': 'localhost',
             'PORT': '5432',
         }
     }
     ```

5. **Apply Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Set Up SQLAlchemy (Optional, for Advanced Queries)**:
   - Create a `db.py` module for SQLAlchemy configuration:
     ```python
     from sqlalchemy import create_engine
     from sqlalchemy.orm import sessionmaker
     engine = create_engine('postgresql://<user>:<password>@localhost:5432/payments_dashboard')
     Session = sessionmaker(bind=engine)
     ```
   - Use SQLAlchemy for specific tasks (e.g., complex aggregations) in views or scripts.

7. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Access the dashboard at `http://localhost:8000`.

8. **Run Tests**:
   ```bash
   pytest --cov --cov-report=html
   ```

9. **Deploy Locally with Docker** (Optional):
   ```bash
   docker-compose up --build
   ```

## Project Structure
- `payments_dashboard_mini/`: Django project directory.
- `payments/`: Django app with models, views, and templates.
- `templates/`: Templates styled with Bootstrap.
- `tests/`: pytest unit and integration tests.
- `scripts/`: Pandas and SQLAlchemy scripts for analytics.
- `docker-compose.yml`: Docker configuration for local deployment.

## Django Models
The models are defined using Django ORM in `payments/models.py`. They mirror the provided SQLAlchemy models but are optimized for Django’s ecosystem, with SQLAlchemy integration planned for advanced queries.

## SQLAlchemy Integration
For advanced queries (e.g., aggregations, filters), define equivalent SQLAlchemy models in a separate module (e.g., `payments/sqlalchemy_models.py`) and use them with the `Session` from `db.py`. Example:
```python
from sqlalchemy import Column, Integer, String, Float, Enum
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class Payment(Base):
    __tablename__ = 'payments'
    payment_id = Column(Integer, primary_key=True)
    amount = Column(Float)
    currency = Column(Enum(Currency))
    # Add other fields as needed
```

## Usage
- **Dashboard**: Access transaction lists and analytics at `/dashboard/`.
- **Analytics**: Use Pandas in `scripts/analytics.py` to compute daily totals, integrated into views.
- **Testing**: Run `pytest` to verify models, views, and analytics logic.
- **Documentation**: Maintain German/English docs in `docs/`.

## Notes
- Use Django ORM for CRUD operations and simple queries to leverage Django’s ecosystem (e.g., admin, forms).
- Reserve SQLAlchemy for performance-critical tasks (e.g., complex aggregations).
- Ensure migrations are applied before running the app.
- For production, configure a WSGI server (e.g., Gunicorn) and a reverse proxy (e.g., Nginx).
