# Advanced Translation Suite Examples

This directory contains example files and usage patterns for the Advanced Translation Suite.

## Command Line Examples

### Basic Text Translation

```bash
# Translate a simple text file from English to Spanish
python run.py text --source English --target Spanish --input examples/sample.txt --output examples/sample_es.txt

# Translate technical documentation from English to Vietnamese
python run.py text --source English --target Vietnamese --input examples/technical_doc.md --type technical --country Vietnam

# Translate legal text with a specific model
python run.py text --source English --target French --input examples/legal.txt --type legal --endpoint OpenAI --model gpt-4o
```

### Excel Translation

```bash
# Translate Excel file from English to Japanese
python run.py excel --source English --target Japanese --file examples/data.xlsx --country Japan

# Process all Excel files in a directory
python run.py excel --source English --target Spanish --dir examples/excel_files/ --output examples/translated/

# Use Groq for faster translation
python run.py excel --source English --target German --file examples/data.xlsx --endpoint Groq
```

### Web Interface

```bash
# Launch the web interface on the default port
python run.py web

# Launch with custom port and share publicly
python run.py web --port 8080 --share
```

## Python API Examples

### Basic Text Translation

```python
from src.translator import model_load, simple_translator

# Initialize the model
model_load(
    endpoint="OpenAI",
    model="gpt-4o",
    api_key="your_api_key"  # Will use from .env if not provided
)

# Simple translation
result = simple_translator(
    source_lang="English",
    target_lang="French",
    source_text="Hello, how are you today?",
    country="France"
)
print(result)

# Get all translation steps
init_translation, reflection, final_translation = simple_translator(
    source_lang="English",
    target_lang="Spanish",
    source_text="The quick brown fox jumps over the lazy dog.",
    country="Mexico",
    full_response=True
)

print("Initial:", init_translation)
print("Reflection:", reflection)
print("Final:", final_translation)
```

### Excel Translation

```python
from src.translator import model_load, process_excel

# Initialize the model
model_load(
    endpoint="OpenAI",
    model="gpt-4o"
)

# Translate Excel file
output_path = process_excel(
    input_path="examples/data.xlsx",
    output_path="examples/data_translated.xlsx",
    source_lang="English",
    target_lang="Japanese",
    country="Japan"
)
print(f"Translated Excel saved to: {output_path}")

# Translate all Excel files in a directory
from src.translator import process_directory

translated_files = process_directory(
    input_dir="examples/excel_files",
    output_dir="examples/translated_excel",
    source_lang="English",
    target_lang="Chinese",
    country="China"
)

for file in translated_files:
    print(f"Translated: {file}")
```

### Working with Document Formats

```python
from src.translator import model_load, simple_translator, extract_pdf, extract_docx

# Initialize the model
model_load(endpoint="Groq", model="llama3-70b-8192")

# Translate PDF document
pdf_text = extract_pdf("examples/document.pdf")
translated_pdf = simple_translator(
    source_lang="English",
    target_lang="Korean",
    source_text=pdf_text
)

with open("examples/document_kr.txt", "w", encoding="utf-8") as f:
    f.write(translated_pdf)

# Translate Word document
docx_text = extract_docx("examples/report.docx")
translated_docx = simple_translator(
    source_lang="English",
    target_lang="Arabic",
    source_text=docx_text
)

with open("examples/report_ar.txt", "w", encoding="utf-8") as f:
    f.write(translated_docx)
``` 