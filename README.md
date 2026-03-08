# Order Service

REST API for order management.

## Features
- Order creation and tracking
- Order status management
- Order history
- Order cancellation

## API Endpoints

### GET /health
Health check endpoint

### GET /api/orders
Get all orders

### GET /api/orders/{id}
Get specific order by ID

### POST /api/orders
Create new order
```json
{
  "customer_email": "customer@example.com",
  "total_amount": 99.99,
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "price": 49.99
    }
  ]
}
```

### PATCH /api/orders/{id}/status
Update order status
```json
{
  "status": "shipped"
}
```

### DELETE /api/orders/{id}
Cancel order (only pending orders)

## Order Status Flow
- `pending` - Initial state
- `processing` - Order being prepared
- `shipped` - Order shipped
- `delivered` - Order delivered
- `cancelled` - Order cancelled

## Setup
```bash
pip install -r requirements.txt
```

## Environment Variables
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)
- `DB_NAME` - Database name (default: ecommerce)
- `DB_USER` - Database user (default: postgres)
- `DB_PASSWORD` - Database password (default: postgres)

## Run
```bash
python app.py
```

Service runs on port 5002
