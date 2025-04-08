# Advanced Translation Suite

A powerful translation tool that supports multiple file formats and translation styles.

## Features

- Translate text, PDF files, and Excel files
- Multiple translation styles (General, Literary, Technical, Financial, etc.)
- Custom terminology support
- Language detection
- Batch translation
- Preserve formatting in Excel files

## Requirements

- Python 3.8+
- Required Python packages:
  - gradio
  - openai
  - xlwings
  - reportlab
  - python-dotenv
  - tiktoken
  - langchain-text-splitters

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/translate_excel_text_agent.git
   cd translate_excel_text_agent
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API key:
   Create a `.env` file in the project root and add your API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Start the web interface:
   ```bash
   python app/web_app.py
   ```

2. Open your browser and go to `http://localhost:7860`

3. Choose your translation options:
   - Select source and target languages
   - Choose translation style
   - Upload custom terminology file (optional)
   - Add custom style instructions (optional)

4. Translate:
   - Enter text directly
   - Upload PDF files
   - Upload Excel files

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

- PDF files must be text-based (not scanned images)
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
