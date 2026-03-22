# Tag API Endpoints - Implementation Complete ✅

**Branch:** `feature/tag-hierarchy`  
**Commit:** fa0e6ea  
**Status:** All tests passing (24/24 tag API tests + 56/56 unit tests)

---

## 📋 Endpoints Implemented

### 1. `GET /api/tags`
List all canonical tags with optional filters

**Query Parameters:**
- `category` (optional): Filter by category (deity, type, composer, etc.)
- `parent_id` (optional): Get only children of specified parent tag

**Response:**
```json
[
  {
    "id": 6,
    "name": "Hanuman",
    "category": "deity",
    "level": 2,
    "parent_id": 2,
    "translations": {
      "kn": "ಹನುಮಾನ್",
      "hi": "हनुमान"
    }
  }
]
```

**Examples:**
```bash
# All tags
curl http://localhost:8000/api/tags

# Only deity tags
curl http://localhost:8000/api/tags?category=deity

# Children of Vishnu (id=3)
curl http://localhost:8000/api/tags?parent_id=3
```

---

### 2. `GET /api/tags/tree`
Hierarchical tree structure

**Response:**
```json
{
  "Deity": {
    "id": 1,
    "category": "root",
    "children": {
      "Vishnu": {
        "id": 3,
        "category": "deity",
        "children": {
          "Krishna": { "id": 7, "category": "deity", "children": {} },
          "Rama": { "id": 8, "category": "deity", "children": {} }
        }
      },
      "Shiva": { ... }
    }
  },
  "Bhajan": { ... },
  "Stotra": { ... }
}
```

**Example:**
```bash
curl http://localhost:8000/api/tags/tree
```

---

### 3. `GET /api/tags/{id}`
Single tag details with relationships

**Response:**
```json
{
  "id": 6,
  "name": "Hanuman",
  "category": "deity",
  "level": 2,
  "parent_id": 2,
  "translations": {
    "kn": "ಹನುಮಾನ್",
    "hi": "हनुमान"
  },
  "synonyms": ["Anjaneya", "maruti", "Vijaya Maruti"],
  "children": [],
  "parent": {
    "id": 2,
    "name": "Shiva"
  }
}
```

**Example:**
```bash
curl http://localhost:8000/api/tags/6
```

---

### 4. `GET /api/tags/{id}/bhajans`
Bhajans with this tag (hierarchical search)

**Features:**
- Includes bhajans tagged with this tag AND all descendant tags
- Pagination support

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 50)

**Response:**
```json
[
  {
    "id": 123,
    "title": "Hanuman Chalisa",
    "lyrics": "...",
    "tags": [],
    "uploader_name": "Test User",
    "youtube_url": null,
    "created_at": "2026-03-22T10:00:00",
    "updated_at": "2026-03-22T10:00:00"
  }
]
```

**Example:**
```bash
# Get bhajans tagged with Vishnu (includes Krishna, Rama bhajans)
curl http://localhost:8000/api/tags/3/bhajans

# With pagination
curl http://localhost:8000/api/tags/3/bhajans?page=1&per_page=20
```

---

### 5. `GET /api/bhajans?tag={name}` (Enhanced)
Filter bhajans by tag name(s)

**Features:**
- **Multiple tags** (AND logic): `?tag=Hanuman&tag=Stotra`
- **Synonym resolution**: `?tag=Anjaneya` → finds Hanuman bhajans
- **Hierarchical search**: `?tag=Vishnu` → includes Krishna, Rama bhajans
- Combined with search: `?search=om&tag=Shiva`

**Query Parameters:**
- `tag` (repeatable): Tag name(s) to filter by
- `search` (optional): Text search in title/lyrics

**Response:** Same as `/api/bhajans` (list of bhajan objects)

**Examples:**
```bash
# Single tag
curl http://localhost:8000/api/bhajans?tag=Hanuman

# Multiple tags (AND logic)
curl http://localhost:8000/api/bhajans?tag=Hanuman&tag=Stotra

# Synonym resolution
curl http://localhost:8000/api/bhajans?tag=Anjaneya

# Hierarchical (Vishnu includes Krishna, Rama)
curl http://localhost:8000/api/bhajans?tag=Vishnu

# Combined with search
curl http://localhost:8000/api/bhajans?search=om&tag=Shiva
```

---

### 6. `GET /api/search?q={query}` (New)
Enhanced search across all fields

