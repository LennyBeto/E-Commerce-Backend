# E-Commerce Product API

A production-ready RESTful API for managing e-commerce products, built with **Django** and **Django REST Framework**. Features full CRUD operations, JWT authentication, product search, filtering, pagination, and is deployed on **Render**.

---

## Live Demo

**Base URL:** `https://e-commerce-backend-xxxx.onrender.com/api/v1/`

> Replace with your actual Render URL after deployment.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Deployment](#deployment)
- [Running Tests](#running-tests)

---

## Features

- **Product Management** — Full CRUD for products with validation
- **User Management** — Register, login, update, delete users
- **JWT Authentication** — Secure token-based auth (access + refresh tokens)
- **Product Search** — Search by name or category with partial matching
- **Filtering** — Filter by category, price range, and stock availability
- **Pagination** — Cursor-based pagination on all list endpoints
- **Category Management** — Dynamic category CRUD
- **Product Reviews** — Submit and retrieve product reviews _(stretch goal)_
- **Wishlist** — Add/remove products from personal wishlist _(stretch goal)_

---

## 🛠 Tech Stack

| Layer        | Technology                                   |
| ------------ | -------------------------------------------- |
| Language     | Python 3.11                                  |
| Framework    | Django 4.2, Django REST Framework 3.14       |
| Database     | PostgreSQL (prod), SQLite (dev)              |
| Auth         | Simple JWT (`djangorestframework-simplejwt`) |
| Filtering    | `django-filter`                              |
| Deployment   | Render                                       |
| Static Files | WhiteNoise                                   |
| CORS         | `django-cors-headers`                        |

---

## 🗂 Project Structure

```
E-Commerce-Backend/
├── ecommerce/                  # Django project config
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py             # Shared settings
│   │   ├── development.py      # Dev overrides
│   │   └── production.py       # Prod overrides
│   ├── urls.py
│   └── wsgi.py
├── products/                   # Products app
│   ├── migrations/
│   ├── models.py               # Product, Category models
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── filters.py
│   └── tests.py
├── users/                      # Users app
│   ├── migrations/
│   ├── models.py               # Custom user model
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── core/                       # Shared utilities
│   ├── pagination.py
│   └── permissions.py
├── manage.py
├── requirements.txt
├── Procfile                    # Render/Heroku process file
├── render.yaml                 # Render deployment config
└── .env.example
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (optional for local dev; SQLite works fine)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/LennyBeto/E-Commerce-Backend.git
cd E-Commerce-Backend
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your values
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. (Optional) Load Sample Data

```bash
python manage.py loaddata fixtures/sample_data.json
```

### 8. Start the Development Server

```bash
python manage.py runserver
```

API is now live at `http://127.0.0.1:8000/api/v1/`

---

## Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-super-secret-django-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/ecommerce_db
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

---

## API Documentation

### Base URL

```
/api/v1/
```

### Auth Endpoints

| Method | Endpoint               | Description              | Auth |
| ------ | ---------------------- | ------------------------ | ---- |
| POST   | `/auth/register/`      | Register new user        | No   |
| POST   | `/auth/login/`         | Obtain JWT tokens        | No   |
| POST   | `/auth/token/refresh/` | Refresh access token     | No   |
| GET    | `/auth/me/`            | Get current user profile | Yes  |
| PUT    | `/auth/me/`            | Update user profile      | Yes  |
| DELETE | `/auth/me/`            | Delete user account      | Yes  |

### Product Endpoints

| Method | Endpoint            | Description                      | Auth |
| ------ | ------------------- | -------------------------------- | ---- |
| GET    | `/products/`        | List all products (paginated)    | No   |
| POST   | `/products/`        | Create a product                 | Yes  |
| GET    | `/products/{id}/`   | Retrieve product by ID           | No   |
| PUT    | `/products/{id}/`   | Full update product              | Yes  |
| PATCH  | `/products/{id}/`   | Partial update product           | Yes  |
| DELETE | `/products/{id}/`   | Delete product                   | Yes  |
| GET    | `/products/search/` | Search products by name/category | No   |

### Category Endpoints

| Method | Endpoint            | Description         | Auth |
| ------ | ------------------- | ------------------- | ---- |
| GET    | `/categories/`      | List all categories | No   |
| POST   | `/categories/`      | Create category     | Yes  |
| GET    | `/categories/{id}/` | Get category        | No   |
| PUT    | `/categories/{id}/` | Update category     | Yes  |
| DELETE | `/categories/{id}/` | Delete category     | Yes  |

### Review Endpoints (Stretch Goal)

| Method | Endpoint                  | Description          | Auth |
| ------ | ------------------------- | -------------------- | ---- |
| GET    | `/products/{id}/reviews/` | List product reviews | No   |
| POST   | `/products/{id}/reviews/` | Submit a review      | Yes  |

### Wishlist Endpoints (Stretch Goal)

| Method | Endpoint          | Description         | Auth |
| ------ | ----------------- | ------------------- | ---- |
| GET    | `/wishlist/`      | View wishlist       | Yes  |
| POST   | `/wishlist/`      | Add product to list | Yes  |
| DELETE | `/wishlist/{id}/` | Remove from list    | Yes  |

---

### Query Parameters

**Product listing & search support:**

| Param       | Type    | Example                 | Description                      |
| ----------- | ------- | ----------------------- | -------------------------------- |
| `search`    | string  | `?search=laptop`        | Full-text search (name/category) |
| `category`  | string  | `?category=Electronics` | Filter by category name          |
| `min_price` | decimal | `?min_price=100`        | Minimum price filter             |
| `max_price` | decimal | `?max_price=500`        | Maximum price filter             |
| `in_stock`  | bool    | `?in_stock=true`        | Show only in-stock items         |
| `ordering`  | string  | `?ordering=-price`      | Sort (prefix `-` for desc)       |
| `page`      | int     | `?page=2`               | Pagination                       |
| `page_size` | int     | `?page_size=20`         | Items per page (max 100)         |

---

### Sample Request & Response

**Create Product**

```http
POST /api/v1/products/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Wireless Headphones",
  "description": "Noise-cancelling Bluetooth headphones",
  "price": "129.99",
  "category": 1,
  "stock_quantity": 50,
  "image_url": "https://example.com/images/headphones.jpg"
}
```

```json
HTTP 201 Created
{
  "id": 7,
  "name": "Wireless Headphones",
  "description": "Noise-cancelling Bluetooth headphones",
  "price": "129.99",
  "category": {"id": 1, "name": "Electronics"},
  "stock_quantity": 50,
  "image_url": "https://example.com/images/headphones.jpg",
  "created_date": "2025-04-30T10:22:00Z",
  "in_stock": true
}
```

---

## Authentication

This API uses **JWT (JSON Web Tokens)**. Include the access token in the `Authorization` header for protected endpoints:

```
Authorization: Bearer <your_access_token>
```

Tokens expire after **60 minutes**. Use the refresh endpoint to obtain a new access token without re-logging in.

---

## Deployment

See the full deployment walkthrough in [`DEPLOYMENT.md`](./DEPLOYMENT.md).

**Quick deploy to Render:**

1. Push repo to GitHub
2. Connect repo in Render dashboard
3. Set environment variables
4. Deploy — Render auto-detects `render.yaml`

---

## Running Tests

```bash
python manage.py test
# or with coverage
pip install coverage
coverage run manage.py test
coverage report
```
