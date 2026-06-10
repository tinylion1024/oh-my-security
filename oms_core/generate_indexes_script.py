import os
import json
import re

# 获取项目根目录 (假设脚本位于 scripts/ 目录下)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def extract_metadata(filepath):
    """
    Extract title and simple metadata from markdown files.
    """
    metadata = {
        "title": "Unknown",
        "domain": "Unknown",
        "threat_type": "Unknown",
        "path": filepath
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract title (first # Heading)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                metadata["title"] = title_match.group(1).strip()
            
            # Extract domain (- **所属领域**: xxx)
            domain_match = re.search(r'-\s*\*\*所属领域\*\*:\s*(.+)$', content, re.MULTILINE)
            if domain_match:
                metadata["domain"] = domain_match.group(1).strip()
                
            # Extract threat type (- **威胁类型**: xxx)
            threat_match = re.search(r'-\s*\*\*威胁/分类\*\*:\s*(.+)$', content, re.MULTILINE)
            if not threat_match:
                threat_match = re.search(r'-\s*\*\*威胁类型\*\*:\s*(.+)$', content, re.MULTILINE)
            if threat_match:
                metadata["threat_type"] = threat_match.group(1).strip()
                
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        
    return metadata

def build_index(base_dir, output_file):
    """
    Traverse a directory, extract metadata, and save to a JSON index file.
    """
    index = []
    
    # 将相对路径转换为绝对路径以确保遍历正确
    abs_base_dir = os.path.join(PROJECT_ROOT, base_dir)
    abs_output_file = os.path.join(PROJECT_ROOT, output_file)
    
    if not os.path.exists(abs_base_dir):
        print(f"Directory not found: {abs_base_dir}")
        return

    for root, dirs, files in os.walk(abs_base_dir):
        for file in files:
            if file.endswith('.md') and file != 'README.md' and file != 'STRUCTURE-SPEC.md':
                filepath = os.path.join(root, file)
                metadata = extract_metadata(filepath)
                # Make path relative to project root for portability
                rel_path = os.path.relpath(filepath, PROJECT_ROOT)
                metadata["path"] = rel_path
                index.append(metadata)
                
    os.makedirs(os.path.dirname(abs_output_file), exist_ok=True)
    with open(abs_output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"[*] Generated index {output_file} with {len(index)} entries.")

if __name__ == "__main__":
    print("Building knowledge indexes...")
    
    cases_dir = "knowledge_base/cases"
    cases_index_file = "knowledge_base/indexes/cases-index.json"
    build_index(cases_dir, cases_index_file)
    
    weapons_dir = "knowledge_base/weapons"
    weapons_index_file = "knowledge_base/indexes/weapons-index.json"
    build_index(weapons_dir, weapons_index_file)
    
    guides_dir = "knowledge_base/guides"
    guides_index_file = "knowledge_base/indexes/guides-index.json"
    build_index(guides_dir, guides_index_file)
    
    print("Done.")

