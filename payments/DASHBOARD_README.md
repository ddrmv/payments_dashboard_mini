# Payments Dashboard

This dashboard demonstrates the use of both Django ORM and SQLAlchemy queries in a single Django application.

## Features

### Django ORM Query (Simple)
- **Recent Payments**: Shows the last 10 payments with customer and service information
- Uses Django's `select_related()` for efficient database queries
- Displays payment amount, customer name, service name, and payment status

### SQLAlchemy Queries (Complex)
- **Service Statistics**: Complex analytics by service type including:
  - Total payments and amounts by service type
  - Average payment amount by service type
  - Success rate by service type
  - Payment method distribution (Credit Card, Bank Transfer, Mobile Payment)
- **Top Customers**: Shows top 5 customers by total payment amount with:
  - Total spent
  - Number of payments
  - Average payment amount

## How to Access

1. Make sure the Django development server is running:
   ```bash
   python manage.py runserver
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000/
   ```

## Technical Details

### Django ORM Query
```python
recent_payments = Payment.objects.select_related(
    'customer', 'purchase__service'
).order_by('-timestamp')[:10]
```

### SQLAlchemy Queries
The dashboard uses complex SQLAlchemy queries with:
- Multiple table joins
- Aggregation functions (`count`, `sum`, `avg`)
- Conditional expressions (`case` statements)
- Grouping and ordering

### Template Features
- Modern, responsive design with CSS Grid and Flexbox
- Color-coded payment status indicators
- Hover effects and smooth transitions
- Mobile-friendly layout

## Database Requirements

The dashboard requires the database to be populated with sample data. You can populate it using:

```bash
python payments/scripts/populate_database.py
```

## Files Created/Modified

- `payments/views.py` - Dashboard view with both ORM queries
- `payments/templates/payments/dashboard.html` - Dashboard template
- `payments/templatetags/payment_filters.py` - Custom template filters
- `payments/urls.py` - URL routing for the dashboard
- `payments_dashboard_mini/urls.py` - Main URL configuration

## Testing

You can test the queries independently using:

```bash
python test_queries.py
```

This will verify that both Django ORM and SQLAlchemy queries work correctly. 