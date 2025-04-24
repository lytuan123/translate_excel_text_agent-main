# -*- coding: utf-8 -*-
"""Module for processing PDF files using OCR."""

import pytesseract
from pdf2image import convert_from_path, exceptions as pdf2image_exceptions
from PIL import Image
import os

def process_pdf_ocr(pdf_file_path: str, lang_code: str) -> tuple[str, str | None]:
    """Processes a PDF file, extracts text using OCR, and returns the text.

    Args:
        pdf_file_path: Path to the PDF file.
        lang_code: Tesseract language code (e.g., 'eng', 'vie').

    Returns:
        A tuple containing:
        - The extracted text (str). Returns an empty string if no text is found
          or if an error occurs during processing steps that can be recovered from.
        - An error message (str | None). Returns None if successful, otherwise
          returns a string describing the error that prevented full processing.
    """
    extracted_text = ""
    error_message = None
    images = []
    page_errors = [] # Keep track of errors per page

    try:
        # --- Task [Backend-2]: Convert PDF pages to images --- 
        try:
            # dpi controls the resolution, higher values might improve OCR but increase processing time/memory
            # poppler_path can be specified if poppler is not in PATH
            images = convert_from_path(pdf_file_path, dpi=200) # Use dpi=200 as a starting point
        except pdf2image_exceptions.PDFInfoNotInstalledError:
            error_message = "Error: pdfinfo command (part of Poppler) not found. Please install Poppler and add it to PATH."
            print("[OCR Setup Error] Poppler not found or not in PATH.")
            # Return early as we cannot proceed without Poppler
            return extracted_text, error_message
        except pdf2image_exceptions.PDFPageCountError:
            error_message = "Error: Could not determine the number of pages in the PDF. It might be corrupted or password-protected."
            print(f"[OCR Error] Could not get page count for {pdf_file_path}")
            # Return early if page count fails
            return extracted_text, error_message
        except pdf2image_exceptions.PDFSyntaxError:
             error_message = "Error: PDF file seems to be corrupted or has syntax errors."
             print(f"[OCR Error] PDF syntax error in {pdf_file_path}")
             # Return early for syntax errors
             return extracted_text, error_message
        except Exception as pdf_err: # Catch other pdf2image specific errors
             error_message = f"Error during PDF to image conversion: {str(pdf_err)}"
             print(f"[OCR Error] PDF to Image conversion failed: {pdf_err}")
             # Return early for conversion errors
             return extracted_text, error_message

        if not images:
            if not error_message: # Only set error if not already set by exceptions
                 error_message = "PDF file seems to be empty or could not be converted to images."
            return extracted_text, error_message
        # --------------------------------------------------------

        print(f"Successfully converted {len(images)} pages from {pdf_file_path}. Starting OCR...")

        # --- Task [Backend-3]: Perform OCR on each image --- 
        all_page_text = []
        for i, image in enumerate(images):
            page_num = i + 1
            try:
                # Perform OCR using pytesseract
                # Add page segmentation mode (psm) if needed, e.g., config='--psm 6'
                page_text = pytesseract.image_to_string(image, lang=lang_code)
                all_page_text.append(page_text)
                print(f"   Processed OCR for page {page_num}")
            except pytesseract.TesseractNotFoundError:
                error_message = "Error: Tesseract command not found. Please install Tesseract and ensure it's in your PATH."
                print("[OCR Setup Error] Tesseract not found or not in PATH.")
                # This is a fatal error for OCR, return immediately
                return "", error_message
            except pytesseract.TesseractError as tess_err:
                # Handle errors like invalid language code or Tesseract failing
                page_error_msg = f"Tesseract error on page {page_num}: {str(tess_err)}"
                print(f"[OCR Warning] {page_error_msg}")
                page_errors.append(page_error_msg)
                all_page_text.append(f"[OCR Error on page {page_num}]\n") # Add placeholder
                # Continue processing other pages
            except Exception as ocr_err:
                # Catch other unexpected errors during OCR for a specific page
                page_error_msg = f"Unexpected error during OCR on page {page_num}: {str(ocr_err)}"
                print(f"[OCR Warning] {page_error_msg}")
                page_errors.append(page_error_msg)
                all_page_text.append(f"[OCR Error on page {page_num}]\n") # Add placeholder
                # Continue processing other pages
        # -----------------------------------------------------

        # Placeholder for combining text and final checks (Task Backend-4)
        # Now 'all_page_text' list holds text (or error placeholder) for each page
        extracted_text = "\n\n---\n\n".join(all_page_text) # Join pages with a separator

        if not extracted_text and not error_message and not page_errors:
            error_message = "No text could be extracted, although the PDF was processed."
        elif page_errors:
             # If there were page-specific errors, append them to the main error message
             consolidated_page_errors = "\n".join(page_errors)
             if error_message:
                 error_message += f"\n\nAdditionally, the following page-specific errors occurred:\n{consolidated_page_errors}"
             else:
                  error_message = f"OCR completed with errors on some pages:\n{consolidated_page_errors}"

    except FileNotFoundError:
        error_message = f"Error: PDF file not found at {pdf_file_path}"
    except Exception as e:
        # Catch other potential errors during setup or basic checks
        error_message = f"An unexpected error occurred before/during image conversion: {str(e)}"
        print(f"[OCR Error] Unexpected error in process_pdf_ocr: {e}")

    return extracted_text.strip(), error_message

# Example usage (for testing purposes, can be removed later)
if __name__ == '__main__':
    # Create a dummy PDF path for testing structure
    # In a real scenario, you would provide a path to an actual PDF
    dummy_pdf = "dummy_test.pdf"
    # Create a dummy file to avoid FileNotFoundError in basic test
    # NOTE: This dummy file IS NOT a valid PDF and will cause pdf2image errors
    # You need a real PDF to test the conversion part properly.
    # print(f"Creating dummy file: {dummy_pdf}")
    # with open(dummy_pdf, 'w') as f:
    #     f.write("dummy content")

    print(f"Testing OCR processor function call (will likely fail without a real PDF)")
    # Replace 'dummy_pdf' with path to a real PDF for actual testing
    # text, error = process_pdf_ocr('path/to/your/test.pdf', 'eng')
    text, error = process_pdf_ocr(dummy_pdf, 'eng') # Expected to fail

    if error:
        print(f"Error reported: {error}") # Expected behavior for dummy file
    else:
        print("Processing function called successfully. Text:")
        print(f"'{text}'")

    # Clean up dummy file if it was created
    # if os.path.exists(dummy_pdf):
    #      print(f"Removing dummy file: {dummy_pdf}")
    #      os.remove(dummy_pdf)
    print("\nReminder: To test PDF conversion, replace 'dummy_pdf' with a real PDF path.") 