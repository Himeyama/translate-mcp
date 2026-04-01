import os
import sys
import argparse
import json
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def translate_content(text: str, from_lang: str, to_lang: str) -> str:
    """
    Translates the given text from one language to another using OpenAI.
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set. Please provide it in .env or environment variables.")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate the following text from {from_lang} to {to_lang}. Output only the translated text."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")

# Initialize FastMCP server
mcp = FastMCP("TranslateServer")

@mcp.tool()
def translate_file(path: str, from_lang: str, to_lang: str) -> str:
    """
    Translates the content of a file from one language to another.
    
    Args:
        path: Path to the input file.
        from_lang: Source language (e.g., 'English').
        to_lang: Target language (e.g., 'Japanese').
    """
    try:
        if not os.path.exists(path):
            return json.dumps({"error": f"File not found: {path}"}, ensure_ascii=False)
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        translated = translate_content(content, from_lang, to_lang)
        return translated
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="Translation CLI and MCP Server")
    parser.add_argument("--mcp", action="store_true", help="Run as an MCP server")
    parser.add_argument("--input", help="Input file path (ignored in MCP mode)")
    parser.add_argument("--from", dest="from_lang", help="Source language")
    parser.add_argument("--to", dest="to_lang", help="Target language")

    args = parser.parse_args()

    if args.mcp:
        # MCP Mode
        mcp.run()
    else:
        # CLI Mode
        if not args.input or not args.from_lang or not args.to_lang:
            sys.stderr.write("Error: --input, --from, and --to are required in CLI mode.\n")
            sys.exit(1)
        
        try:
            if not os.path.exists(args.input):
                sys.stderr.write(f"Error: File not found: {args.input}\n")
                sys.exit(1)

            with open(args.input, "r", encoding="utf-8") as f:
                content = f.read()

            result = translate_content(content, args.from_lang, args.to_lang)
            print(result)
        except Exception as e:
            sys.stderr.write(f"Error: {str(e)}\n")
            sys.exit(1)

if __name__ == "__main__":
    main()
