# SadSat Backend

A FastAPI backend service for scraping and managing SAT (Servicio de Administración Tributaria) product and service catalogs.

## Quick Start

### Development Setup

1. **Start both backend and frontend services:**

   ```bash
   make up
   ```

   This will:

   - Build and run the backend Docker container on port 8080
   - Install frontend dependencies and start the dev server

2. **Alternative: Start services individually:**

   ```bash
   # Backend only
   make back

   # Frontend only
   make front
   ```

3. **Access the services:**
   - Backend API: http://localhost:8080
   - Frontend: http://localhost:5173 (or port shown in terminal)

### Other Useful Commands

```bash
# Restart backend container
make restart_back

# View backend logs
make logs

# Open terminal in backend container
make terminal

# Clean up Docker resources
make clean

# Run backend in debug mode
make debug

# Run linter
make lint
```

## Catalog Scraping System

The backend implements two approaches for pulling SAT catalog data:

### 1. Traditional Excel Download (Legacy)

- **Endpoint:** `POST /pull_catalogo/{date_str}`
- **Method:** Downloads Excel files from SAT's official site
- **Status:** File download is currently locked behind an auth layer

### 2. PYS Web Scraping (Current)

- **Endpoint:** `POST /pull_pys_catalog`
- **Method:** Scrapes the SAT PYS unsecured website (http://pys.sat.gob.mx/PyS/catPyS.aspx)
- **Data Structure:** 4-level hierarchy (Type → Segment → Family → Class)
- **Output Files:**
  - `pys_catalog_latest.json` (raw hierarchical data and metadata)
  - `pys_flattened_latest.json` (flattened for database import)

## API Endpoints

### Health & Status

- `GET /` - Root endpoint with timestamp
- `GET /health` - Health check
- `GET /show_latest` - Show latest pulled data, now fetches pys files

### Catalog Management

- `POST /pull_pys_catalog` - Scrape complete PYS catalog
- `GET /test_pys_scraper` - Test basic scraper functionality
- `GET /cleanup_pys_files` - Clean up old catalog files
- `POST /pull_catalogo/{date_str}` - Legacy Excel download method

### Database Operations

- `GET /load_db` - Load latest catalog data into database
- `GET /search_clave_prod_and_taxonomy?q={query}` - Search products and taxonomy

### Data Management

- `GET /pull_taxonomy` - Trigger taxonomy data pull
- `GET /load_db` - Load data into database

### File Management

- **Latest Files Only:** The system maintains only the most recently pulled catalog files
- **Automatic Cleanup:** Old timestamped files are automatically removed
- **Fixed Filenames:**
  - Raw data: `pys_catalog_latest.json`
  - Flattened data: `pys_flattened_latest.json`

## Development

### Linting with Ruff

The project uses Ruff for code quality:

```bash
# Check code
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .

# Run via Makefile
make lint
```

## Architecture

- **Framework:** FastAPI
- **Database:** SQLite with SQLAlchemy ORM
- **Scraping:** BeautifulSoup + Requests
- **Containerization:** Docker
- **Data Processing:** Pandas for Excel/Parquet handling
