# Profile Intelligence API ⚡

A Django REST API that generates intelligent demographic profiles by analyzing names using external prediction services.

---

## Overview

The Profile Intelligence API automatically enriches profile data by querying multiple external demographic prediction services:

- **[Genderize.io](https://genderize.io)** – Predicts gender and probability
- **[Agify.io](https://agify.io)** – Estimates age from name
- **[Nationalize.io](https://nationalize.io)** – Predicts country of origin

---

## Features

- ✅ Create profiles with automatic demographic enrichment
- 🔍 Search profiles by name, gender, country, or age group
- 📊 Order results by creation date, name, age, or gender
- 🔑 UUID v7 primary keys for modern, sortable IDs
- 🗄️ PostgreSQL database with SSL mode
- 📡 RESTful API with standardized response format
- 🔄 Filter backends for advanced queries

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Django 6.0.4 |
| API | Django REST Framework |
| Database | PostgreSQL |
| ID Generator | UUID v7 |
| Env Config | python-dotenv |

---

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL database
- Virtual environment (recommended)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/owoaanu/hng14_stage_one.git
   cd hng14_stage_one
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install django djangorestframework python-dotenv requests django-cors-headers
   ```

4. **Configure environment variables:**
   
   Create a `.env` file in the project root:
   ```bash
   DB_NAME=your_database_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=5432
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/api/profiles/` | Create a new profile |
| **GET** | `/api/profiles/` | List all profiles |
| **GET** | `/api/profiles/{id}/` | Retrieve a single profile |
| **DELETE** | `/api/profiles/{id}/` | Delete a profile |

---

## Usage Examples

### Create a Profile

```bash
curl -X POST http://localhost:8000/api/profiles/ \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe"}'
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "019eb8f6-5f7c-7a8b-b9c0-d1e2f3a4b5c6",
    "name": "John Doe",
    "gender": "male",
    "gender_probability": 0.99,
    "age": 45,
    "age_group": "adult",
    "country_id": "US",
    "country_probability": 0.15,
    "sample_size": 1500,
    "created_at": "2026-04-18T22:45:00Z"
  }
}
```

### List Profiles

```bash
curl "http://localhost:8000/api/profiles/"
```

**Response:**
```json
{
  "status": "success",
  "count": 25,
  "data": [
    {
      "id": "019eb8f6-5f7c-7a8b-b9c0-d1e2f3a4b5c6",
      "name": "John Doe",
      "gender": "male",
      "age": 45,
      "age_group": "adult",
      ...
    }
  ]
}
```

### Search Profiles

```bash
# Search by name
curl "http://localhost:8000/api/profiles/?search=john"

# Search by country
curl "http://localhost:8000/api/profiles/?search=US"

# Filter by age group
curl "http://localhost:8000/api/profiles/?age_group=adult"

# Sort by age ascending
curl "http://localhost:8000/api/profiles/?ordering=age"

# Sort by creation date (newest first)
curl "http://localhost:8000/api/profiles/?ordering=-created_at"
```

---

## Data Model

### Profile Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID v7 | Primary key, auto-generated |
| `name` | String | Profile name (indexed) |
| `gender` | String | Predicted gender (male/female/null) |
| `gender_probability` | Float | Confidence score (0-1) |
| `age` | Integer | Predicted age |
| `age_group` | String | Classified group: child/teenager/adult/senior |
| `country_id` | String | ISO country code |
| `country_probability` | Float | Country confidence score |
| `sample_size` | Integer | Dataset size from genderize.io |
| `created_at` | DateTime | Creation timestamp |

### Age Group Classification

| Age Range | Group |
|-----------|-------|
| 0-12 | `child` |
| 13-19 | `teenager` |
| 20-59 | `adult` |
| 60+ | `senior` |

---

## Project Structure

```
hng14_stage_one/
├── hng14_stage_one/          # Project config
│   ├── __init__.py
│   ├── settings.py           # Django settings
│   ├── urls.py               # Root URL config
│   ├── wsgi.py
│   └── asgi.py
├── profile_intelligence/     # Main application
│   ├── admin.py
│   ├── apps.py
│   ├── models.py             # Profile model
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # API viewsets
│   ├── urls.py               # App URLs
│   └── migrations/
├── .env                      # Environment variables
├── .gitignore
├── manage.py
└── README.md
```

---

## Error Handling

The API returns consistent JSON error responses:

```json
{
  "status": "error",
  "message": "Error description here"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Server Error |

---

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | Database username |
| `DB_PASSWORD` | Database password |
| `DB_HOST` | Database host |
| `DB_PORT` | Database port (default: 5432) |

### Security Notes

- `SECRET_KEY`: Change for production deployments
- `DEBUG`: Set to `False` in production
- `CORS_ALLOW_ALL_ORIGINS`: Configure appropriately for production

---

## External Dependencies

| Service | Purpose |
|---------|---------|
| https://api.genderize.io | Gender prediction |
| https://api.agify.io | Age estimation |
| https://api.nationalize.io | Nationality prediction |

> ⚠️ These services are rate-limited. For production use, consider caching results or using paid tiers.

---

## API Features

### Filtering & Search

- **Search**: Query by name, gender, country_id, or age_group
- **Ordering**: Sort by `created_at`, `name`, `age`, `gender`
- Use `-` prefix for descending order (e.g., `-created_at`)

### Sample Queries

```bash
# Find adults named "John"
curl "http://localhost:8000/api/profiles/?search=john&age_group=adult"

# Get all profiles sorted by age descending
curl "http://localhost:8000/api/profiles/?ordering=-age"

# Search US profiles
curl "http://localhost:8000/api/profiles/?search=US"
```

---

## License

This project is part of the HNG Internship Stage One task.
