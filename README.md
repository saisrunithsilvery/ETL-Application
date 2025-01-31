# Assignment 1 - Document Processing Platform
 
## Project Links and Resources
 
- **GitHub Issues and Tasks**: [Link to GitHub Project Issues]
- **Codelabs Documentation**: [Link to Codelabs]
- **Project Submission Video (5 Minutes)**: [Link to Submission Video]
- **Hosted Application Links**:
  - **Frontend (Streamlit)**: []()
  - **Backend (FastAPI)**: []()
 
 
## Introduction
 
This project focuses on building a **document processing platform** capable of extracting, structuring, and managing data from **unstructured sources like PDFs and web pages**. The goal is to evaluate the feasibility of **open-source and enterprise tools**, compare their performance, and develop a **Client-facing Streamlit application** that integrates document processing with **standardization, storage, and retrieval mechanisms**.  
 
The system will extract content from **PDFs and web pages**, process it into **Markdown format**, and store it efficiently in **AWS S3**. It will also provide a **FastAPI-based backend** and a **Streamlit-based frontend** for user interaction. The platform aims to ensure **scalability, security, and usability** by integrating modern technologies for **data extraction, organization, and querying**.  
 
By leveraging **PyPDF2, pdfplumber, BeautifulSoup, Microsoft Document Intelligence, Docling, and MarkItDown**, this project will evaluate various methodologies for document processing. Additionally, it will implement **FastAPI and Streamlit** to enable **secure access, document processing, and retrieval** via an interactive user interface.
 
 
The core technologies used in this project include:
- **Docling**: Used for PDF extraction as an Open Source Tool.
- **Adobe PDF Services**: Used for PDF extraction as an Closed Source Tool.
- **Jina.ai**: Used for Web Page extraction as an Closed source Tool.
- **Beautiful Soup**: Used for Web Page extraction as an Open Source Tool.
- **FastAPI**: Backend for handling requests.
- **Streamlit**: Frontend for the client-facing application.
- **Render**: For Delopyment.
 
The project aims to provide a comprehensive platform for extracting, storing, and interacting with document data.
 
## Problem Statement
 
The challenge is to develop a **scalable platform** that enables users to:  
1. **Extract and convert** data from PDFs and web pages into a structured format.  
2. **Compare open-source and enterprise tools** for document processing efficiency.  
3. **Store and retrieve processed data** in AWS S3 with proper organization.  
4. **Provide an Client Interface** for seamless interaction.  
 
### **Desired Outcome:**  
- Efficient extraction and conversion of PDF and webpage data.  
- Standardized storage of processed content in **Markdown format**.  
- Scalable and well-organized infrastructure for storing and retrieving files in **AWS S3**.  
- A seamless **API and client interface** for processing and interacting with extracted data.  
 
### **Constraints:**  
- Handling large datasets efficiently from **PDFs and web pages**.  
- Managing **multiple tools for extraction** (open-source and enterprise).  
- Ensuring **proper organization and retrieval** of files in AWS S3.  
 
## **Proof of Concept**  
 
The project utilizes two main approaches for document extraction:  
- **Docling & Beautiful Soup** (open-source) and **Adobe PDF Services & Jina.ai** (enterprise).  
 
The extracted content is stored in **AWS S3** for efficient retrieval and further processing. Initial setup involved:  
- Developing Python Functions to handle the extraction of texts,tables,images from PDF's and WebPages.  
- Storing extracted content in **Markdown format**.  
- Organizing processed files in **AWS S3** with structured naming conventions and metadata tagging.  
- Developing an **API** to handle document processing and retrieval.  
- Creating a **client-facing Streamlit interface** for uploading and viewing extracted content.  
 
Challenges such as **handling diverse document structures and optimizing extraction accuracy** have been addressed by using multiple extraction tools and refining the standardization process.  
 
 
Certainly! Here’s the section for **local setup and running the code locally** that you can insert into your existing README:
 
---
 
# PDF to Markdown Converter
 
This tool converts PDF documents to Markdown format using Adobe PDF Services API, preserving document structure, tables, and images.
 
## Prerequisites
 
- Python 3.8 or higher
- Adobe PDF Services API credentials (client ID and client secret)
- Git (for cloning the repository)
 
## Setup Instructions
 
### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```
 
### 2. Set Up Python Virtual Environment
 
#### On Windows:
```bash
# Create virtual environment
python -m venv venv
 
# Activate virtual environment
venv\Scripts\activate
```
 
#### On macOS/Linux:
```bash
# Create virtual environment
python3 -m venv venv
 
# Activate virtual environment
source venv/bin/activate
```
 
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
 
