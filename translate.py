import os
import sys
import argparse
import json
from typing import Optional

def get_openai_client():
    """必要な時だけインポートしてクライアントを返す"""
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)

def translate_content(text: str, from_lang: str, to_lang: str, model: str) -> str:
    """OpenAIを使用して一括で翻訳を行う"""
    client = get_openai_client()
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"You are a professional translator. Translate from {from_lang} to {to_lang}. Output only the translated text."
            },
            {"role": "user", "content": text}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def main():
    # エンコーディング設定（Windows対策）
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="Translation CLI and MCP Server")
    parser.add_argument("--mcp", action="store_true", help="Run as an MCP server")
    parser.add_argument("--input", help="Input file path")
    parser.add_argument("--from", dest="from_lang", help="Source language")
    parser.add_argument("--to", dest="to_lang", help="Target language")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model to use (default: gpt-4o-mini)")

    args = parser.parse_args()

    # --- MCP Mode ---
    if args.mcp:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("TranslateServer")

        @mcp.tool()
        def translate_file(path: str, from_lang: str, to_lang: str, model: str = "gpt-4o-mini") -> str:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                return translate_content(content, from_lang, to_lang, model)
            except Exception as e:
                return json.dumps({"error": str(e)}, ensure_ascii=False)

        mcp.run()

    # --- CLI Mode ---
    else:
        # CLIモードで必須の引数チェック
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
            result = translate_content(content, args.from_lang, args.to_lang, args.model)
            print(result)
            
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
