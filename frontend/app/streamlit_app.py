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
try:
    from backend.app.utils.opensource.web_utils import WebScraper
   # from backend.app.utils.opensource.pdf_utils import DoclingConverter
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current sys.path: {sys.path}")
    st.error("Failed to import required modules. Please check the console for details.")

# Initialize session state
if 'extracted_content' not in st.session_state:
    st.session_state.extracted_content = ""
if 'extraction_metadata' not in st.session_state:
    st.session_state.extraction_metadata = {}

def extract_pdf_text(uploaded_file, extraction_type="enterprise"):
    """Extract text from PDF using either enterprise or opensource solution"""
    pdf_path = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            pdf_path = Path(tmp_file.name)
        
        output_dir = Path("temp_output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if extraction_type == "enterprise":
            # First API call - PDF extraction
            response = requests.post(
                f"{API_BASE_URL}/extract-pdf/enterprise",
                json={
                    "pdf_path": str(pdf_path),
                    "output_dir": str(output_dir)
                }
            )
            
            if response.status_code != 200:
                st.error(f"PDF Extraction API Error: {response.json().get('detail', 'Unknown error')}")
                return None
                
            print("PDF Extraction API Response:", response.json())
            zip_path = response.json().get('zip_path')
            
            if not zip_path:
                st.error("No zip path returned from extraction API")
                return None
            
            # Second API call - ZIP processing
            result = requests.post(
                f"{API_BASE_URL}/process-zip/enterprise",
                json={"zip_path": zip_path}
            )
            
            if result.status_code != 200:
                st.error(f"ZIP Processing API Error: {result.json().get('detail', 'Unknown error')}")
                return None
                
            print("ZIP Processing API Response:", result.json())
            result_data = result.json()
            print("Result data:", result_data)
            # Get content from markdown file
            output_dir = Path(result_data["output_locations"]["output_directory"])
            markdown_path = output_dir / "markdown" / "content.md"

            if not markdown_path.exists():
                st.error(f"Markdown file not found at: {markdown_path}")
                return None
                
            content = markdown_path.read_text()
            # Store metadata
            st.session_state.extraction_metadata = {
                "markdown_file": str(markdown_path),
                "images_directory": result_data["output_locations"]["images_directory"]
            }
            return content
            
        else:
            # Use opensource Docling solution
            try:
                # converter = DoclingConverter()
                # result = converter.process_pdf(pdf_path, output_dir)
                
                # if result['status'] != 'success':
                #     st.error(f"Error in PDF conversion: {result.get('message', 'Unknown error')}")
                #     return None
                    
                # content = Path(result['markdown_path']).read_text()
                # st.session_state.extraction_metadata = {
                #     'tables': result['tables'],
                #     'images': result['images']
                # }
                return content
                
            except Exception as e:
                st.error(f"Open source PDF extraction failed: {str(e)}")
                return None
                
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None
        
    finally:
        # Cleanup temporary files
        if pdf_path:
            try:
                os.unlink(str(pdf_path))
            except Exception as e:
                print(f"Error removing temporary file: {e}")

def scrape_website(url):
    """Scrape content from website"""
    try:
        scraper = WebScraper(url)
        output_file = scraper.scrape_page(url)
        
        if output_file and os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        else:
            st.error("Failed to scrape website")
            return None
            
    except Exception as e:
        st.error(f"Error scraping website: {str(e)}")
        return None

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
        pdf_engine = st.radio(
            "Select PDF Engine",
            ["Enterprise (Adobe)", "Open Source (Docling)"]
        )

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📥 Data Source", "📄 Content", "📊 Analysis"])

with tab1:
    st.header("Data Source/Extraction")
    
    if extraction_type == "PDF Extraction":
        uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'])
        
        if uploaded_file is not None and st.button("🚀 Extract Content"):
            with st.spinner("Processing PDF..."):
                engine = "enterprise" if pdf_engine == "Enterprise (Adobe)" else "opensource"
                st.session_state.extracted_content = extract_pdf_text(uploaded_file, engine)
                if st.session_state.extracted_content:
                    st.success("✅ PDF extracted successfully!")
    
    else:  # Web Scraping
        url = st.text_input("Enter website URL")
        if url and st.button("🌐 Scrape Content"):
            with st.spinner("Scraping website..."):
                st.session_state.extracted_content = scrape_website(url)
                if st.session_state.extracted_content:
                    st.success("✅ Website scraped successfully!")

with tab2:
    st.header("Extracted Content")
    if st.session_state.extracted_content:
        st.markdown(st.session_state.extracted_content)
        st.markdown(get_download_link(st.session_state.extracted_content), unsafe_allow_html=True)
        
        if st.session_state.extraction_metadata:
            st.subheader("📊 Extraction Details")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📑 Tables", st.session_state.extraction_metadata.get('tables', 0))
            with col2:
                st.metric("🖼️ Images", st.session_state.extraction_metadata.get('images', 0))
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