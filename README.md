# Michelin Guide Restaurant Scraper

A Python script that scrapes restaurant data from the Michelin Guide website. It extracts restaurant names, addresses, ratings, cuisine types, and other details for restaurants in a specified region.

## What it does

This scraper:
- Fetches restaurant listings from Michelin Guide for different rating categories (Bib Gourmand, 1 Star, 2 Stars, 3 Stars, The Plate Michelin)
- Extracts detailed information from each restaurant's page including:
  - Restaurant name
  - Full address
  - City
  - Michelin rating
  - Price range
  - Cuisine type
  - Restaurant URL
  - Latitude/Longitude (if available)
- Saves all data to a CSV file for analysis

## Prerequisites

You need to install `uv` (a fast Python package manager) to run this script.

### Installing uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative methods:**
- Using pip: `pip install uv`
- Using Homebrew: `brew install uv`

## Running the scraper using uv run

```bash
# Use defaults (Greater London, UK)
uv run scraper.py

# Specify a different region and country
uv run scraper.py --region "new-york-state" --country "us"
uv run scraper.py --region "ile-de-france" --country "fr"
```

This will:
1. Automatically install the required dependencies (`requests`, `beautifulsoup4`, `pandas`)
2. Run the scraper in an isolated environment
3. Save results to `michelin_restaurants_full_data_{region}.csv`


## Configuration

The script accepts command-line arguments to specify the region and country:

```bash
uv run scraper.py --region "greater-london" --country "gb"
```

**Default values**: If no arguments are provided, it defaults to Greater London, UK.


## Output

The script generates a CSV file named `michelin_restaurants_full_data_{region}.csv` containing:
- Restaurant Name
- Full Address  
- City
- Michelin Rating
- Price Range Text
- Cuisine Type
- URL
- Latitude
- Longitude
- Review
- Award

## Dependencies

The script automatically installs these packages via uv:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `pandas` - Data manipulation and CSV export

## Notes

- The script includes polite delays between requests to avoid overwhelming the server
- It uses JSON-LD structured data when available for more reliable data extraction
- The script defaults to Greater London, UK but can be configured via command-line arguments

## Performance & Etiquette

**Important**: This script is intentionally slow due to built-in delays (0.5-1.5 seconds between detail page requests, 2-5 seconds between listing pages). This is by design to:

- Be respectful to the Michelin Guide servers
- Avoid being blocked or rate-limited
- Follow web scraping best practices
