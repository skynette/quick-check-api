# Hacker News API

A RESTful API that synchronizes with Hacker News data and provides enhanced filtering, searching, and CRUD operations for news items. This API allows for exploring Hacker News content with improved search capabilities, while also supporting creation of local items not present in the official Hacker News.

## Live Demo

The API is hosted at:
```
https://quick-check.up.railway.app/api/
```

## Features

- **Synchronization with Hacker News API**: Regularly syncs with the official Hacker News API
- **Comprehensive filtering**: Filter by item type, author, status, and more
- **Full-text search**: Search across titles, text, and authors
- **Pagination**: Browse through large result sets with ease
- **Top-level filtering**: Focus on main stories without comments
- **CRUD operations**: Create, read, update, and delete local items
- **Protection for HN data**: Prevents modification of data from the official Hacker News API
- **Manual sync trigger**: Force a sync with the latest HN items when needed

## API Endpoints

### List and Create Items
```
GET /api/items/
POST /api/items/
```

#### GET Parameters
- `type`: Filter by item type (story, comment, job, poll, pollopt)
- `by`: Filter by author
- `dead`: Filter by dead/removed status (true/false)
- `created_locally`: Filter by origin (true/false)
- `top_level`: Show only top-level items (true/false)
- `search`: Search in title, text, and author fields
- `ordering`: Order by time, score, descendants, or item_id (add - for descending)
- `page`: Page number for pagination

#### POST Parameters
- `type`: Item type (required)
- `by`: Author username (required)
- `title`: Item title (required for stories)
- `text`: Item content
- `url`: URL (for stories with external links)
- `score`: Numeric score

### Item Details, Update, and Delete
```
GET /api/items/{item_id}/
PUT /api/items/{item_id}/
PATCH /api/items/{item_id}/
DELETE /api/items/{item_id}/
```

### Trigger Sync
```
POST /api/sync/
```

#### POST Parameters
- `count`: Number of items to sync (default: 100)

## Usage Examples

### List all stories
```bash
curl -X GET "https://quick-check.up.railway.app/api/items/?type=story"
```

### Search for Python-related content
```bash
curl -X GET "https://quick-check.up.railway.app/api/items/?search=python"
```

### Get top-scored stories
```bash
curl -X GET "https://quick-check.up.railway.app/api/items/?type=story&ordering=-score"
```

### Create a new local item
```bash
curl -X POST "https://quick-check.up.railway.app/api/items/" \
  -H "Content-Type: application/json" \
  -d '{"type": "story", "by": "localuser", "title": "My Local Story", "text": "This is a test story."}'
```

### Update a local item
```bash
curl -X PATCH "https://quick-check.up.railway.app/api/items/10000001/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

### Trigger a manual sync
```bash
curl -X POST "https://quick-check.up.railway.app/api/sync/" \
  -H "Content-Type: application/json" \
  -d '{"count": 50}'
```

## Running the API Test Script

A comprehensive test script is provided to verify all API functionality. The script checks all endpoints and verifies they meet the specified criteria.

### Installation
```bash
pip install requests
```

### Usage
```bash
python test_script.py
```

### What the Test Script Checks

1. **List Items Endpoint**
   - Basic listing functionality
   - Pagination
   - Filtering by type
   - Filtering by top-level status
   - Search functionality
   - Combined filters
   - Ordering

2. **Item Detail Endpoint**
   - Retrieval of item details
   - Comment inclusion

3. **Create Item Endpoint**
   - Creation of local items
   - Verification of created_locally flag

4. **Update Item Endpoint**
   - Partial updates (PATCH)
   - Full updates (PUT)

5. **Delete Item Endpoint**
   - Deletion of local items
   - Verification of deletion

6. **HN Item Protection**
   - Prevention of HN item updates
   - Prevention of HN item deletion

7. **Sync Endpoint**
   - Manual sync triggering
   - Verification of data changes

## Implementation Details

The API is built using:
- Django and Django REST Framework
- APScheduler for regular synchronization with Hacker News
- PostgreSQL for data storage
- Django Filter for advanced filtering options

The system maintains a distinction between items retrieved from Hacker News (read-only) and items created locally through the API (fully editable).