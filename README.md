# Payments Dashboard

A simple payments dashboard built with Django, Django ORM, SQLAlchemy, DTL, Bootstrap, and PostgreSQL. With Customers, Services, Purchases and Payments models, tested with 20 services and 10 million records each for the other models.


## Project Overview
- **Objective**: Build a simple dashboard to display and analyze payment transactions.
- **Technologies**:
  - Django (web framework, ORM for primary/simple database operations)
  - SQLAlchemy (advanced queries)
  - Pandas (transaction analysis)
  - pytest
  - DTL (templates)
  - Bootstrap (frontend styling)
  - PostgreSQL (database)
- **Features**:
  - Models for customers, services, purchases, and payments, for Django ORM and SQLAlchemy.
  - Dashboard with transaction lists and example analytics.
  - Django ORM for simple queries and SQLAlchemy for more demanding ones.
  - Unit tests.

![](https://i.imgur.com/aoDMg0j.jpeg)

## Setup Instructions
### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- Docker (optional, for deployment)
- Git

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ddrmv/payments_dashboard_mini.git
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
   - Create a database: `createdb payments_dashboard_mini` ( also `test_payments_dashboard_mini`)
   - Update `settings.py` with your database credentials:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql',
             'NAME': 'payments_dashboard_mini',
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

67. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Access the dashboard at `http://localhost:8000`.

8. **Run Tests**:
   ```bash
   pytest --cov --cov-report=html
   ```

## Project Structure
- `payments_dashboard_mini/`: Django project directory.
- `payments/`: Django app with models, views, and templates.
- `templates/`: Templates styled with Bootstrap.
- `tests/`: pytest unit and integration tests.
- `scripts/`: Pandas and SQLAlchemy scripts for analytics.

## Django and SQLAlchemy Models
The models are defined using Django ORM in `payments/models.py`. They mirror the SQLAlchemy models, with SQLAlchemy integration implemented for advanced queries.


## Usage
- **Dashboard**: Access transaction lists and analytics at the homepage.
- **Testing**: Run `pytest` to verify models, views, and analytics logic.

## Notes
- Use Django ORM for CRUD operations and simple queries for Django’s ecosystem (e.g., admin, forms).
- SQLAlchemy for performance-critical tasks.
- Ensure migrations are applied before running the app.
