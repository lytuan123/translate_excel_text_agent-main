"""
Document Processing Utilities for Advanced Translation Suite
Contains functions for extracting text from different file formats
"""

import re
from difflib import Differ
from typing import List, Tuple, Optional


def extract_text(path: str) -> str:
    """
    Extract text from a plain text file.
    
    Args:
        path: Path to the text file
        
    Returns:
        Extracted text content
    """
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        file_text = f.read()
    return file_text


def extract_pdf(path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    try:
        import pymupdf
        
        doc = pymupdf.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
        
    except ImportError:
        raise ImportError(
            "PyMuPDF is not installed. Please install with: pip install pymupdf"
        )


def extract_docx(path: str) -> str:
    """
    Extract text from a Word document.
    
    Args:
        path: Path to the DOCX file
        
    Returns:
        Extracted text content
    """
    try:
        import docx
        
        doc = docx.Document(path)
        data = []
        for paragraph in doc.paragraphs:
            data.append(paragraph.text)
        content = "\n\n".join(data)
        return content
        
    except ImportError:
        raise ImportError(
            "python-docx is not installed. Please install with: pip install python-docx"
        )


def tokenize(text: str) -> List[str]:
    """
    Tokenize text for diff visualization.
    
    Args:
        text: Input text to tokenize
        
    Returns:
        List of tokens (words and spaces)
    """
    try:
        from simplemma import simple_tokenizer
        
        # Use simplemma to tokenize the text
        words = simple_tokenizer(text)
        
        # Check if the text contains spaces
        if " " in text:
            # Create a list of words and spaces
            tokens = []
            for word in words:
                tokens.append(word)
                # Don't add space after punctuation
                if not word.startswith("'") and not word.endswith("'"):
                    tokens.append(" ")
            return tokens[:-1]  # Remove the last space
        else:
            return words
            
    except ImportError:
        # Fallback simple tokenization if simplemma is not available
        words = []
        current_word = ""
        
        for char in text:
            if char.isalnum() or char in "-'":
                current_word += char
            else:
                if current_word:
                    words.append(current_word)
                    current_word = ""
                if not char.isspace():
                    words.append(char)
                else:
                    words.append(" ")
                    
        if current_word:
            words.append(current_word)
            
        return words


def diff_texts(text1: str, text2: str) -> List[Tuple[str, Optional[str]]]:
    """
    Create a highlighted diff between two texts.
    
    Args:
        text1: First text (typically initial translation)
        text2: Second text (typically improved translation)
        
    Returns:
        List of (word, category) tuples for visualization
    """
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)
    
    d = Differ()
    diff_result = list(d.compare(tokens1, tokens2))
    
    highlighted_text = []
    for token in diff_result:
        word = token[2:]
        category = None
        
        if token[0] == "+":
            category = "added"
        elif token[0] == "-":
            category = "removed"
        elif token[0] == "?":
            continue  # Ignore the hints line
            
        highlighted_text.append((word, category))
        
    return highlighted_text 