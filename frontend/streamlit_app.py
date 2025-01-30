# Must be the first Streamlit command
import streamlit as st
st.set_page_config(
    page_title="DataNexus Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

import io
import base64
import tempfile
from pathlib import Path
import os
import sys
import requests

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

# Import backend modules

# Initialize session state
if 'extracted_content' not in st.session_state:
    st.session_state.extracted_content = ""
if 'extraction_metadata' not in st.session_state:
    st.session_state.extraction_metadata = {}

def extract_pdf_text(uploaded_file, extraction_type="enterprise"):
    """Extract text from PDF using either enterprise or opensource solution"""
    # [Previous PDF extraction code remains the same]
    pass

def scrape_website(url, scraping_type="enterprise"):
    """Scrape content from website using either enterprise or opensource solution"""
    try:
        # Create temporary output directory
        output_dir = Path("temp_output") / "web_scraping"
        output_dir.mkdir(parents=True, exist_ok=True)

        if scraping_type == "enterprise":
            # Enterprise web scraping using API
            response = requests.post(
                f"{API_BASE_URL}/web-scraping/enterprise",
                json={
                    "url": url,
                    "output_dir": str(output_dir)
                }
            )
            
            if response.status_code != 200:
                st.error(f"Web Scraping API Error: {response.json().get('detail', 'Unknown error')}")
                return None
            
            result_data = response.json()
            
            if result_data["status"] == "success":
                # Read the markdown content
                markdown_path = Path(result_data["saved_path"])
                if markdown_path.exists():
                    content = markdown_path.read_text(encoding='utf-8')
                    # Store metadata
                    st.session_state.extraction_metadata = {
                        "source_url": url,
                        "saved_path": result_data["saved_path"],
                        "status": "success"
                    }
                    return content
                else:
                    st.error("Markdown file not found")
                    return None
            else:
                st.error(f"Web scraping failed: {result_data.get('message', 'Unknown error')}")
                return None

        else:
            # Open source web scraping using API
            response = requests.post(
                f"{API_BASE_URL}/web-scraping/opensource",
                json={
                    "url": url,
                    "output_dir": str(output_dir)
                }
            )
            
            if response.status_code != 200:
                st.error(f"Web Scraping API Error: {response.json().get('detail', 'Unknown error')}")
                return None
                
            result_data = response.json()
            
            if result_data["status"] == "success":
                # Read the markdown content
                markdown_path = Path(result_data["saved_path"]["markdown"])
                if markdown_path.exists():
                    content = markdown_path.read_text(encoding='utf-8')
                    # Store metadata
                    st.session_state.extraction_metadata = {
                        "source_url": url,
                        "html_path": result_data["saved_path"]["html"],
                        "markdown_path": result_data["saved_path"]["markdown"],
                        "images_folder": result_data["saved_path"]["images_folder"],
                        "status": "success"
                    }
                    return content
                else:
                    st.error("Markdown file not found")
                    return None
            else:
                st.error(f"Web scraping failed: {result_data.get('message', 'Unknown error')}")
                return None
            
    except Exception as e:
        st.error(f"Error scraping website: {str(e)}")
        return None
    finally:
        # Cleanup temporary files if needed
        try:
            if output_dir.exists():
                import shutil
                shutil.rmtree(output_dir)
        except Exception as e:
            print(f"Error cleaning up temporary files: {e}")

def get_download_link(text, filename="extracted_content.md"):
    """Create download link for extracted content"""
    try:
        b64 = base64.b64encode(text.encode()).decode()
        return f'<a href="data:text/markdown;base64,{b64}" download="{filename}" class="download-button">Download Markdown File</a>'
    except Exception as e:
        st.error(f"Error creating download link: {str(e)}")
        return None

# Main layout
st.title("📊 DataNexus Pro")
st.subheader("Unified Data Extraction Platform")

# Sidebar
with st.sidebar:
    st.header("Dashboard Controls")
    extraction_type = st.selectbox(
        "Select Extraction Type",
        ["PDF Extraction", "Web Scraping"]
    )
    
    if extraction_type == "PDF Extraction":
        extraction_engine = st.radio(
            "Select PDF Engine",
            ["Enterprise (Adobe)", "Open Source (Docling)"]
        )
    else:
        extraction_engine = st.radio(
            "Select Scraping Engine",
            ["Enterprise (Advanced)", "Open Source (Basic)"]
        )

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📥 Data Source", "📄 Content", "📊 Analysis"])

with tab1:
    st.header("Data Source/Extraction")
    
    if extraction_type == "PDF Extraction":
        uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'])
        
        if uploaded_file is not None and st.button("🚀 Extract Content"):
            with st.spinner("Processing PDF..."):
                engine = "enterprise" if "Enterprise" in extraction_engine else "opensource"
                st.session_state.extracted_content = extract_pdf_text(uploaded_file, engine)
                if st.session_state.extracted_content:
                    st.success("✅ PDF extracted successfully!")
    
    else:  # Web Scraping
        url = st.text_input("Enter website URL")
        if url and st.button("🌐 Scrape Content"):
            with st.spinner("Scraping website..."):
                engine = "enterprise" if "Enterprise" in extraction_engine else "opensource"
                st.session_state.extracted_content = scrape_website(url, engine)
                if st.session_state.extracted_content:
                    st.success("✅ Website scraped successfully!")

# [Rest of the code for tab2 and tab3 remains the same]

# Styling
st.markdown("""
    <style>
    .download-button {
        display: inline-block;
        padding: 0.5em 1em;
        color: white;
        background-color: #0066cc;
        border-radius: 4px;
        text-decoration: none;
        margin: 1em 0;
        transition: background-color 0.3s ease;
    }
    .download-button:hover {
        background-color: #0052a3;
        text-decoration: none;
    }
    .stButton>button {
        width: 100%;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)