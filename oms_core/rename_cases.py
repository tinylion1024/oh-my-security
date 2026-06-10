#!/usr/bin/env python3
import os
import re
import shutil

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES_DIR = os.path.join(PROJECT_ROOT, "knowledge/cases/vertical")

def sanitize_filename(title):
    """
    将中文或包含特殊字符的标题转换为安全的文件名。
    将空格、特殊符号替换为连字符 -
    """
    # 移除首尾空白
    title = title.strip()
    
    # 移除一些会导致路径问题的特殊字符
    title = re.sub(r'[\\/*?:"<>|#\(\)\[\]{}]', '', title)
    
    # 将空格、破折号等替换为单个连字符
    title = re.sub(r'[\s_]+', '-', title)
    title = re.sub(r'-+', '-', title)
    
    # 转为小写
    return title.lower()

def extract_title_from_md(filepath):
    """
    读取 Markdown 文件，提取第一个一级标题作为文件名依据。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# '):
                    return line[2:].strip()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return None

def process_directory(dir_path):
    """
    处理特定目录下的所有 markdown 文件，根据其内部标题重命名。
    """
    if not os.path.exists(dir_path):
        return

    print(f"\n📁 正在处理目录: {os.path.relpath(dir_path, PROJECT_ROOT)}")
    
    files = sorted([f for f in os.listdir(dir_path) if f.endswith('.md')])
    
    for i, filename in enumerate(files):
        # 如果文件名已经是描述性的（而不是 case_xx.md），则跳过
        if not filename.startswith('case_'):
            continue
            
        old_filepath = os.path.join(dir_path, filename)
        
        # 提取标题
        title = extract_title_from_md(old_filepath)
        if not title:
            print(f"  ⚠️ 警告: {filename} 中未找到标题，跳过。")
            continue
            
        # 生成安全的文件名
        safe_title = sanitize_filename(title)
        
        # 提取原本 case_xx 中的数字，保留顺序
        match = re.search(r'case_(\d+)', filename)
        prefix = match.group(1) if match else f"{i+1:02d}"
        
        new_filename = f"{prefix}-{safe_title}.md"
        new_filepath = os.path.join(dir_path, new_filename)
        
        # 重命名
        try:
            os.rename(old_filepath, new_filepath)
            print(f"  ✅ 重命名: {filename} -> {new_filename}")
        except Exception as e:
            print(f"  ❌ 失败 {filename}: {e}")

def main():
    print("=" * 60)
    print("🔄 启动 Security Master 案例文件名优化器")
    print("将提取文件内的 Markdown 标题作为物理文件名...")
    print("=" * 60)

    # 遍历所有纵深安全领域的子目录
    for domain in ['bizsec', 'infosec', 'aisec']:
        domain_path = os.path.join(CASES_DIR, domain)
        if not os.path.exists(domain_path):
            continue
            
        for category in sorted(os.listdir(domain_path)):
            category_path = os.path.join(domain_path, category)
            if os.path.isdir(category_path):
                process_directory(category_path)

    print("\n✅ 所有文件重命名完成！建议运行 scripts/generate_indexes.py 更新索引。")

if __name__ == "__main__":
    main()
