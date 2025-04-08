"""
Advanced Translation Suite - Translator Module
Combines Translation Agent with Excel processing capabilities
"""

from .translator_core import (
    model_load,
    get_completion,
    simple_translator,
    batch_translate,
    num_tokens_in_string,
    calculate_chunk_size
)

from .excel_processor import (
    process_excel,
    process_directory,
    clean_text,
    should_translate
)

from .document_utils import (
    extract_text,
    extract_pdf,
    extract_docx,
    tokenize,
    diff_texts
)

__all__ = [
    # Core translation functions
    'model_load',
    'get_completion',
    'simple_translator',
    'batch_translate',
    'num_tokens_in_string',
    'calculate_chunk_size',
    
    # Excel processing functions
    'process_excel',
    'process_directory',
    'clean_text',
    'should_translate',
    
    # Document utilities
    'extract_text',
    'extract_pdf',
    'extract_docx',
    'tokenize',
    'diff_texts',
] 