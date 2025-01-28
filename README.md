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