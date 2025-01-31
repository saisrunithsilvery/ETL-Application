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
import shutil

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

# Initialize session state
if 'extracted_content' not in st.session_state:
    st.session_state.extracted_content = ""
if 'extraction_metadata' not in st.session_state:
    st.session_state.extraction_metadata = {}

def extract_pdf_text(uploaded_file, extraction_type="enterprise"):
    """Extract text from PDF using either enterprise or opensource solution"""
    pdf_path = None
    try:
        # Create temporary file and directory
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            pdf_path = Path(tmp_file.name)
        
        output_dir = Path("temp_output") / "pdf_extraction"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if extraction_type == "enterprise":
            # Enterprise PDF extraction using API
            response = requests.post(
                f"{API_BASE_URL}/extract-pdf/enterprise",
                json={
                    "pdf_path": str(pdf_path),
                    "output_dir": str(output_dir)
                }
            )
            result = requests.post(
                f"{API_BASE_URL}/process-zip/enterprise",
                json={
                    "zip_path": response.json().get("zip_path")
                    
                }
            )   
            if result.status_code != 200:
                st.error(f"PDF Extraction API Error: {response.json().get('detail', 'Unknown error')}")
                return None

            result_data = result.json()
            markdown_url = result_data["output_locations"]["markdown_file"]
            if result_data["status"] == "success":
                markdown_response = requests.get(markdown_url)
                if markdown_response.status_code == 200:
                    content = markdown_response.text
                    st.session_state.extraction_metadata = {
                        "markdown_file": markdown_url,
                        "images_directory": result_data["output_locations"].get("base_path"),
                        "bucket": result_data["output_locations"].get("bucket")
                    }
                    return content
                else:
                    st.error("Markdown file not found")
                    return None
        else:
            # Open source PDF extraction
            response = requests.post(
                f"{API_BASE_URL}/extract-pdf/opensource",
                json={
                    "pdf_path": str(pdf_path),
                    "output_dir": str(output_dir)
                }
            )

            if response.status_code != 200:
                st.error(f"PDF Extraction API Error: {response.json().get('detail', 'Unknown error')}")
                return None

            result_data = response.json()
            
            if result_data["status"] == "success":
                content = Path(result_data["markdown_path"]).read_text(encoding='utf-8')
                st.session_state.extraction_metadata = {
                    "source_type": "pdf",
                    "markdown_path": result_data["markdown_path"],
                    "tables": result_data.get("tables", 0),
                    "images": result_data.get("images", 0),
                    "status": "success"
                }
                return content

    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None
    
    finally:
        # Cleanup temporary files
        if pdf_path and pdf_path.exists():
            try:
                pdf_path.unlink()
            except Exception as e:
                print(f"Error removing temporary file: {e}")

def scrape_website(url, scraping_type="enterprise"):
    """Scrape content from website using either enterprise or opensource solution"""
    try:
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

            result = requests.post(
                f"{API_BASE_URL}/web-process/",
                json={
                    "md_path": response.json().get("saved_path"),
                   
                }
            )
            
           
            result_data = result.json()
            
            markdown_url = result_data.get("saved_path")
           
            
            if result_data["status"] == "success":
                markdown_response = requests.get(markdown_url)
                print(markdown_response.text)
                content = markdown_response.text
                # print(f"Content length: {len(content)}")
                # print(f"First 100 characters: {content[:100]}")
                st.session_state.extraction_metadata = {
                    "markdown_file": markdown_url
                }
                print(f"Content length is the : {len(content)}")
                print(f"First 100 characters: {content[:100]}")
                return content
               
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
                try:
                    markdown_response = requests.get(result_data["output_locations"]["markdown_file"])
                    if markdown_response.status_code == 200:
                        content = markdown_response.text
                        st.session_state.extraction_metadata = {
                            "source_type": "web",
                            "source_url": url,
                            "markdown_file": result_data["output_locations"]["markdown_file"],
                            "images_directory": result_data["output_locations"].get("base_path"),
                            "bucket": result_data["output_locations"].get("bucket"),
                            "status": "success"
                        }
                        return content
                except Exception as e:
                    st.error(f"Error fetching markdown content: {str(e)}")
                    return None

    except Exception as e:
        st.error(f"Error scraping website: {str(e)}")
        return None
    
    finally:
        # Cleanup temporary files
        try:
            if output_dir.exists():
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

    extraction_engine = st.radio(
        "Select Engine",
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

with tab2:
    st.header("Extracted Content")
    if st.session_state.extracted_content:
        st.markdown(st.session_state.extracted_content)
        st.markdown(get_download_link(st.session_state.extracted_content), unsafe_allow_html=True)
        
        if st.session_state.extraction_metadata:
            st.subheader("📊 Extraction Details")
            if st.session_state.extraction_metadata.get("source_type") == "pdf":
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📑 Tables", st.session_state.extraction_metadata.get('tables', 0))
                with col2:
                    st.metric("🖼️ Images", st.session_state.extraction_metadata.get('images', 0))
            elif st.session_state.extraction_metadata.get("source_type") == "web":
                st.text(f"Source URL: {st.session_state.extraction_metadata.get('source_url', 'N/A')}")
    else:
        st.info("💡 No content extracted yet. Please use the Data Source tab to extract content.")

with tab3:
    st.header("Analysis Dashboard")
    if st.session_state.extracted_content:
        # Text analysis
        word_count = len(st.session_state.extracted_content.split())
        char_count = len(st.session_state.extracted_content)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Word Count", word_count)
        with col2:
            st.metric("📊 Character Count", char_count)
        with col3:
            avg_word_length = round(char_count / word_count, 2) if word_count > 0 else 0
            st.metric("📏 Avg Word Length", avg_word_length)
        
        # Content preview
        st.subheader("📄 Content Preview")
        with st.expander("Show first 500 characters"):
            st.text_area(
                "Content sample",
                st.session_state.extracted_content[:500],
                height=200,
                disabled=True
            )
    else:
        st.info("💡 No content to analyze. Please extract content first.")

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