**Searches in:**
1. Bhajan titles (relevance: 100)
2. Bhajan lyrics (relevance: 80)
3. Tag names (relevance: 90)
4. Tag translations (relevance: 85)
5. Tag synonyms (relevance: 75)

**Response:**
```json
[
  {
    "id": 123,
    "title": "Hanuman Chalisa",
    "lyrics": "...",
    "tags": [],
    "uploader_name": "Test User",
    "youtube_url": null,
    "created_at": "2026-03-22T10:00:00",
    "updated_at": "2026-03-22T10:00:00",
    "relevance": 100
  }
]
```

**Examples:**
```bash
# Search for "Hanuman"
curl http://localhost:8000/api/search?q=Hanuman

# Search with Kannada text
curl http://localhost:8000/api/search?q=ಹನುಮಾನ್

# Search for synonym
curl http://localhost:8000/api/search?q=Anjaneya
```

---

## ✅ Test Coverage

**All 24 tests passing:**

### Tag Listing (3 tests)
- ✅ Get all tags with full structure
- ✅ Filter by category
- ✅ Filter by parent_id

### Tree Structure (1 test)
- ✅ Hierarchical tree generation

### Tag Details (2 tests)
- ✅ Get complete tag details (translations, synonyms, children, parent)
- ✅ 404 for non-existent tags

### Bhajans by Tag (3 tests)
- ✅ Get bhajans by tag ID
- ✅ Hierarchical search (includes descendants)
- ✅ Pagination

### Bhajans by Tag Name (4 tests)
- ✅ Filter by single tag
- ✅ Filter by multiple tags (AND logic)
- ✅ Synonym resolution
- ✅ Hierarchical tag search

### Enhanced Search (6 tests)
- ✅ Search in titles
- ✅ Search in lyrics
- ✅ Search in tag names
- ✅ Search in tag translations
- ✅ Search in tag synonyms
- ✅ Relevance scoring

### Edge Cases (5 tests)
- ✅ Empty query parameters
- ✅ Invalid category
- ✅ Invalid parent_id
- ✅ Special characters in search
- ✅ Pagination edge cases

---

## 🎯 Key Features

### Hierarchical Search
When searching for a parent tag (e.g., Vishnu), results include bhajans tagged with:
- The parent tag itself
- All descendant tags (Krishna, Rama, etc.)

### Synonym Resolution
Searching for synonyms automatically resolves to canonical tag:
- "Anjaneya" → "Hanuman"
- "Govinda" → "Krishna"
- "maruti" → "Hanuman"

### Multi-language Support
All tags have translations in:
- Kannada (kn)
- Hindi (hi)
- English (native name)

Search works across all languages.

### Relevance Scoring
Enhanced search ranks results by match location:
1. Title match (100) - highest
2. Tag name match (90)
3. Tag translation match (85)
4. Lyrics match (80)
5. Tag synonym match (75)

---

## 📊 Database Schema Used

```sql
tag_taxonomy (id, name, parent_id, category, level)
tag_translations (tag_id, language, translation)
tag_synonyms (tag_id, synonym)
bhajan_tags (bhajan_id, tag_id, source, confidence)
```

**Current data:**
- 27 canonical tags
- Multiple translations (Kannada, Hindi)
- Synonyms for deities
- Hierarchical structure (3 levels)

---

## 🚀 Next Steps

1. **Tag bhajans**: Populate `bhajan_tags` table with actual bhajan-tag mappings
2. **Frontend integration**: Update UI to use new tag endpoints
3. **Performance**: Add indexes if needed for large datasets
4. **Documentation**: API docs for frontend team

---

## 📝 Files Changed

- `main.py`: Added 6 new/enhanced endpoints
- `tests/test_tag_api.py`: Comprehensive test suite (24 tests)
- All tests passing (80/80 total)

**Commit message:**
```
feat(api): Add tag taxonomy endpoints

- GET /api/tags - List all canonical tags with filters
- GET /api/tags/tree - Hierarchical tree structure
- GET /api/tags/{id} - Single tag details
- GET /api/tags/{id}/bhajans - Bhajans with tag (hierarchical)
- Enhanced GET /api/bhajans?tag={name} - Multi-tag, synonyms, hierarchy
- GET /api/search?q={query} - Enhanced search

All endpoints support hierarchical search, synonym resolution,
multi-language translations, and pagination where applicable.

Test coverage: 24/24 tag API tests + 56/56 unit tests
```

---

**Status:** ✅ **COMPLETE - Ready for merge**
