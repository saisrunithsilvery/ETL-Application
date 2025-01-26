import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import markdown
from urllib.parse import urljoin, urlparse

class WebScraper:
    def __init__(self, base_url, output_dir='scraped_content'):
        self.base_url = base_url
        self.output_dir = output_dir
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/images", exist_ok=True)
        
    def get_soup(self, url):
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    
    def scrape_text(self, soup):
        """Extract main text content and convert to markdown"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Extract text from common content containers
        content_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'article', 'main','div' 'section'])
        markdown_content = ""
        
        for tag in content_tags:
            if tag.name.startswith('h'):
                level = int(tag.name[1])
                markdown_content += f"{'#' * level} {tag.get_text().strip()}\n\n"
            else:
                markdown_content += f"{tag.get_text().strip()}\n\n"
                
        return markdown_content
    
    def scrape_images(self, soup, url):
        """Download images and return their markdown references"""
        image_markdown = ""
        images_dir = os.path.join(self.output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if not src or src.startswith('data:'):  # Skip data URIs
                continue
                
            img_url = urljoin(url, src)
            safe_filename = "".join(c for c in urlparse(img_url).path.split('/')[-1] if c.isalnum() or c in '._-')
            if not safe_filename:
                safe_filename = f"image_{hash(img_url)}.jpg"
                
            try:
                img_response = self.session.get(img_url, headers=self.headers)
                img_response.raise_for_status()
                
                img_path = os.path.join(images_dir, safe_filename)
                with open(img_path, 'wb') as f:
                    f.write(img_response.content)
                
                alt_text = img.get('alt', 'Image')
                # Use relative path for markdown reference
                image_markdown += f"![{alt_text}](images/{safe_filename})\n\n"
                
            except Exception as e:
                print(f"Failed to download image {img_url}: {e}")
                
        return image_markdown
    
    def scrape_tables(self, soup):
        """Convert HTML tables to markdown tables"""
        markdown_tables = ""
        
        for table in soup.find_all('table'):
            try:
                rows = []
                for tr in table.find_all('tr'):
                    row = [cell.get_text().strip() for cell in tr.find_all(['td', 'th'])]
                    if row:  # Only add non-empty rows
                        rows.append(row)
                
                if rows:
                    # Make all rows the same length by padding with empty strings
                    max_cols = max(len(row) for row in rows)
                    padded_rows = [row + [''] * (max_cols - len(row)) for row in rows]
                    
                    # Create DataFrame with default column names
                    df = pd.DataFrame(padded_rows)
                    markdown_tables += df.to_markdown(index=False) + "\n\n"
            except Exception as e:
                print(f"Failed to process table: {e}")
                continue
            
        return markdown_tables
    
    def scrape_page(self, url):
        """Scrape all content types from a page"""
        try:
            soup = self.get_soup(url)
            
            # Scrape different content types
            text_content = self.scrape_text(soup)
            image_content = self.scrape_images(soup, url)
            table_content = self.scrape_tables(soup)
            
            # Combine all content
            full_content = f"{text_content}\n{image_content}\n{table_content}"
            
            # Save to file
            page_name = urlparse(url).path.split('/')[-1] or 'index'
            output_file = os.path.join(self.output_dir, f"{page_name}.md")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_content)
                
            return output_file
            
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
            return None

# Usage example
if __name__ == "__main__":
    scraper = WebScraper("https://www.google.com/about/careers/applications/jobs/results/")
    output_file = scraper.scrape_page("https://www.google.com/about/careers/applications/jobs/results/")
    print(f"Content saved to {output_file}")