import requests
import json
import re
import logging
import base64
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
import re

from markdownify import markdownify

# Configure logging
logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)
def find_image_urls(text):
    # Pattern to match URLs starting with http/https and ending with image extensions
    pattern = r'https?://[^\s<>"]+?\.(?:jpg|jpeg|png|svg|gif)(?=\s|$)'
    
    # Find all matches
    matches = re.findall(pattern, text, re.IGNORECASE) or  []
    soup = BeautifulSoup(text, "html.parser")
    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("src")
        if img_url and "images/image_" not in img_url:
            matches.append(img_url)
        
    return matches
def fetch_html(url, output_dir):
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

        
        # Save raw HTML to a file
        raw_html_path = Path(output_dir) / "website.html"
        raw_html_path.parent.mkdir(parents=True, exist_ok=True)
        


        with open(raw_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)


        _log.info(f"HTML content fetched and saved to: {raw_html_path}")
        # _log.info(f"Markdown content saved to: {markdown_path}")
        
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
    


def extract_image_name(url):
    pattern = r"(?<=/)([^/]+\.(?:jpg|jpeg|png|svg|gif))$"
    match = re.search(pattern, url, re.IGNORECASE)
    return match.group(1) if match else None

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
                image_name=extract_image_name(img_url)or f"image_{image_counter}{image_extension}"
                print("if block",img_url,image_name)
                image_filename = images_dir / f"{image_name}"
                raw_html_path = Path(output_dir) / "website.html"
                with open(raw_html_path, "w", encoding="utf-8") as f:
                    replaced_content = html_content.replace(img_url, f"/images/{image_name}")
                    f.write(replaced_content)
                
                
                if save_data_url(img_url, image_filename):
                    image_counter += 1
                    _log.info(f"Data URL image saved: {img_url}")
            else:
                # Handle regular 
                print("else  befor change",img_url)
                if not img_url.startswith(("http://", "https://")):
                    img_url = urljoin(base_url, img_url)
                # print("img_url----------------",img_url)
                response = requests.get(img_url, headers=headers, stream=True)
                response.raise_for_status()

                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    extension = content_type.split('/')[-1].split(';')[0]
                    if not extension:
                        extension = 'jpg'
                else:
                    extension = Path(urlparse(img_url).path).suffix.lstrip('.') or 'jpg'
                image_name=extract_image_name(img_url)
                # print(image_name,"in elseblock")
                image_filename = images_dir / f"{image_name}"
                image_filename_url = images_dir / f"image_{image_counter}.{extension}"
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
    api_key = "jina_d872ad41e3f04d3eb17b2d227b4ff670r5jn_lTYEGQy1Ps10Ze3jZP9Raax"

    try:
        # Step 1: Fetch HTML content using both direct request and Jina
        html_path, html_content = fetch_html(url, output_dir)

        # Step 2: Extract images from HTML
        extract_images_from_html(html_content, output_dir, url)
        
        with open(html_path, "r", encoding="utf-8") as f:
            updated_html=f.read()

        replace_html(updated_html,output_dir)
        process_html_with_docling(html_path, output_dir)
        _log.info("HTML content successfully processed and saved.")
    except Exception as e:
        _log.error(f"An error occurred: {str(e)}")

def replace_html(html_content,output_dir):
    try:
                # # Find all image URLs and replace them with local paths
        list_urls = find_image_urls(html_content)
        print(list_urls)
        for img_url in list_urls:
            image_name = extract_image_name(img_url)
            if image_name:
                local_path = f"{output_dir}/images/{image_name}"
                # print("Local_path----------------",img_url,local_path)
                # Create img tag with local path
                img_tag = local_path
                # Replace URL in HTML content
                html_content = html_content.replace(img_url, img_tag)
                raw_html_path = Path(output_dir) / "website.html"
        with open(raw_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    except Exception as e:
        _log.warning(f"Failed to save data URL: {str(e)}")
        return False
    
def process_html_with_docling(input_html_path, output_dir):
    """Process HTML content with Docling and save as Markdown, JSON, and YAML."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    # Initialize DocumentConverter for HTML processing
    doc_converter = DocumentConverter(
        allowed_formats=[InputFormat.HTML]  # Restrict processing to HTML format
    )

    # Process the HTML file
    result = doc_converter.convert(input_html_path)

    if not result:
        _log.error("Failed to process the HTML file with Docling.")
        return

    # Save processed content in Markdown format
    markdown_path = output_dir / "website_content.md"
    with open(markdown_path, "w", encoding="utf-8") as f:
        # f.write(result.document.export_to_markdown())
        markdown=markdownify(html_content)
        markdown=markdown.replace("images/",f"{output_dir}/images/")
        f.write(markdown)
    _log.info(f"Processed content saved as Markdown: {markdown_path}")

     

if __name__ == "__main__":
    process_html_with_docling("test_output/website.html","test_output")