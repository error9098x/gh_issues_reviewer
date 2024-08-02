import json
import os
from pathlib import Path
import argparse
import sys

def read_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, 1):
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON on line {line_number}: {e}")
                    print(f"Problematic line: {line}")
                    continue  # Skip this line and continue with the next

def sanitize_name(name):
    return ''.join(c for c in name if c.isalnum() or c in [' ', '_', '-']).rstrip()

def generate_markdown(title, tool_name, subcategory, conversation):
    md_content = f"# {title}\n\n"
    if tool_name:
        md_content += f"Tool: {tool_name}\n\n"
    if subcategory:
        md_content += f"Subcategory: {subcategory}\n\n"
    md_content += "## Conversation\n\n"
    for entry in conversation:
        md_content += f"### {entry['role']}\n{entry['message']}\n\n"
    return md_content

def convert_jsonl_to_md(input_file, output_dir):
    mapping = {}
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for item in read_jsonl(input_file):
        category = sanitize_name(item['category'])
        unique_id = str(item['id'])
        title = item['title']
        tool_name = item.get('Tool')
        subcategory = item.get('subcategory')
        conversation = item['content']

        category_dir = os.path.join(output_dir, category)
        Path(category_dir).mkdir(parents=True, exist_ok=True)

        file_name = f"{unique_id}.md"
        file_path = os.path.join(category_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as md_file:
            md_file.write(generate_markdown(title, tool_name, subcategory, conversation))

        relative_path = os.path.join(category, file_name)
        mapping[relative_path] = {
            "url": item['url'],
            "tool": tool_name if tool_name else None,
            "author": item['author'],
            "date": item['date']
        }

    mapping_file = os.path.join(output_dir, 'mapping.json')
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Convert JSONL to Markdown files")
    parser.add_argument("input_file", help="Path to the input JSONL file")
    args = parser.parse_args()

    output_dir = 'gh_discussions_dataset'
    
    if not os.path.exists(args.input_file):
        print(f"Input file not found: {args.input_file}")
        sys.exit(1)
    
    convert_jsonl_to_md(args.input_file, output_dir)
    print("Conversion completed successfully")

if __name__ == "__main__":
    main()