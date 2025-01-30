import os
import requests
# import json
# import yaml
import logging
import base64
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

def fetch_html(url, output_dir, api_key):
    """Fetch HTML content from a URL using Jina API and save it to a file."""
    direct_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    try:
        # Direct request to get raw HTML
        response = requests.get(url, headers=direct_headers)
        response.raise_for_status()
        html_content = response.text

        # Get Jina's processed version for the markdown
        base_url = "https://r.jina.ai/"
        jina_headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        params = {
            "content_format": "markdown",
            "token_budget": 200000,
            "timeout": 10
        }

        jina_response = requests.get(
            f"{base_url}{url}",
            headers=jina_headers,
            params=params
        )
        jina_response.raise_for_status()
        
        # Save raw HTML to a file
        raw_html_path = Path(output_dir) / "website.html"
        raw_html_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(raw_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Save Jina's markdown directly
        markdown_path = Path(output_dir) / "website_content.md"
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(jina_response.text)

        _log.info(f"HTML content fetched and saved to: {raw_html_path}")
        _log.info(f"Markdown content saved to: {markdown_path}")
        
        return raw_html_path, html_content

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch {url}. Error: {str(e)}")

def is_data_url(url):
    """Check if the URL is a data URL."""
    return url.startswith('data:')

def save_data_url(data_url, output_path):
    """Save a data URL to a file."""
    try:
        # Extract the data part
        header, data = data_url.split(',', 1)
        
        # Handle base64 encoded data
        if 'base64' in header:
            file_data = base64.b64decode(data)
        else:
            file_data = data.encode('utf-8')
            
        with open(output_path, 'wb') as f:
            f.write(file_data)
            
        return True
    except Exception as e:
        _log.warning(f"Failed to save data URL: {str(e)}")
        return False

def extract_images_from_html(html_content, output_dir, base_url):
    """Extract and download images from the HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")
    images_dir = Path(output_dir) / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": base_url
    }

    image_counter = 0
    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("src")
        if not img_url:
            continue

        try:
            if is_data_url(img_url):
                # Handle data URLs
                image_extension = ".svg" if "svg+xml" in img_url else ".png"
                image_filename = images_dir / f"image_{image_counter}{image_extension}"
                if save_data_url(img_url, image_filename):
                    image_counter += 1
                    _log.info(f"Data URL image saved: {image_filename}")
            else:
                # Handle regular URLs
                if not img_url.startswith(("http://", "https://")):
                    img_url = urljoin(base_url, img_url)

                response = requests.get(img_url, headers=headers, stream=True)
                response.raise_for_status()

                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    extension = content_type.split('/')[-1].split(';')[0]
                    if not extension:
                        extension = 'jpg'
                else:
                    extension = Path(urlparse(img_url).path).suffix.lstrip('.') or 'jpg'

                image_filename = images_dir / f"image_{image_counter}.{extension}"
                with open(image_filename, "wb") as img_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            img_file.write(chunk)
                image_counter += 1
                _log.info(f"Image saved: {image_filename}")

        except Exception as e:
            _log.warning(f"Failed to download image: {img_url}. Error: {e}")

    if image_counter == 0:
        _log.info("No images found in the HTML content.")
    else:
        _log.info(f"{image_counter} images downloaded.")

def main():
    # Configuration
    url = "https://sreenidhi.edu.in/" 
    output_dir = "test_output"
    api_key = "jina_f1478928aeae4272a020bb08046e1217eDIBRE9huqGkOvNwAkuBDgKytl3q"

    try:
        # Step 1: Fetch HTML content using both direct request and Jina
        html_path, html_content = fetch_html(url, output_dir, api_key)

        # Step 2: Extract images from HTML
        extract_images_from_html(html_content, output_dir, url)

        _log.info("HTML content successfully processed and saved.")
    except Exception as e:
        _log.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()