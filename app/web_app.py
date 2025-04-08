#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Advanced Translation Suite - Web UI
Combined interface for text, document, and Excel translation
"""

import os
import re
import sys
import tempfile
from pathlib import Path
from glob import glob
from typing import Tuple, Optional, List, Dict, Any, Union

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Gradio
import gradio as gr


# Import our translator module
from src.translator.translator_core import TRANSLATION_STYLES
from src.translator import (
    model_load,
    simple_translator,
    process_excel,
    num_tokens_in_string,
    extract_docx,
    extract_pdf,
    extract_text,
    diff_texts,
    #TRANSLATION_STYLES
)

# Import PDF processor
from src.translator.pdf_processor import process_pdf


# File extraction utilities
def extract_file_content(file_path: str) -> str:
    """Extract text content from a file based on its extension."""
    file_type = file_path.split(".")[-1].lower()
    
    if file_type == "pdf":
        content = extract_pdf(file_path)
    elif file_type == "docx":
        content = extract_docx(file_path)
    elif file_type in ["txt", "py", "json", "cpp", "md", "html", "css", "js"]:
        content = extract_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    # Remove empty lines
    return re.sub(r"(?m)^\s*$\n?", "", content)


# Translation function (handles both text and file uploads)
def translate_content(
    # API configuration
    endpoint: str,
    base_url: str,
    model: str,
    api_key: str,
    second_endpoint: bool,
    endpoint2: str,
    base_url2: str,
    model2: str,
    api_key2: str,
    
    # Translation parameters
    source_lang: str,
    target_lang: str,
    source_text: str,
    country: str,
    max_tokens: int,
    temperature: float,
    rpm: int,
    translation_style: str,
    custom_style_instructions: str,
    terminology_file: Optional[tempfile._TemporaryFileWrapper] = None,
    
    # For file uploads
    upload_file: Optional[tempfile._TemporaryFileWrapper] = None,
):
    """Translate text or document content."""
    if not source_text and not upload_file:
        raise gr.Error("Please enter text or upload a file to translate.")
    
    if source_lang == target_lang:
        raise gr.Error("Source and target languages cannot be the same.")
    
    # Load model configuration
    try:
        model_load(
            endpoint=endpoint,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            rpm=rpm
        )
    except Exception as e:
        raise gr.Error(f"Failed to initialize translation model: {e}")
    
    # If a file was uploaded, extract its content
    if upload_file and not source_text:
        try:
            source_text = extract_file_content(upload_file.name)
        except Exception as e:
            raise gr.Error(f"Error extracting text from file: {e}")
    
    # Remove empty lines and clean up text
    source_text = re.sub(r"(?m)^\s*$\n?", "", source_text)
    
    # Check for empty text
    if not source_text:
        raise gr.Error("No text to translate. Please check your input.")
    
    # Get terminology file path if provided
    terminology_path = None
    if terminology_file:
        terminology_path = terminology_file.name
    
    # Perform translation
    if second_endpoint:
        # Load second model for reflection/improvement
        try:
            # Save first model results
            init_translation = simple_translator(
                source_lang=source_lang,
                target_lang=target_lang,
                source_text=source_text,
                country=country,
                max_tokens=max_tokens,
                full_response=False,
                translation_style=translation_style,
                custom_style_instructions=custom_style_instructions,
                terminology_file=terminology_path
            )
            
            # Switch to second model for reflection
            model_load(
                endpoint=endpoint2,
                model=model2,
                api_key=api_key2,
                base_url=base_url2,
                temperature=temperature,
                rpm=rpm
            )
            
            # Get full translation with reflection using the second model
            _, reflection, final_translation = simple_translator(
                source_lang=source_lang,
                target_lang=target_lang,
                source_text=source_text,
                country=country,
                max_tokens=max_tokens,
                full_response=True,
                translation_style=translation_style,
                custom_style_instructions=custom_style_instructions,
                terminology_file=terminology_path
            )
        except Exception as e:
            raise gr.Error(f"Error in multi-model translation: {e}")
    else:
        # Single model translation
        try:
            init_translation, reflection, final_translation = simple_translator(
                source_lang=source_lang,
                target_lang=target_lang,
                source_text=source_text,
                country=country,
                max_tokens=max_tokens,
                full_response=True,
                translation_style=translation_style,
                custom_style_instructions=custom_style_instructions,
                terminology_file=terminology_path
            )
        except Exception as e:
            raise gr.Error(f"Error in translation: {e}")
    
    # Create diff visualization
    final_diff = gr.HighlightedText(
        diff_texts(init_translation, final_translation),
        label="Translation Differences",
        combine_adjacent=True,
        show_legend=True,
        visible=True,
        color_map={"removed": "red", "added": "green"},
    )
    
    return init_translation, reflection, final_translation, final_diff


def translate_pdf(
    # API configuration
    endpoint: str,
    base_url: str,
    model: str,
    api_key: str,
    
    # Translation parameters
    source_lang: str,
    target_lang: str,
    country: str,
    temperature: float,
    rpm: int,
    detect_languages: bool,
    translation_style: str,
    custom_style_instructions: str,
    terminology_file: Optional[tempfile._TemporaryFileWrapper] = None,
    
    # PDF file upload
    pdf_file: Optional[tempfile._TemporaryFileWrapper] = None,
) -> Tuple[str, str]:
    """Process and translate a PDF file."""
    if not pdf_file:
        raise gr.Error("Please upload a PDF file.")
    
    if source_lang == target_lang:
        raise gr.Error("Source and target languages cannot be the same.")
    
    # Check file extension
    file_path = pdf_file.name
    if not file_path:
        raise gr.Error("Invalid PDF file. Please try uploading again.")
        
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension != '.pdf':
        raise gr.Error("Please upload a PDF file (.pdf)")
    
    # Create temporary output file
    filename = os.path.basename(file_path)
    base_name, ext = os.path.splitext(filename)
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{base_name}-{target_lang}")
    
    # Load model configuration
    try:
        model_load(
            endpoint=endpoint,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            rpm=rpm
        )
    except Exception as e:
        raise gr.Error(f"Failed to initialize translation model: {e}")
    
    # Get terminology file path if provided
    terminology_path = None
    if terminology_file:
        terminology_path = terminology_file.name
    
    # Process PDF file
    try:
        pdf_path, txt_path = process_pdf(
            input_path=file_path,
            output_path=output_path,
            source_lang=source_lang,
            target_lang=target_lang,
            country=country,
            detect_languages=detect_languages,
            translation_style=translation_style,
            custom_style_instructions=custom_style_instructions,
            terminology_file=terminology_path
        )
        
        if not txt_path or not os.path.exists(txt_path):
            raise gr.Error("Translation failed. Please check the logs.")
            
        return txt_path, f"PDF file translated successfully. Text version available for download."
        
    except Exception as e:
        raise gr.Error(f"Error translating PDF file: {str(e)}")


def translate_excel(
    excel_file: str,
    source_lang: str,
    target_lang: str,
    country: str,
    translation_style: str,
    custom_style_instructions: str,
    terminology_file: str,
    api_key: str,
    endpoint: str,
    model: str,
    temperature: float,
    rpm: int,
    max_tokens: int,
    json_mode: bool,
    base_url: str
) -> Tuple[str, str]:
    """Translate Excel file content."""
    try:
        if not excel_file:
            raise gr.Error("Please upload an Excel file.")
            
        # Load model configuration
        model_config = model_load(
            endpoint=endpoint,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            rpm=rpm,
            json_mode=json_mode
        )
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename
        input_filename = os.path.basename(excel_file)
        base_name, ext = os.path.splitext(input_filename)
        output_filename = f"{base_name}-{target_lang}{ext}"
        output_path = os.path.join(output_dir, output_filename)
        
        # Process Excel file
        result_path = process_excel(
            input_path=excel_file,
            output_path=output_path,
            source_lang=source_lang,
            target_lang=target_lang,
            country=country,
            translation_style=translation_style,
            custom_style_instructions=custom_style_instructions,
            terminology_file=terminology_file
        )
        
        if not result_path or not os.path.exists(result_path):
            raise gr.Error("Failed to process Excel file.")
            
        # Create text preview
        preview_text = f"Excel file translated from {source_lang} to {target_lang}.\n"
        preview_text += f"Translation style: {translation_style}\n"
        if custom_style_instructions:
            preview_text += f"Custom instructions: {custom_style_instructions}\n"
        if terminology_file:
            preview_text += f"Custom terminology file used: {os.path.basename(terminology_file)}\n"
        preview_text += f"\nTranslated file saved as: {os.path.basename(result_path)}"
        
        return result_path, preview_text
        
    except Exception as e:
        raise gr.Error(f"Error translating Excel: {str(e)}")


def update_model_selection(endpoint: str) -> Tuple[gr.update, gr.update]:
    """Update model dropdown and base URL field based on selected endpoint."""
    endpoint_model_map = {
        "Groq": "llama3-70b-8192",
        "OpenAI": "gpt-4o",
        "TogetherAI": "Qwen/Qwen2-72B-Instruct", 
        "Ollama": "llama3",
        "CUSTOM": "",
    }
    
    # Show/hide base URL field
    if endpoint == "CUSTOM":
        base_url_update = gr.update(visible=True)
    else:
        base_url_update = gr.update(visible=False)
    
    # Update default model
    model_update = gr.update(value=endpoint_model_map[endpoint])
    
    return model_update, base_url_update


def enable_second_endpoint(use_second: bool) -> gr.update:
    """Show/hide the second endpoint configuration section."""
    return gr.update(visible=use_second)


def export_text(text: str) -> gr.update:
    """Prepare text for export to file."""
    if text:
        os.makedirs("outputs", exist_ok=True)
        base_count = len(glob(os.path.join("outputs", "*.txt")))
        file_path = os.path.join("outputs", f"{base_count:06d}.txt")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
            
        return gr.update(value=file_path, visible=True)
    else:
        return gr.update(visible=False)


def switch_languages(
    source_lang: str, source_text: str, target_lang: str, output_final: str
) -> Tuple[gr.update, gr.update, gr.update, gr.update]:
    """Switch source and target languages."""
    if output_final:
        return (
            gr.update(value=target_lang),
            gr.update(value=output_final),
            gr.update(value=source_lang),
            gr.update(value=source_text),
        )
    else:
        return (
            gr.update(value=target_lang),
            gr.update(value=source_text),
            gr.update(value=source_lang),
            gr.update(value=""),
        )


# UI definitions
TITLE = """
    <div style="display: inline-flex;">
        <div style="margin-left: 6px; font-size:32px; color: #6366f1">
            <b>Advanced Translation Suite</b> - Text & Excel Translation with AI
        </div>
    </div>