### 4. Configure Adobe Credentials
 
Create a `.env` file in the project root and add your Adobe API credentials:
```plaintext
PDF_SERVICES_CLIENT_ID=your_client_id_here
PDF_SERVICES_CLIENT_SECRET=your_client_secret_here
```
 
## Usage
 
1. Activate the virtual environment (if not already activated):
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```
 
2. Run the PDF conversion script:
   ```bash
   python pdf_utils.py
   ```
 
3. The converted files will be available in:
   - `output/markdown/` - Markdown files
   - `output/images/` - Extracted images
 
## Project Structure
```
.
├── pdf_utils.py          # Main PDF extraction script
├── handler_utils.py      # ZIP and markdown conversion utilities
├── requirements.txt      # Project dependencies
├── .env                 # Environment variables (create this)
└── output/              # Output directory
    ├── markdown/        # Converted markdown files
    └── images/          # Extracted images
```
 
## Notes
 
- The virtual environment should be activated every time you work on the project
- Keep your Adobe credentials secure and never commit them to version control
- Make sure you have proper permissions for file operations in the project directory
 
## Troubleshooting
 
1. If you encounter permission errors, make sure you have write access to the output directory
 
2. For Adobe API errors, verify your credentials in the `.env` file
 
3. If pip install fails:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
 
4. For virtual environment issues:
   ```bash
   # Remove existing venv
   rm -rf venv
   
   # Create new venv
   python -m venv venv
   ```
 
## Dependencies
 
- requests==2.31.0
- beautifulsoup4==4.12.2
- pandas==2.1.3
- markdown==3.5.1
- adobe-pdfservices-sdk
- openpyxl>=3.0.10
- pathlib>=1.0.1
- markdown-it-py>=2.0.0
- python-dotenv>=0.19.0
--
 
## Architecture Diagram
 
![Architecture Diagram](docling_multimodal/architecture_diagram.png)
 
### **Description of Components**  
 
- **Render.com**: The cloud platform where both the **FastAPI backend** and **Streamlit frontend** are deployed, making the application accessible online.  
 
- **Client Interface (Streamlit)**: A user-friendly web application where users can **upload PDFs**, **enter webpage URLs**, **select extraction tools**, and **view extracted data** in an interactive manner.  
 
- **Document Type Selection**: Allows users to choose between **PDF Extraction** and **Web Scraping**, determining which processing method will be used.  
 
- **Tool Selection**:  
  - **Web Scraping Tools**:  
    - **Enterprise (Jina.ai)** → AI-powered web scraping tool for structured and unstructured web data.  
    - **Open Source (Beautiful Soup)** → Python library for parsing and extracting data from HTML and XML documents.  
  - **PDF Extraction Tools**:  
    - **Enterprise (Adobe PDF Services)** → Proprietary tool for extracting text, tables, and images from PDFs.  
    - **Open Source (Docling)** → Open-source tool for document processing, supporting text and image extraction.  
 
- **FastAPI Server (Backend Processing)**: Handles user requests, processes extracted content, and sends structured data for storage and retrieval.  
 
- **Processing Extracted Data**:  
  - Extracts **text, tables, and images** from PDFs and webpages.  
  - Converts extracted content into **Markdown format** for standardization.  
  - Sends extracted images and references to **AWS S3**.  
 
- **Markdown Format Storage**: Stores extracted and structured **text content** , making it easy to query and retrieve processed data.  
 
- **AWS S3 (Images & References)**: Stores extracted **images, tables, and metadata** for future access and retrieval.  
 
### **Data Flow:**  
1. **Users upload PDFs or enter webpage URLs** through the **Streamlit client interface**.  
2. **Users select the extraction type** → **PDF Extraction or Web Scraping**.  
3. **Users choose an extraction tool** → **Open-source (Docling, Beautiful Soup) or Enterprise (Adobe PDF Services, Jina.ai)**.  
4. **The FastAPI backend processes the request**, extracting **text, tables, and images** from the selected document.  
5. **Extracted data is converted into Markdown format** for standardization.  
6. **Extracted images and references are stored in AWS S3**
7. **Users interact with the extracted content** through the **Streamlit interface**, viewing and downloading processed documents.  
 
 
**Team Members:**
- Sai Priya Veerabomma
- Sai Srunith Silvery
- Vishal Prasanna


 
 
## References
 
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Docling](https://ds4sd.github.io/docling/)
- [Jina.ai](https://jina.ai/serve/)
- [Adobe PDF Services](https://developer.adobe.com/document-services/docs/overview/)
 