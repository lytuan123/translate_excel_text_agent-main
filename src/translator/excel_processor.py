"""
Excel Processor for Advanced Translation Suite
Handles Excel file reading, cell detection, and translation
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

# Import translator utilities
from .translator_core import batch_translate, detect_language


def clean_text(text: str) -> str:
    """Clean and normalize text before translation."""
    if not text or not isinstance(text, str):
        return ""
    text = ' '.join(text.split())  # Normalize whitespace
    return text.strip()


def should_translate(text: str) -> bool:
    """Check if a cell needs translation."""
    text = clean_text(text)
    if not text or len(text) < 2:
        return False
    if re.match(r'^[\d\s,.-]+$', text):  # Contains only numbers and number formatting characters
        return False
    if text.startswith('='):  # Excel formula
        return False
    return True


def process_excel(
    input_path: str,
    output_path: Optional[str] = None,
    source_lang: str = "English",
    target_lang: str = "Spanish",
    country: str = "",
    batch_size: int = 100,
    detect_languages: bool = True,
    translation_style: str = "General",
    custom_style_instructions: str = "",
    terminology_file: Optional[str] = None,
) -> str:
    """
    Process an Excel file: find text to translate, translate it, and save the result.
    
    Args:
        input_path: Path to the Excel file to translate
        output_path: Path where to save the translated file (if None, auto-generated)
        source_lang: Source language of the content (used if language detection is disabled)
        target_lang: Target language for translation
        country: Optional country context for translation style
        batch_size: Maximum number of cells to translate in one batch
        detect_languages: Whether to detect languages in different cells
        translation_style: Style of translation (e.g., "General", "Technical", "Literary")
        custom_style_instructions: Additional instructions for translation style
        terminology_file: Path to custom terminology file
        
    Returns:
        Path to the saved translated file
    """
    try:
        # Dynamic import to avoid unnecessary dependency if Excel not used
        import xlwings as xw
        
        # Create output file path if not provided
        if output_path is None:
            filename = os.path.basename(input_path)
            base_name, ext = os.path.splitext(filename)
            
            # Auto-generate output path
            dir_name = os.path.dirname(input_path)
            output_path = os.path.join(dir_name, f"{base_name}-{target_lang}{ext}")
        
        print(f"\n🔄 Processing file: {input_path}")
        print(f"   Source: {source_lang}, Target: {target_lang}, Country: {country}")
        
        # Open workbook with xlwings to preserve formatting
        app = xw.App(visible=False)
        wb = None
        
        try:
            wb = app.books.open(input_path)
            
            # Process each sheet
            for sheet in wb.sheets:
                print(f"📋 Processing sheet: {sheet.name}")
                
                # Collect data from cells that need translation
                texts_to_translate = []
                cell_references = []
                
                # For language detection
                language_groups = {} if detect_languages else None
                
                # Scan through used data range
                used_rng = sheet.used_range
                if used_rng.count > 1 or used_rng.value is not None:
                    for cell in used_rng:
                        # Check if cell value exists and should be translated
                        cell_value_str = str(cell.value) if cell.value is not None else ""
                        if cell_value_str and should_translate(cell_value_str):
                            clean_cell_text = clean_text(cell_value_str)
                            
                            if detect_languages:
                                # Detect language for this cell
                                detected_lang = detect_language(clean_cell_text)
                                
                                # Skip if already in target language
                                if detected_lang.lower() == target_lang.lower():
                                    print(f"   ⏩ Skipping cell {cell.address} (already in {detected_lang})")
                                    continue
                                
                                # Group by language
                                if detected_lang not in language_groups:
                                    language_groups[detected_lang] = []
                                language_groups[detected_lang].append((clean_cell_text, cell))
                            else:
                                # No language detection, just add to translation list
                                texts_to_translate.append(clean_cell_text)
                                cell_references.append(cell)
                else:
                    print(f"   ⚠️ Sheet '{sheet.name}' is empty or has no data.")
                
                # Process shapes with text
                try:
                    shapes_collection = sheet.api.Shapes
                    shapes_count = shapes_collection.Count
                    
                    if shapes_count > 0:
                        print(f"📊 Sheet '{sheet.name}' has {shapes_count} shapes to check")
                        
                        # Process each shape by index (Excel COM API indexes from 1)
                        for i in range(1, shapes_count + 1):
                            shape = None
                            try:
                                shape = shapes_collection.Item(i)
                                shape_text = None
                                
                                # Try multiple methods to get text from shape
                                # Method 1: TextFrame
                                try:
                                    if hasattr(shape, 'TextFrame'):
                                        if shape.TextFrame.HasText:
                                            shape_text = shape.TextFrame.Characters().Text
                                except Exception:
                                    pass
                                
                                # Method 2: TextFrame2
                                if not shape_text:
                                    try:
                                        if hasattr(shape, 'TextFrame2'):
                                            shape_text = shape.TextFrame2.TextRange.Text
                                    except Exception:
                                        pass
                                
                                # Method 3: AlternativeText
                                if not shape_text:
                                    try:
                                        if hasattr(shape, 'AlternativeText') and shape.AlternativeText:
                                            shape_text = shape.AlternativeText
                                    except Exception:
                                        pass
                                
                                # Method 4: OLEFormat (for OLE objects)
                                if not shape_text:
                                    try:
                                        if hasattr(shape, 'OLEFormat') and hasattr(shape.OLEFormat, 'Object'):
                                            if hasattr(shape.OLEFormat.Object, 'Text'):
                                                shape_text = shape.OLEFormat.Object.Text
                                    except Exception:
                                        pass
                                
                                # Method 5: TextEffect (for WordArt)
                                if not shape_text:
                                    try:
                                        if hasattr(shape, 'TextEffect') and hasattr(shape.TextEffect, 'Text'):
                                            shape_text = shape.TextEffect.Text
                                    except Exception:
                                        pass
                                
                                # If text is found, add to translation list
                                if shape_text and should_translate(shape_text):
                                    clean_shape_text = clean_text(shape_text)
                                    print(f"   💬 Shape {i}: Found text: {clean_shape_text[:30]}...")
                                    
                                    if detect_languages:
                                        # Detect language for this shape
                                        detected_lang = detect_language(clean_shape_text)
                                        
                                        # Skip if already in target language
                                        if detected_lang.lower() == target_lang.lower():
                                            print(f"   ⏩ Skipping shape {i} (already in {detected_lang})")
                                            continue
                                        
                                        # Group by language
                                        if detected_lang not in language_groups:
                                            language_groups[detected_lang] = []
                                        language_groups[detected_lang].append((clean_shape_text, ('shape', sheet, i)))
                                    else:
                                        # No language detection, just add to translation list
                                        texts_to_translate.append(clean_shape_text)
                                        cell_references.append(('shape', sheet, i))
                                    
                            except Exception as outer_e:
                                print(f"   ⚠️ Error processing shape {i}: {str(outer_e)}")
                                continue
                                
                except Exception as e:
                    print(f"   ⚠️ Error processing shapes on sheet '{sheet.name}': {str(e)}")
                
                # Translate and update content
                if detect_languages:
                    # Process each language group separately
                    for lang, items in language_groups.items():
                        if not items:
                            continue
                            
                        print(f"   🔄 Translating {len(items)} cells from {lang} to {target_lang}")
                        
                        # Extract texts and references for this language
                        lang_texts = [item[0] for item in items]
                        lang_refs = [item[1] for item in items]
                        
                        # Translate in batches
                        total_batches = (len(lang_texts) - 1) // batch_size + 1
                        
                        for i in range(0, len(lang_texts), batch_size):
                            batch_texts = lang_texts[i:i+batch_size]
                            batch_refs = lang_refs[i:i+batch_size]
                            current_batch_num = i // batch_size + 1
                            
                            print(f"   📦 Translating batch {current_batch_num}/{total_batches} ({len(batch_texts)} texts)")
                            
                            # Translate batch
                            translated_batch = batch_translate(
                                texts=batch_texts,
                                source_lang=lang,
                                target_lang=target_lang,
                                country=country,
                                translation_style=translation_style,
                                custom_style_instructions=custom_style_instructions,
                                terminology_file=terminology_file
                            )
                            
                            # Update translated content
                            print(f"   ✍️ Updating content for batch {current_batch_num}...")
                            for j, ref in enumerate(batch_refs):
                                if j < len(translated_batch) and translated_batch[j] is not None:
                                    try:
                                        # Update content based on reference type
                                        if isinstance(ref, tuple) and ref[0] == 'shape':
                                            # Handle shape updates
                                            _, sheet_obj, shape_index = ref
                                            try:
                                                shape_to_update = sheet_obj.api.Shapes.Item(shape_index)
                                                updated = False
                                                
                                                # Try different methods for updating shape text
                                                # Method 1: TextFrame
                                                try:
                                                    if hasattr(shape_to_update, 'TextFrame') and shape_to_update.TextFrame.HasText:
                                                        shape_to_update.TextFrame.Characters().Text = translated_batch[j]
                                                        updated = True
                                                except Exception:
                                                    pass
                                                    
                                                # Method 2: TextFrame2
                                                if not updated:
                                                    try:
                                                        if hasattr(shape_to_update, 'TextFrame2'):
                                                            shape_to_update.TextFrame2.TextRange.Text = translated_batch[j]
                                                            updated = True
                                                    except Exception:
                                                        pass
                                                        
                                                # Method 3: AlternativeText
                                                if not updated:
                                                    try:
                                                        if hasattr(shape_to_update, 'AlternativeText'):
                                                            shape_to_update.AlternativeText = translated_batch[j]
                                                            updated = True
                                                    except Exception:
                                                        pass
                                                        
                                                # Method 4: TextEffect (for WordArt)
                                                if not updated:
                                                    try:
                                                        if hasattr(shape_to_update, 'TextEffect') and hasattr(shape_to_update.TextEffect, 'Text'):
                                                            shape_to_update.TextEffect.Text = translated_batch[j]
                                                            updated = True
                                                    except Exception:
                                                        pass
                                                        
                                                # Method 5: OLEFormat
                                                if not updated:
                                                    try:
                                                        if hasattr(shape_to_update, 'OLEFormat') and hasattr(shape_to_update.OLEFormat, 'Object'):
                                                            if hasattr(shape_to_update.OLEFormat.Object, 'Text'):
                                                                shape_to_update.OLEFormat.Object.Text = translated_batch[j]
                                                                updated = True
                                                    except Exception:
                                                        pass
                                                        
                                                if updated:
                                                    print(f"   ✅ Updated text for shape {shape_index}")
                                                else:
                                                    print(f"   ⚠️ Could not update text for shape {shape_index}")
                                                    
                                            except Exception as update_err:
                                                print(f"   ⚠️ Error updating shape {shape_index}: {str(update_err)}")
                                        
                                        # Handle regular cell updates
                                        elif hasattr(ref, 'value'):
                                            # Is a cell
                                            ref.value = translated_batch[j]
                                        else:
                                            print(f"   ⚠️ Unknown reference type: {type(ref)}")
                                            
                                    except Exception as update_single_err:
                                        ref_info = f"Shape index {ref[2]}" if isinstance(ref, tuple) else f"Cell {ref.address}"
                                        print(f"   ⚠️ Could not update content for {ref_info}: {str(update_single_err)}")
                else:
                    # No language detection, process all cells with the specified source language
                    if not texts_to_translate:
                        print(f"   ✅ No text to translate on sheet '{sheet.name}'.")
                        continue
                    
                    total_batches = (len(texts_to_translate) - 1) // batch_size + 1
                    print(f"   📦 Preparing to translate {len(texts_to_translate)} text segments in {total_batches} batches.")
                    
                    for i in range(0, len(texts_to_translate), batch_size):
                        batch_texts = texts_to_translate[i:i+batch_size]
                        batch_refs = cell_references[i:i+batch_size]
                        current_batch_num = i // batch_size + 1
                        
                        print(f"   🔄 Translating batch {current_batch_num}/{total_batches} ({len(batch_texts)} texts)")
                        
                        # Translate batch - key function that connects to translator_core
                        translated_batch = batch_translate(
                            texts=batch_texts,
                            source_lang=source_lang,
                            target_lang=target_lang,
                            country=country,
                            translation_style=translation_style,
                            custom_style_instructions=custom_style_instructions,
                            terminology_file=terminology_file
                        )
                        
                        # Update translated content
                        print(f"   ✍️ Updating content for batch {current_batch_num}...")
                        for j, ref in enumerate(batch_refs):
                            if j < len(translated_batch) and translated_batch[j] is not None:
                                try:
                                    # Update content based on reference type
                                    if isinstance(ref, tuple) and ref[0] == 'shape':
                                        # Handle shape updates
                                        _, sheet_obj, shape_index = ref
                                        try:
                                            shape_to_update = sheet_obj.api.Shapes.Item(shape_index)
                                            updated = False
                                            
                                            # Try different methods for updating shape text
                                            # Method 1: TextFrame
                                            try:
                                                if hasattr(shape_to_update, 'TextFrame') and shape_to_update.TextFrame.HasText:
                                                    shape_to_update.TextFrame.Characters().Text = translated_batch[j]
                                                    updated = True
                                            except Exception:
                                                pass
                                                
                                            # Method 2: TextFrame2
                                            if not updated:
                                                try:
                                                    if hasattr(shape_to_update, 'TextFrame2'):
                                                        shape_to_update.TextFrame2.TextRange.Text = translated_batch[j]
                                                        updated = True
                                                except Exception:
                                                    pass
                                                    
                                            # Method 3: AlternativeText
                                            if not updated:
                                                try:
                                                    if hasattr(shape_to_update, 'AlternativeText'):
                                                        shape_to_update.AlternativeText = translated_batch[j]
                                                        updated = True
                                                except Exception:
                                                    pass
                                                    
                                            # Method 4: TextEffect (for WordArt)
                                            if not updated:
                                                try:
                                                    if hasattr(shape_to_update, 'TextEffect') and hasattr(shape_to_update.TextEffect, 'Text'):
                                                        shape_to_update.TextEffect.Text = translated_batch[j]
                                                        updated = True
                                                except Exception:
                                                    pass
                                                    
                                            # Method 5: OLEFormat
                                            if not updated:
                                                try:
                                                    if hasattr(shape_to_update, 'OLEFormat') and hasattr(shape_to_update.OLEFormat, 'Object'):
                                                        if hasattr(shape_to_update.OLEFormat.Object, 'Text'):
                                                            shape_to_update.OLEFormat.Object.Text = translated_batch[j]
                                                            updated = True
                                                except Exception:
                                                    pass
                                                    
                                            if updated:
                                                print(f"   ✅ Updated text for shape {shape_index}")
                                            else:
                                                print(f"   ⚠️ Could not update text for shape {shape_index}")
                                                
                                        except Exception as update_err:
                                            print(f"   ⚠️ Error updating shape {shape_index}: {str(update_err)}")
                                    
                                    # Handle regular cell updates
                                    elif hasattr(ref, 'value'):
                                        # Is a cell
                                        ref.value = translated_batch[j]
                                    else:
                                        print(f"   ⚠️ Unknown reference type: {type(ref)}")
                                        
                                except Exception as update_single_err:
                                    ref_info = f"Shape index {ref[2]}" if isinstance(ref, tuple) else f"Cell {ref.address}"
                                    print(f"   ⚠️ Could not update content for {ref_info}: {str(update_single_err)}")
            
            # Save file with original format
            print(f"\n💾 Saving translated file to: {output_path}")
            wb.save(output_path)
            print(f"✅ File saved successfully: {output_path}")
            
            return output_path
            
        except Exception as wb_process_err:
            print(f"❌ Error processing workbook: {str(wb_process_err)}")
            # Ensure workbook is closed if error occurs
            if wb is not None:
                try:
                    wb.close()
                except Exception:
                    pass
            return ""
            
        finally:
            # Always close the workbook and quit the app
            if wb is not None:
                try:
                    wb.close()
                except Exception:
                    pass
            try:
                app.quit()
            except Exception:
                pass
            
    except ImportError:
        print("❌ xlwings is not installed. Please install with: pip install xlwings>=0.30.0")
        return ""
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return ""


def process_directory(
    input_dir: str,
    output_dir: Optional[str] = None,
    source_lang: str = "English",
    target_lang: str = "Spanish",
    country: str = "",
    detect_languages: bool = True,
) -> List[str]:
    """
    Process all Excel files in a directory.
    
    Args:
        input_dir: Directory containing Excel files to translate
        output_dir: Directory where to save translated files (if None, uses input_dir)
        source_lang: Source language of the content
        target_lang: Target language for translation
        country: Optional country context for translation style
        detect_languages: Whether to detect languages in different cells
        
    Returns:
        List of paths to successfully translated files
    """
    import glob
    
    # Ensure directory path exists
    if not os.path.isdir(input_dir):
        print(f"❌ Directory does not exist: {input_dir}")
        return []
    
    # Use input_dir as output_dir if not specified
    if output_dir is None:
        output_dir = input_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all Excel files in the directory
    excel_files = glob.glob(os.path.join(input_dir, "*.xlsx")) + glob.glob(os.path.join(input_dir, "*.xls"))
    
    if not excel_files:
        print(f"⚠️ No Excel files found in directory: {input_dir}")
        return []
    
    print(f"🔍 Found {len(excel_files)} Excel files in input directory")
    
    # Process each file
    successful_files = []
    failed_files = []
    
    for file_path in excel_files:
        # Skip temporary files
        if os.path.basename(file_path).startswith('~$'):
            print(f"   ⏩ Skipping temporary file: {os.path.basename(file_path)}")
            continue
        
        # Create output path
        filename = os.path.basename(file_path)
        base_name, ext = os.path.splitext(filename)
        output_path = os.path.join(output_dir, f"{base_name}-{target_lang}{ext}")
        
        # Process the file
        result_path = process_excel(
            input_path=file_path,
            output_path=output_path,
            source_lang=source_lang,
            target_lang=target_lang,
            country=country,
            detect_languages=detect_languages
        )
        
        if result_path:
            successful_files.append(result_path)
        else:
            failed_files.append(file_path)
    
    # Print summary
    print("\n--- Directory processing completed ---")
    print(f"✅ Successfully translated: {len(successful_files)} files")
    
    if failed_files:
        print(f"❌ Failed to translate: {len(failed_files)} files")
        for file in failed_files:
            print(f"   - {os.path.basename(file)}")
    
    return successful_files 