"""

CSS = """
    h1 {
        text-align: center;
        display: block;
        height: 10vh;
        align-content: center;
    }
    footer {
        visibility: hidden;
    }
    .menu_btn {
        width: 48px;
        height: 48px;
        max-width: 48px;
        min-width: 48px;
        padding: 0px;
        background-color: transparent;
        border: none;
        cursor: pointer;
        position: relative;
        box-shadow: none;
    }
    .menu_btn::before,
    .menu_btn::after {
        content: '';
        position: absolute;
        width: 30px;
        height: 3px;
        background-color: #4f46e5;
        transition: transform 0.3s ease;
    }
    .menu_btn::before {
        top: 12px;
        box-shadow: 0 8px 0 #6366f1;
    }
    .menu_btn::after {
        bottom: 16px;
    }
    .menu_btn.active::before {
        transform: translateY(8px) rotate(45deg);
        box-shadow: none;
    }
    .menu_btn.active::after {
        transform: translateY(-8px) rotate(-45deg);
    }
    .lang {
        max-width: 100px;
        min-width: 100px;
    }
"""

JS = """
    function () {
        const menu_btn = document.getElementById('menu');
        menu_btn.classList.toggle('active');
    }
"""


def create_ui():
    """Create and configure the web UI."""
    with gr.Blocks(theme="soft", css=CSS, fill_height=True) as demo:
        with gr.Row():
            visible = gr.State(value=True)
            menu_btn = gr.Button(
                value="", elem_classes="menu_btn", elem_id="menu", size="sm"
            )
            gr.HTML(TITLE)
            
        with gr.Row():
            # Common sidebar for configuration
            with gr.Column(scale=1) as menubar:
                # Primary model configuration
                endpoint = gr.Dropdown(
                    label="Translation Service",
                    choices=["OpenAI", "Groq", "TogetherAI", "Ollama", "CUSTOM"],
                    value="OpenAI",
                )
                
                use_second_endpoint = gr.Checkbox(
                    label="Use Additional Model for Refinement",
                    info="Use a second model for reflection and improvement",
                )
                
                model = gr.Textbox(
                    label="Model",
                    value="gpt-4o",
                )
                
                api_key = gr.Textbox(
                    label="API Key",
                    type="password",
                )
                
                base_url = gr.Textbox(
                    label="Base URL",
                    visible=False
                )
                
                # Secondary model configuration
                with gr.Column(visible=False) as second_endpoint_config:
                    endpoint2 = gr.Dropdown(
                        label="Secondary Service",
                        choices=["OpenAI", "Groq", "TogetherAI", "Ollama", "CUSTOM"],
                        value="OpenAI",
                    )
                    
                    model2 = gr.Textbox(
                        label="Secondary Model",
                        value="gpt-4o",
                    )
                    
                    api_key2 = gr.Textbox(
                        label="Secondary API Key",
                        type="password",
                    )
                    
                    base_url2 = gr.Textbox(
                        label="Secondary Base URL",
                        visible=False
                    )
                
                # Language configuration
                with gr.Row():
                    source_lang = gr.Textbox(
                        label="Source Language",
                        value="English",
                        elem_classes="lang",
                    )
                    target_lang = gr.Textbox(
                        label="Target Language",
                        value="Vietnames",
                        elem_classes="lang",
                    )
                
                switch_btn = gr.Button(value="🔄️")
                
                country = gr.Textbox(
                    label="Target Country",
                    value="Vietnames",
                    max_lines=1,
                    info="Localization context (e.g., Vietnames,Spain, Mexico, Argentina)"
                )
                
                # Translation style configuration
                translation_style = gr.Dropdown(
                    label="Translation Style",
                    choices=list(TRANSLATION_STYLES.keys()),
                    value="General",
                    info="Select the style of translation (e.g., Literary, Technical, Financial)"
                )
                
                custom_style_instructions = gr.Textbox(
                    label="Custom Style Instructions",
                    placeholder="Enter additional instructions for translation style (e.g., 'Use formal language', 'Maintain the author's poetic style')",
                    lines=3
                )
                
                terminology_file = gr.File(
                    label="Custom Terminology File (format: source_term=target_term, one per line)",
                    file_types=[".txt"],
                    type="filepath"
                )
                
                # Advanced settings
                with gr.Accordion("Advanced Options", open=False):
                    max_tokens = gr.Slider(
                        label="Max Tokens Per Chunk",
                        minimum=512,
                        maximum=4096,
                        value=1000,
                        step=8,
                    )
                    
                    temperature = gr.Slider(
                        label="Temperature",
                        minimum=0,
                        maximum=1.0,
                        value=0.3,
                        step=0.1,
                    )
                    
                    rpm = gr.Slider(
                        label="Requests Per Minute",
                        minimum=1,
                        maximum=1000,
                        value=60,
                        step=1,
                    )
                    
                    detect_languages = gr.Checkbox(
                        label="Detect Languages Automatically",
                        value=True,
                        info="Detect different languages in the document and translate each appropriately"
                    )
                    
                    json_mode = gr.Checkbox(
                        label="JSON Mode",
                        value=False,
                        info="Enable JSON mode for structured output"
                    )
                
            # Main content area with tabs
            with gr.Column(scale=4):
                # Main tabs
                with gr.Tabs() as main_tabs:
                    # Text translation tab
                    with gr.TabItem("Text Translation"):
                        source_text = gr.Textbox(
                            label="Source Text",
                            value="If one advances confidently in the direction of his dreams, and endeavors to live the life which he has imagined, he will meet with a success unexpected in common hours.",
                            lines=12,
                        )
                        
                        upload_btn = gr.UploadButton(
                            label="Upload Document", 
                            file_types=["text", "pdf", "docx"]
                        )
                        
                        # Text translation output tabs
                        with gr.Tabs():
                            with gr.TabItem("Final Translation"):
                                output_final = gr.Textbox(
                                    label="Final Translation", 
                                    lines=12, 
                                    show_copy_button=True
                                )
                                
                            with gr.TabItem("Initial Draft"):
                                output_init = gr.Textbox(
                                    label="Initial Translation Draft", 
                                    lines=12, 
                                    show_copy_button=True
                                )
                                
                            with gr.TabItem("Reflection"):
                                output_reflect = gr.Textbox(
                                    label="Translation Analysis", 
                                    lines=12, 
                                    show_copy_button=True
                                )
                                
                            with gr.TabItem("Differences"):
                                output_diff = gr.HighlightedText(visible=False)
                        
                        with gr.Row():
                            submit_text = gr.Button(value="Translate Text")
                            export = gr.DownloadButton(visible=False)
                            clear_text = gr.ClearButton([source_text, output_init, output_reflect, output_final])
                            cancel_text = gr.Button(value="Cancel", visible=False)
                    
                    # PDF translation tab
                    with gr.TabItem("Dịch PDF"):
                        pdf_upload = gr.File(
                            label="Tải lên tệp PDF",
                            file_types=[".pdf"],
                            type="filepath"
                        )
                        
                        pdf_message = gr.Textbox(
                            label="Trạng thái",
                            interactive=False
                        )
                        
                        pdf_output = gr.File(
                            label="Văn bản PDF đã dịch",
                            interactive=False
                        )
                        
                        with gr.Row():
                            submit_pdf = gr.Button(value="Dịch Pdf")
                            clear_pdf = gr.ClearButton([pdf_upload, pdf_output, pdf_message])
                    
                    # Excel translation tab
                    with gr.TabItem("Dịch excel"):
                        excel_upload = gr.File(
                            label="Tải tệp excel lên",
                            file_types=[".xlsx", ".xls"],
                            type="filepath"
                        )
                        
                        excel_message = gr.Textbox(
                            label="Trạng thái",
                            interactive=False
                        )
                        
                        excel_output = gr.File(
                            label="Tệp excel đã dịch",
                            interactive=False
                        )
                        
                        with gr.Row():
                            submit_excel = gr.Button(value="Dịch excel")
                            clear_excel = gr.ClearButton([excel_upload, excel_output, excel_message])
                    
                    # Ollama model tab
                    with gr.TabItem("Ollama Model"):
                        ollama_prompt = gr.Textbox(label="Nhập lời nhắc của bạn")
                        ollama_output = gr.Textbox(label="Model Phản hồi", interactive=False)

                        def handle_ollama_request(prompt):
                            return query_ollama("your_model_name", prompt)

                        ollama_button = gr.Button("Run Ollama")
                        ollama_button.click(handle_ollama_request, inputs=[ollama_prompt], outputs=[ollama_output])
        
        # Set up event handlers
        
        # UI visibility and model selection
        menu_btn.click(
            fn=lambda x: (not x, gr.update(visible=not x)),
            inputs=visible,
            outputs=[visible, menubar],
            js=JS
        )
        
        # Model selection handlers
        endpoint.change(
            fn=update_model_selection,
            inputs=[endpoint],
            outputs=[model, base_url]
        )
        
        endpoint2.change(
            fn=update_model_selection,
            inputs=[endpoint2],
            outputs=[model2, base_url2]
        )
        
        # Second endpoint visibility
        use_second_endpoint.change(
            fn=enable_second_endpoint,
            inputs=[use_second_endpoint],
            outputs=[second_endpoint_config]
        )
        
        # Language switching
        switch_btn.click(
            fn=switch_languages,
            inputs=[source_lang, source_text, target_lang, output_final],
            outputs=[source_lang, source_text, target_lang, output_final],
        )
        
        # Document upload handling
        upload_btn.upload(
            fn=extract_file_content,
            inputs=[upload_btn],
            outputs=[source_text]
        )
        
        # Text translation
        text_translation = submit_text.click(
            fn=translate_content,
            inputs=[
                endpoint, base_url, model, api_key,
                use_second_endpoint, endpoint2, base_url2, model2, api_key2,
                source_lang, target_lang, source_text, country,
                max_tokens, temperature, rpm,
                translation_style, custom_style_instructions, terminology_file,
                upload_btn
            ],
            outputs=[output_init, output_reflect, output_final, output_diff]
        )
        
        # PDF translation
        pdf_translation = submit_pdf.click(
            fn=translate_pdf,
            inputs=[
                endpoint, base_url, model, api_key,
                source_lang, target_lang, country,
                temperature, rpm, detect_languages,
                translation_style, custom_style_instructions, terminology_file,
                pdf_upload
            ],
            outputs=[pdf_output, pdf_message]
        )
        
        # Excel translation
        excel_translation = submit_excel.click(
            fn=translate_excel,
            inputs=[
                excel_upload,
                source_lang, target_lang, country,
                translation_style, custom_style_instructions, terminology_file,
                api_key, endpoint, model, temperature, rpm,
                max_tokens, json_mode, base_url
            ],
            outputs=[excel_output, excel_message]
        )
        
        # Text export
        output_final.change(
            fn=export_text,
            inputs=[output_final],
            outputs=[export]
        )
        
        # Cancel buttons visibility
        submit_text.click(
            fn=lambda: gr.update(visible=True),
            outputs=[cancel_text]
        )
        
        cancel_text.click(
            fn=lambda: None,
            cancels=[text_translation]
        )
        
        # Reset cancel button after completion
        output_diff.change(
            fn=lambda: gr.update(visible=False),
            outputs=[cancel_text]
        )
        
    return demo


if __name__ == "__main__":
    # Import required utilities for file extraction
    import src.translator.document_utils
    
    # Create and launch the UI
    demo = create_ui()
    demo.queue(api_open=False).launch(
        share=True,
        show_api=False,
        server_name="0.0.0.0"
    )