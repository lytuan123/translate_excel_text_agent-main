"""
PDF Processor for Advanced Translation Suite
Handles PDF file reading, language detection, and translation
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

# Import translator utilities
from .translator_core import batch_translate, detect_language
from .document_utils import extract_pdf


def process_pdf(
    input_path: str,
    output_path: Optional[str] = None,
    source_lang: str = "English",
    target_lang: str = "Spanish",
    country: str = "",
    batch_size: int = 100,
    detect_languages: bool = True,
    translation_style: str = "General",
    custom_style_instructions: Optional[str] = None,
    terminology_file: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Process a PDF file: extract text, detect languages, translate, and save the result.
    
    Args:
        input_path: Path to the PDF file to translate
        output_path: Path where to save the translated file (if None, auto-generated)
        source_lang: Source language of the content (used if language detection is disabled)
        target_lang: Target language for translation
        country: Optional country context for translation style
        batch_size: Maximum number of paragraphs to translate in one batch
        detect_languages: Whether to detect languages in different sections of the PDF
        translation_style: Style of translation to use (e.g., "Literary", "Technical")
        custom_style_instructions: Additional custom instructions for the style
        terminology_file: Path to custom terminology file
        
    Returns:
        Tuple of (PDF output path, TXT output path)
    """
    try:
        # Extract text from PDF
        print(f"\n🔄 Processing PDF file: {input_path}")
        print(f"   Source: {source_lang}, Target: {target_lang}, Country: {country}")
        print(f"   Style: {translation_style}")
        
        pdf_text = extract_pdf(input_path)
        
        # Split text into paragraphs
        paragraphs = re.split(r'\n\s*\n', pdf_text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        if not paragraphs:
            print("❌ No text content found in the PDF")
            return "", ""
        
        print(f"   📄 Extracted {len(paragraphs)} paragraphs from PDF")
        
        # Create output file paths if not provided
        if output_path is None:
            filename = os.path.basename(input_path)
            base_name, ext = os.path.splitext(filename)
            
            # Auto-generate output paths
            dir_name = os.path.dirname(input_path)
            output_path_pdf = os.path.join(dir_name, f"{base_name}-{target_lang}.pdf")
            output_path_txt = os.path.join(dir_name, f"{base_name}-{target_lang}.txt")
        else:
            base_name, ext = os.path.splitext(output_path)
            output_path_pdf = f"{base_name}.pdf"
            output_path_txt = f"{base_name}.txt"
        
        # Process paragraphs
        translated_paragraphs = []
        
        if detect_languages:
            # Group paragraphs by detected language
            language_groups = {}
            
            print("   🔍 Detecting languages in paragraphs...")
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph) < 10:  # Skip very short paragraphs
                    continue
                    
                detected_lang = detect_language(paragraph)
                if detected_lang not in language_groups:
                    language_groups[detected_lang] = []
                language_groups[detected_lang].append((i, paragraph))
            
            print(f"   ✅ Detected {len(language_groups)} different languages in the PDF")
            
            # Initialize translated paragraphs with original text
            translated_paragraphs = paragraphs.copy()
            
            # Translate each language group separately
            for lang, para_indices in language_groups.items():
                if lang.lower() == target_lang.lower():
                    print(f"   ⏩ Skipping paragraphs in target language: {lang}")
                    continue
                
                print(f"   🔄 Translating {len(para_indices)} paragraphs from {lang} to {target_lang}")
                
                # Extract paragraphs for this language
                lang_paragraphs = [p[1] for p in para_indices]
                
                # Translate in batches
                total_batches = (len(lang_paragraphs) - 1) // batch_size + 1
                
                for batch_idx in range(total_batches):
                    start_idx = batch_idx * batch_size
                    end_idx = min((batch_idx + 1) * batch_size, len(lang_paragraphs))
                    batch = lang_paragraphs[start_idx:end_idx]
                    
                    print(f"      📦 Processing batch {batch_idx+1}/{total_batches} ({len(batch)} paragraphs)")
                    
                    # Translate the batch
                    translated_batch = batch_translate(
                        source_lang=lang,
                        target_lang=target_lang,
                        source_texts=batch,
                        country=country,
                        translation_style=translation_style,
                        custom_style_instructions=custom_style_instructions,
                        terminology_file=terminology_file
                    )
                    
                    # Update the translated paragraphs
                    for i, (orig_idx, _) in enumerate(para_indices[start_idx:end_idx]):
                        translated_paragraphs[orig_idx] = translated_batch[i]
        else:
            # Translate all paragraphs without language detection
            print(f"   🔄 Translating {len(paragraphs)} paragraphs from {source_lang} to {target_lang}")
            
            # Translate in batches
            total_batches = (len(paragraphs) - 1) // batch_size + 1
            
            for batch_idx in range(total_batches):
                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, len(paragraphs))
                batch = paragraphs[start_idx:end_idx]
                
                print(f"      📦 Processing batch {batch_idx+1}/{total_batches} ({len(batch)} paragraphs)")
                
                # Translate the batch
                translated_batch = batch_translate(
                    source_lang=source_lang,
                    target_lang=target_lang,
                    source_texts=batch,
                    country=country,
                    translation_style=translation_style,
                    custom_style_instructions=custom_style_instructions,
                    terminology_file=terminology_file
                )
                
                translated_paragraphs.extend(translated_batch)
        
        # Save the translated text to TXT file
        with open(output_path_txt, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(translated_paragraphs))
        
        # Create PDF with translated text
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # Register fonts that support multiple languages
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        except:
            print("Warning: DejaVuSans font not found, using default font")
        
        c = canvas.Canvas(output_path_pdf, pagesize=letter)
        c.setFont('DejaVuSans' if 'DejaVuSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica', 12)
        
        # Add translated text to PDF
        y = 750  # Start from top of page
        for paragraph in translated_paragraphs:
            # Split paragraph into lines that fit the page width
            words = paragraph.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                line_width = c.stringWidth(' '.join(current_line), 'DejaVuSans' if 'DejaVuSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica', 12)
                if line_width > 500:  # Page width minus margins
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Write lines to PDF
            for line in lines:
                if y < 50:  # Start new page if near bottom
                    c.showPage()
                    y = 750
                    c.setFont('DejaVuSans' if 'DejaVuSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica', 12)
                
                c.drawString(50, y, line)
                y -= 15  # Line spacing
        
        c.save()
        
        print(f"   ✅ Translation completed and saved to:")
        print(f"      PDF: {output_path_pdf}")
        print(f"      TXT: {output_path_txt}")
        return output_path_pdf, output_path_txt
        
    except Exception as e:
        print(f"❌ Error processing PDF: {str(e)}")
        return "", "" 