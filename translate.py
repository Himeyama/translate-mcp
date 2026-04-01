import os
import sys
import argparse
import json
import logging
from typing import Optional

def get_openai_client(debug: bool = False):
    """必要な時だけインポート。debug=TrueならログレベルをDEBUGに設定"""
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    
    if debug:
        # openaiライブラリのログを有効化
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("openai").setLevel(logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.DEBUG)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)

def translate_content(text: str, from_lang: str, to_lang: str, model: str, debug: bool = False) -> str:
    """OpenAIを使用して翻訳を行う"""
    client = get_openai_client(debug=debug)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"You are a professional translator. Translate from {from_lang} to {to_lang}. Output only the translated text."
            },
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="Translation CLI and MCP Server")
    parser.add_argument("--mcp", action="store_true", help="Run as an MCP server")
    parser.add_argument("--input", help="Input file path")
    parser.add_argument("--output", help="Output file path (optional)")
    parser.add_argument("--from", dest="from_lang", help="Source language")
    parser.add_argument("--to", dest="to_lang", help="Target language")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model to use (default: gpt-4o-mini)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging for API communication")

    args = parser.parse_args()

    # --- MCP Mode ---
    if args.mcp:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("TranslateServer")

        @mcp.tool()
        def translate_file(path: str, from_lang: str, to_lang: str, output_path: Optional[str] = None, model: str = "gpt-4o-mini", debug: bool = False) -> str:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                result = translate_content(content, from_lang, to_lang, model, debug)
                
                if output_path:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(result)
                    return f"Successfully translated and saved to {output_path}"
                
                return result
            except Exception as e:
                return json.dumps({"error": str(e)}, ensure_ascii=False)

        mcp.run()

    # --- CLI Mode ---
    else:
        if not all([args.input, args.from_lang, args.to_lang]):
            parser.print_help()
            sys.exit(1)

        try:
            if not os.path.exists(args.input):
                print(f"Error: File not found: {args.input}", file=sys.stderr)
                sys.exit(1)

            with open(args.input, "r", encoding="utf-8") as f:
                content = f.read()

            # 翻訳実行
            result = translate_content(content, args.from_lang, args.to_lang, args.model, args.debug)
            
            # 出力先（ファイル or 標準出力）の切り替え
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(result)
                print(f"Success: Translated content saved to {args.output}")
            else:
                print(result)
            
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()