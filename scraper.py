# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests",
#   "beautifulsoup4", 
#   "pandas"
# ]
# ///
import argparse
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# --- Global Configuration ---
BASE_MICHELIN_URL = "https://guide.michelin.com"

DISTINCTION_PATHS = {
    "1 Star": "1-star-michelin",
    "2 Stars": "2-stars-michelin",
    "3 Stars": "3-stars-michelin",
    "The Plate Michelin": "the-plate-michelin",
    "Bib Gourmand": "bib-gourmand"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_restaurant_detail(detail_url, michelin_rating_type_from_listing):
    """
    Fetches and parses a single restaurant's detail page, primarily using JSON-LD data.
    Extracts name, full address, cuisine type, price range, etc.
    """
    print(f"  Fetching details for: {detail_url}")
    try:
        detail_response = requests.get(detail_url, headers=HEADERS, timeout=10)
        detail_response.raise_for_status()

        detail_soup = BeautifulSoup(detail_response.text, "html.parser")

        json_ld_script = detail_soup.find("script", type="application/ld+json")
        
        if json_ld_script:
            json_data = json.loads(json_ld_script.string)

            name = json_data.get("name", "N/A")
            
            address_obj = json_data.get("address", {})
            street_address = address_obj.get("streetAddress", "N/A")
            address_locality = address_obj.get("addressLocality", "N/A")
            postal_code = address_obj.get("postalCode", "N/A")
            address_country = address_obj.get("addressCountry", "N/A")
            
            full_address = f"{street_address}, {address_locality}, {postal_code}, {address_country}".replace("N/A, ", "").replace(", N/A", "").strip()
            
            cuisine_type = json_data.get("servesCuisine", "N/A")
            price_range_text = json_data.get("priceRange", "N/A")

            latitude = json_data.get("latitude", None)
            longitude = json_data.get("longitude", None)

            review_info = json_data.get("review", "N/A")

            award_info = json_data.get("award", "N/A")

            city_extracted = address_locality


            return {
                "Restaurant Name": name,
                "Full Address": full_address,
                "City": city_extracted,
                "Michelin Rating": michelin_rating_type_from_listing,
                "Price Range Text": price_range_text,
                "Cuisine Type": cuisine_type,
                "URL": detail_url,
                "Latitude": latitude,
                "Longitude": longitude,
                "Review": review_info,
                "Award": award_info
            }

        else:
            print(f"  Warning: No application/ld+json script found for {detail_url}. Falling back to old parsing (if implemented or N/A).")
            return {
                "Restaurant Name": "N/A",
                "Full Address": "N/A",
                "City": "N/A",
                "Michelin Rating": michelin_rating_type_from_listing,
                "Price Range Text": "N/A",
                "Cuisine Type": "N/A",
                "URL": detail_url,
                "Latitude": None,
                "Longitude": None,
                "Review": "N/A",
                "Award": "N/A"
            }

    except requests.exceptions.RequestException as e:
        print(f"  Error fetching detail page {detail_url}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"  Error decoding JSON-LD for {detail_url}: {e}")
        return None
    except Exception as e:
        print(f"  An unexpected error occurred while processing {detail_url}: {e}")
        return None
    finally:
        time.sleep(random.uniform(0.5, 1.5))

def get_listing_info_and_urls(base_listing_url, michelin_rating_name, city_region):
    """
    Fetches Michelin Guide listing pages (including pagination) for a specific distinction.
    Extracts basic info and detail page URLs for each restaurant.
    Determines total pages by finding highest page number in pagination links.
    """
    print(f"\n--- Processing listing pages for: {michelin_rating_name} ---")
    print(f"Base Listing URL: {base_listing_url}")
    
    listing_restaurants_info = []
    
    max_page = 1
    current_page = 1

    print(f"  Fetching initial page to find total pagination: {base_listing_url}")
    try:
        response = requests.get(base_listing_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        pagination_ul = soup.find("ul", class_="pagination")
        if pagination_ul:
            page_links = pagination_ul.find_all("a", href=True)
            for link in page_links:
                href = link['href']
                if "/page/" in href:
                    try:
                        page_num_str = href.split("/page/")[-1]
                        page_num = int(page_num_str)
                        if page_num > max_page:
                            max_page = page_num
                    except ValueError:
                        continue
        
        if max_page > 1:
            print(f"  Detected {max_page} total pages for {michelin_rating_name}.")
        else:
            print(f"  No clear pagination detected or only one page for {michelin_rating_name}. Proceeding with page 1 only.")
            
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching initial page {base_listing_url}: {e}")
        print("  Cannot determine pagination. Proceeding with page 1 only if possible.")
        raise e
    except Exception as e:
        print(f"  An unexpected error occurred while detecting pagination for {base_listing_url}: {e}")
        raise e

    while current_page <= max_page:
        listing_url = f"{base_listing_url}/page/{current_page}" if current_page > 1 else base_listing_url
        print(f"  Processing page {current_page}/{max_page} ({listing_url})")

        try:
            if current_page > 1:
                 response = requests.get(listing_url, headers=HEADERS, timeout=10)
                 response.raise_for_status()
                 soup = BeautifulSoup(response.text, "html.parser")

            restaurant_cards = soup.find_all("div", class_="col-md-6 col-lg-4 col-xl-3")

            if not restaurant_cards:
                print(f"  No restaurant cards found on page {current_page}. This may be the end, or an issue.")
                if current_page == 1:
                    return []
                break
            
            print(f"  Found {len(restaurant_cards)} restaurants on page {current_page}.")

            for i, card in enumerate(restaurant_cards):
                name_h3_tag = card.find("h3", class_="card__menu-content--title")
                name_a_tag = name_h3_tag.find("a", href=True) if name_h3_tag else None

                name = name_a_tag.text.strip() if name_a_tag else "N/A"
                relative_url = name_a_tag['href'] if name_a_tag and 'href' in name_a_tag.attrs else None
                full_detail_url = BASE_MICHELIN_URL + relative_url if relative_url else "N/A"
                
                if full_detail_url != "N/A" and "restaurant" in full_detail_url and f"/{city_region}/" in full_detail_url:
                    listing_restaurants_info.append(
                        {
                            "Restaurant Name (Listing)": name,
                            "Michelin Rating (Listing)": michelin_rating_name,
                            "Detail URL": full_detail_url
                        }
                    )
                else:
                    print(f"    Skipping non-relevant or malformed link: {full_detail_url} (from card {i+1}, name: {name})")
            
            current_page += 1

        except requests.exceptions.HTTPError as e:
            print(f"  HTTP Error {e.response.status_code} for {listing_url}: {e}")
            break
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching listing page {listing_url}: {e}")
            break
        except Exception as e:
            print(f"  An unexpected error occurred for listing page {listing_url}: {e}")
            break
        finally:
            # Polite delay after each listing page request
            time.sleep(random.uniform(2, 5))

    print(f"Collected {len(listing_restaurants_info)} valid restaurant entries across all pages for {michelin_rating_name}.")
    return listing_restaurants_info

# --- Main Scraper Orchestration ---
def main_scraper(region, country_code):
    """
    Orchestrates the entire scraping process.
    Iterates through distinctions, gets listing info, then scrapes detail pages.
    """
    all_final_restaurant_data = []
    
    for rating_name, rating_path in DISTINCTION_PATHS.items():
        listing_url = f"{BASE_MICHELIN_URL}/en/{country_code}/{region}/restaurants/{rating_path}"
        
        listing_info = get_listing_info_and_urls(listing_url, rating_name, region)
        
        if listing_info:
            print(f"  Starting detail page scraping for {len(listing_info)} restaurants in {rating_name} category...")
            for restaurant_basic_info in listing_info:
                detail_url = restaurant_basic_info["Detail URL"]
                michelin_rating_from_listing = restaurant_basic_info["Michelin Rating (Listing)"]
                
                detailed_data = scrape_restaurant_detail(detail_url, michelin_rating_from_listing)
                if detailed_data:
                    all_final_restaurant_data.append(detailed_data)
        else:
            print(f"  No restaurant detail URLs found for {rating_name}. Skipping detail scrape for this category.")

    if all_final_restaurant_data:
        df_final = pd.DataFrame(all_final_restaurant_data)
        df_final = df_final[
            [
                "Restaurant Name",
                "Full Address",
                "City",
                "Michelin Rating",
                "Price Range Text",
                "Cuisine Type",
                "URL",
                "Latitude",
                "Longitude",
                "Review",
                "Award"
            ]
        ]
        df_final.to_csv(f"michelin_restaurants_full_data_{region}.csv", index=False, encoding="utf-8")
        print(f"\n--- Scraping Complete ---")
        print(f"Successfully scraped {len(df_final)} restaurants and saved to michelin_restaurants_full_data_{region}.csv")
        print("\nFirst 5 rows of the final scraped data:")
        print(df_final.head())
    else:
        print("\n--- Scraping Complete ---")
        print("No restaurant data was scraped. Please check your configuration, URLs, and selectors.")

# --- Run the scraper ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Michelin Guide restaurants")
    parser.add_argument("--region", type=str, default="greater-london", help="Region to scrape")
    parser.add_argument("--country", type=str, default="gb", help="Country code")
    args = parser.parse_args()
    main_scraper(args.region, args.country)