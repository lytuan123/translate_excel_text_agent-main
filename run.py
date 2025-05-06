#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Advanced Translation Suite - Entry Point
Script to launch the translation suite with various options
"""

import os
import sys
import argparse

def main():
    """Main entry point for the Advanced Translation Suite."""
    parser = argparse.ArgumentParser(
        description="Advanced Translation Suite - AI-powered text and Excel translation",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Define command groups
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Web UI command
    web_parser = subparsers.add_parser("web", help="Launch the web interface")
    web_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    web_parser.add_argument("--port", type=int, default=7860, help="Port to bind to (default: 7860)")
    web_parser.add_argument("--share", action="store_true", help="Create a shareable link")
    
    # Excel command
    excel_parser = subparsers.add_parser("excel", help="Translate Excel files")
    excel_parser.add_argument("--source", required=True, help="Source language (e.g., English)")
    excel_parser.add_argument("--target", required=True, help="Target language (e.g., Spanish)")
    excel_parser.add_argument("--country", default="", help="Target country for localization")
    
    excel_input = excel_parser.add_mutually_exclusive_group(required=True)
    excel_input.add_argument("--file", help="Excel file to translate")
    excel_input.add_argument("--dir", help="Directory of Excel files to translate")
    
    excel_parser.add_argument("--output", help="Output file or directory")
    excel_parser.add_argument("--endpoint", choices=["OpenAI", "Groq", "TogetherAI", "Ollama", "CUSTOM"], 
                              default="OpenAI", help="Model provider")
    excel_parser.add_argument("--model", help="Model name (defaults to provider's recommended model)")
    excel_parser.add_argument("--apikey", help="API key (will use from .env if not provided)")
    
    # Text command
    text_parser = subparsers.add_parser("text", help="Translate text directly from command line")
    text_parser.add_argument("--source", required=True, help="Source language (e.g., English)")
    text_parser.add_argument("--target", required=True, help="Target language (e.g., Spanish)")
    text_parser.add_argument("--input", help="Input text file (if not provided, will use stdin)")
    text_parser.add_argument("--output", help="Output text file (if not provided, will print to stdout)")
    text_parser.add_argument("--country", default="", help="Target country for localization")
    text_parser.add_argument("--endpoint", choices=["OpenAI", "Groq", "TogetherAI", "Ollama", "CUSTOM"], 
                             default="OpenAI", help="Model provider")
    text_parser.add_argument("--model", help="Model name (defaults to provider's recommended model)")
    text_parser.add_argument("--apikey", help="API key (will use from .env if not provided)")
    text_parser.add_argument("--type", choices=["general", "technical", "literary", "business", "legal", "medical"],
                             default="general", help="Type of content to translate")
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == "web":
        # Launch web interface
        print(f"🚀 Launching web interface on http://{args.host}:{args.port}")
        print("Press Ctrl+C to exit")
        
        # Add app directory to path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Launch web app
        try:
            import gradio as gr
            from app.web_app import create_ui
            
            # Create the UI
            demo = create_ui()
            
            # Launch the app
            demo.queue(api_open=False).launch(
                server_name=args.host,
                server_port=args.port,
                share=args.share,
                show_api=False
            )
            
            return 0
            
        except ImportError as e:
            print(f"❌ Error: {e}")
            print("Please install the required packages: pip install -r requirements.txt")
            return 1
        
    elif args.command == "excel":
        # Check if we need to set a default model based on endpoint
        model = args.model
        if not model:
            endpoint_model_map = {
                "Groq": "llama3-70b-8192",
                "Gemini": "gemini-2.5-flash-preview-04-17",
                "OpenAI": "gpt-4o",
                "TogetherAI": "Qwen/Qwen2-72B-Instruct", 
                "Ollama": "llama3",
                "CUSTOM": "",
            }
            model = endpoint_model_map.get(args.endpoint, "gpt-4o")
        
        # Add directory to path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        try:
            # Import needed modules
            from app.excel_translator_cli import main as excel_main
            
            # Prepare sys.argv for the excel_translator_cli
            sys.argv = [
                sys.argv[0],
                "--source", args.source,
                "--target", args.target,
                "--endpoint", args.endpoint,
                "--model", model,
            ]
            
            # Add optional arguments
            if args.country:
                sys.argv.extend(["--country", args.country])
            if args.apikey:
                sys.argv.extend(["--apikey", args.apikey])
            if args.file:
                sys.argv.extend(["--file", args.file])
            if args.dir:
                sys.argv.extend(["--dir", args.dir])
            if args.output:
                sys.argv.extend(["--output", args.output])
            
            # Run the Excel CLI
            return excel_main()
            
        except ImportError as e:
            print(f"❌ Error: {e}")
            print("Please install the required packages: pip install -r requirements.txt")
            return 1
        
    elif args.command == "text":
        # Get input text
        if args.input:
            try:
                with open(args.input, 'r', encoding='utf-8') as f:
                    source_text = f.read()
            except Exception as e:
                print(f"❌ Error reading input file: {e}")
                return 1
        else:
            print("Enter text to translate (press Ctrl+D when finished):")
            source_text = sys.stdin.read()
        
        # Check if we need to set a default model based on endpoint
        model = args.model
        if not model:
            endpoint_model_map = {
                "Groq": "llama3-70b-8192",
                "OpenAI": "gpt-4o",
                "Gemini": "gemini-2.5-flash-preview-04-17",
                "TogetherAI": "Qwen/Qwen2-72B-Instruct", 
                "Ollama": "llama3",
                "CUSTOM": "",
            }
            model = endpoint_model_map.get(args.endpoint, "gpt-4o")
        
        # Add directory to path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Translate text
        try:
            from src.translator import model_load, simple_translator
            
            # Get API key from argument or environment
            api_key = args.apikey
            if not api_key and args.endpoint != 'Ollama':
                from dotenv import load_dotenv
                load_dotenv()
                env_key_name = f"{args.endpoint.upper()}_API_KEY"
                api_key = os.getenv(env_key_name)
            
            # Initialize the model
            model_load(
                endpoint=args.endpoint,
                model=model,
                api_key=api_key
            )
            
            # Translate the text
            translation = simple_translator(
                source_lang=args.source,
                target_lang=args.target,
                source_text=source_text,
                country=args.country
            )
            
            # Output the translation
            if args.output:
                try:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(translation)
                    print(f"✅ Translation saved to: {args.output}")
                except Exception as e:
                    print(f"❌ Error writing output file: {e}")
                    return 1
            else:
                print("\n----- Translation -----")
                print(translation)
                print("-----------------------")
            
            return 0
            
        except ImportError as e:
            print(f"❌ Error: {e}")
            print("Please install the required packages: pip install -r requirements.txt")
            return 1
        except Exception as e:
            print(f"❌ Error during translation: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 