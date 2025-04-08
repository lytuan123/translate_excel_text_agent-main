#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Advanced Translation Suite - Excel Translator CLI
Translates Excel files with enhanced AI translation capabilities
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import Optional

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from our module
from src.translator import model_load, process_excel, process_directory


def main():
    """Main entry point for Excel Translator CLI"""
    parser = argparse.ArgumentParser(description='Advanced Translation Suite - Excel Translator')
    
    # Required arguments
    parser.add_argument('--source', type=str, required=True,
                        help='Source language (e.g., English, Japanese)')
    parser.add_argument('--target', type=str, required=True,
                        help='Target language (e.g., Spanish, Vietnamese)')
    
    # Input/output options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--file', type=str,
                             help='Path to Excel file to translate')
    input_group.add_argument('--dir', type=str,
                             help='Path to directory containing Excel files')
    
    parser.add_argument('--output', type=str,
                        help='Path for saving translated output (file or directory)')
    parser.add_argument('--country', type=str, default="",
                        help='Target country context (e.g., Mexico, Vietnam, Japan)')
    
    # API configuration
    parser.add_argument('--endpoint', choices=['OpenAI', 'Groq', 'TogetherAI', 'Ollama', 'CUSTOM'],
                        default='OpenAI', help='Translation service endpoint')
    parser.add_argument('--model', type=str, default='gpt-4o',
                        help='Model name')
    parser.add_argument('--apikey', type=str,
                        help='API Key (will use environment variable if not provided)')
    parser.add_argument('--baseurl', type=str,
                        help='Custom Base URL (needed only for CUSTOM endpoint)')
    
    # Advanced options
    parser.add_argument('--temperature', type=float, default=0.3,
                        help='Sampling temperature (0.0-1.0)')
    parser.add_argument('--rpm', type=int, default=60,
                        help='Requests per minute limit')
    
    args = parser.parse_args()
    
    # Get API key from argument or environment variable
    api_key = args.apikey
    if not api_key and args.endpoint != 'Ollama':
        env_key_name = f"{args.endpoint.upper()}_API_KEY"
        api_key = os.getenv(env_key_name)
        if not api_key:
            print(f"⚠️ API Key not provided via --apikey argument or {env_key_name} environment variable.")
            if args.endpoint != 'Ollama':  # Ollama doesn't need key
                return 1
    
    # Validate and process arguments
    if args.endpoint == 'CUSTOM' and not args.baseurl:
        print("❌ Base URL is required for CUSTOM endpoint")
        return 1
    
    # Initialize translator model
    print(f"🚀 Initializing translation model: {args.endpoint} / {args.model}")
    try:
        model_load(
            endpoint=args.endpoint,
            model=args.model,
            api_key=api_key,
            base_url=args.baseurl,
            temperature=args.temperature,
            rpm=args.rpm
        )
    except Exception as e:
        print(f"❌ Failed to initialize model: {str(e)}")
        return 1
    
    # Process file or directory
    start_time = time.time()
    
    if args.file:
        # Single file processing
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            return 1
            
        print(f"📄 Processing file: {args.file}")
        output_path = args.output
        
        result = process_excel(
            input_path=args.file,
            output_path=output_path,
            source_lang=args.source,
            target_lang=args.target,
            country=args.country
        )
        
        if not result:
            print("❌ Translation failed")
            return 1
            
    elif args.dir:
        # Directory processing
        if not os.path.isdir(args.dir):
            print(f"❌ Directory not found: {args.dir}")
            return 1
            
        print(f"📁 Processing directory: {args.dir}")
        output_dir = args.output
        
        results = process_directory(
            input_dir=args.dir,
            output_dir=output_dir,
            source_lang=args.source,
            target_lang=args.target,
            country=args.country
        )
        
        if not results:
            print("⚠️ No files were translated successfully")
            return 1
    
    # Calculate and display execution time
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\n⏱️ Translation completed in {execution_time:.2f} seconds")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 