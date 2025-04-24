# Advanced Translation Suite

A powerful translation tool that supports multiple file formats and translation styles, including PDF OCR.

## Features

- Translate text, PDF files, and Excel files
- **Extract text from image-based or complex PDFs using OCR**
- Multiple translation styles (General, Literary, Technical, Financial, etc.)
- Custom terminology support
- Language detection
- Batch translation
- Preserve formatting in Excel files

## Requirements

- Python 3.8+
- **System Dependencies:**
    - **Tesseract OCR Engine:** Required for the PDF OCR feature. Must be installed and added to the system PATH. See Tesseract documentation for installation instructions for your OS (Windows/macOS/Linux).
    - **Poppler:** Required by the `pdf2image` library (used for OCR). Must be installed and utilities (like `pdftoppm`) added to the system PATH. See Poppler documentation/builds for your OS.
- **Required Python packages (install via `pip install -r requirements.txt`):**
  - gradio
  - openai
  - xlwings
  - reportlab
  - python-dotenv
  - tiktoken
  - langchain-text-splitters
  - simplemma>=0.9.1

  # Document processing
  - pymupdf>=1.22.0  # PDF processing
  - python-docx>=0.8.11  # DOCX processing

  # Excel processing (optional, needed only for Excel translation)
  - xlwings>=0.30.0  # Excel processing (requires Microsoft Excel installation)

  # Dependencies for PDF OCR (New)
  - pytesseract>=0.3.10
  - python-pdf2image>=1.16.3

  # Suggested packages for improved functionality
  - icecream>=2.1.3  # Better debugging

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/translate_excel_text_agent.git
   cd translate_excel_text_agent
   ```

2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   **Note:** Ensure you have installed the system dependencies (Tesseract and Poppler) *before* running the application if you intend to use the PDF OCR feature.

3. Set up your API key:
   Create a `.env` file in the project root and add your API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Start the web interface:
   ```bash
   python run.py web
   ```
   (You can also use `python run.py --help` to see command-line options for text and Excel translation.)

2. Open your browser and go to `http://localhost:7860` (or the specified port).

3. **Using the PDF OCR Tab:**
   - Navigate to the "PDF OCR" tab.
   - Click "Tải lên PDF để OCR" to upload your PDF file.
   - Select the primary language present in the PDF document from the "Ngôn ngữ trong PDF (OCR)" dropdown.
   - Click the "Trích xuất Văn bản từ PDF" button.
   - Wait for the processing to complete. The extracted text will appear in the right-hand text area.
   - If needed, click "Gửi tới ô Dịch" to copy the extracted text to the main "Text Translation" tab for translation.
   - Check the "Trạng thái OCR" and "Thông báo lỗi OCR" fields for status updates or error messages.

4. **Using other tabs (Text, Dịch PDF, Dịch Excel):**
   - Choose your translation options in the left sidebar (API keys, languages, style, etc.).
   - Enter text directly or upload files in the respective tabs.
   - Click the appropriate "Translate" button.

## Translation Styles

- General: Standard translation with balanced accuracy and fluency
- Literary: Preserves artistic style and literary devices
- Technical: Focuses on technical accuracy and terminology
- Financial: Specialized for financial documents
- Legal: Precise legal terminology and formal style
- Medical: Medical terminology and clinical language
- Scientific: Academic and research-oriented translation
- Casual: Informal, conversational style
- Formal: Professional and formal language
- Marketing: Persuasive and engaging content
- Educational: Clear and instructional language
- Creative: Artistic and innovative translation

## Custom Terminology

You can provide a custom terminology file in the following format:
```
source_term=target_term
one term=one thuật ngữ
another term=thuật ngữ khác
```

## Notes

- PDF files for the *translation* tab ("Dịch PDF") ideally should be text-based for best results with direct translation. Use the "PDF OCR" tab first for image-based or complex PDFs.
- Excel files should not contain complex formulas
- Large files may take longer to process
- Some formatting may be lost in translation

## Troubleshooting

1. If you get a "No module named 'reportlab'" error:
   ```bash
   pip install reportlab
   ```

2. If Excel translation fails:
   - Make sure xlwings is installed
   - Check if Excel is installed on your system
   - Try saving the file in a newer Excel format (.xlsx)

3. If language detection fails:
   - Ensure the text is long enough (at least 10 characters)
   - Check your internet connection
   - Verify your API key is valid

## License

MIT License 
