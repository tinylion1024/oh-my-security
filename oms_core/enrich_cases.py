#!/usr/bin/env python3
import os
import subprocess
import time
import re

# 目标：遍历剩下的目录，使用 `gemini -p` 命令批量重写文件
# 该脚本设计为幂等的，可以随时中断和重启。

# 获取项目根目录 (假设脚本位于 scripts/ 目录下)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 需要被重写的根目录 (相对于项目根目录)
TARGET_DIRS = [
    # Bizsec 剩下的 8 个目录
    "knowledge/cases/vertical/bizsec/03-transaction",
    "knowledge/cases/vertical/bizsec/04-logic",
    "knowledge/cases/vertical/bizsec/05-crawling",
    "knowledge/cases/vertical/bizsec/06-fintech",
    "knowledge/cases/vertical/bizsec/07-social",
    "knowledge/cases/vertical/bizsec/08-gaming",
    "knowledge/cases/vertical/bizsec/09-o2o",
    "knowledge/cases/vertical/bizsec/10-ai",
    
    # Infosec 剩下的 8 个目录
    "knowledge/cases/vertical/infosec/03-supply-chain",
    "knowledge/cases/vertical/infosec/04-network",
    "knowledge/cases/vertical/infosec/05-endpoint",
    "knowledge/cases/vertical/infosec/06-identity",
    "knowledge/cases/vertical/infosec/07-app-sec",
    "knowledge/cases/vertical/infosec/08-data-protection",
    "knowledge/cases/vertical/infosec/09-devsecops",
    "knowledge/cases/vertical/infosec/10-emerging",
    
    # AIsec 剩下的 8 个目录
    "knowledge/cases/vertical/aisec/03-model-robustness",
    "knowledge/cases/vertical/aisec/04-training-security",
    "knowledge/cases/vertical/aisec/05-deployment",
    "knowledge/cases/vertical/aisec/06-llm-logic",
    "knowledge/cases/vertical/aisec/07-content-safety",
    "knowledge/cases/vertical/aisec/08-ai-infra",
    "knowledge/cases/vertical/aisec/09-supply-chain",
    "knowledge/cases/vertical/aisec/10-governance"
]

def check_if_enriched(dir_path):
    """
    检查该目录下的文件是否已经被扩充过。
    简单的启发式方法：如果第一个文件大小超过 500 字节，则认为已处理。
    """
    try:
        first_file = os.path.join(dir_path, "case_01.md")
        if os.path.exists(first_file):
            size = os.path.getsize(first_file)
            if size > 600:  # 重写后的文件通常在 1000 字节以上，未重写的大约 200 字节
                return True
        return False
    except Exception:
        return False

def build_prompt(dir_path):
    """
    根据目录路径，构建具体的 Prompt。
    要求大模型直接输出带特殊定界符的纯文本，不再使用 Tool。
    """
    domain = "业务安全" if "bizsec" in dir_path else ("信息安全" if "infosec" in dir_path else "AI 安全")
    
    prompt = f"""你现在是一个高级网络安全专家。
请深度重写（Enrich）以下目录中的所有 10 个 Markdown 文件：
`{dir_path}`

目标：将该目录下的 case_01.md 到 case_10.md 共 10 个文件，分别扩充为 300-400 字的专家级中文安全案例。

重写要求：
1. 事件回顾: 设定高度逼真的行业背景，描述具体的攻击后果或损失。
2. Red View: 提供 3-4 步具体的技术攻击链（Kill Chain）。必须提到具体的攻击工具或手法。
3. Blue View: 解释防线为何被击穿（缺乏检测、配置错误、逻辑漏洞等）。
4. 策略借鉴: 提供 3 条具体且可落地的技术修复建议。

【极度重要指令】：
你不允许使用任何写文件的 Tool！由于环境限制，调用写文件工具会被拦截。
请直接在文本回复中输出文件内容。为了方便解析，请严格使用以下定界符包裹每一个文件（千万不要在外部套 markdown 代码块）：

===FILE:case_01.md===
# [具体而专业的案例名称]
- **所属领域**: {domain}
- **威胁类型**: [具体的威胁子类]
- **事件回顾**: ...
- **Red View (利用路径)**: ...
- **Blue View (防御缺失)**: ...
- **策略借鉴**: ...
===ENDFILE===

===FILE:case_02.md===
...（此处是第二个文件的内容）...
===ENDFILE===

请连续输出 case_01.md 到 case_10.md 共十个案例。不要输出任何多余的开头解释或闲聊。
"""
    return prompt

def parse_and_write(target_dir, text_output):
    """
    使用正则表达式解析大模型输出的内容，并由 Python 写入本地文件。
    """
    # 匹配 ===FILE:case_xx.md=== 和 ===ENDFILE=== 之间的内容
    pattern = r"===FILE:(case_\d{2}\.md)===[\s\S]*?\n(.*?)\n===ENDFILE==="
    matches = re.finditer(pattern, text_output, re.DOTALL)
    
    count = 0
    for match in matches:
        filename = match.group(1).strip()
        content = match.group(2).strip()
        
        # 清理由于大模型习惯额外加的 markdown 代码块包裹
        if content.startswith("```markdown"):
            content = content[11:].strip()
        elif content.startswith("```"):
            content = content[3:].strip()
            
        if content.endswith("```"):
            content = content[:-3].strip()
            
        filepath = os.path.join(target_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        
        count += 1
        print(f"    [+] 成功解析并保存: {filename} ({len(content)} 字符)")
        
    return count

def main():
    print("=" * 60)
    print("🚀 启动 Security Master 案例库全量扩充引擎 (无 Tool 安全版)")
    print(f"总计需要检查 {len(TARGET_DIRS)} 个目录")
    print("=" * 60)

    for i, rel_target_dir in enumerate(TARGET_DIRS):
        target_dir = os.path.join(PROJECT_ROOT, rel_target_dir)
        print(f"\n[{i+1}/{len(TARGET_DIRS)}] 正在检查: {rel_target_dir}")
        
        if not os.path.exists(target_dir):
            print(f"⚠️ 警告：目录不存在 ({target_dir})，跳过。")
            continue
            
        if check_if_enriched(target_dir):
            print("✅ 该目录文件已精修，跳过。")
            continue
            
        print("⏳ 正在请求 Gemini 生成案例 (约需 1~2 分钟)，请耐心等待...")
        prompt = build_prompt(target_dir)
        
        command = ["gemini", "-p", prompt]
        
        try:
            # 执行命令并捕获全部输出
            result = subprocess.run(command, capture_output=True, text=True)
            output = result.stdout + "\n" + result.stderr
            
            # 使用 Python 脚本进行解析并写文件
            files_written = parse_and_write(target_dir, output)
            
            if files_written > 0:
                print(f"🎉 成功生成并写入 {files_written} 个文件！休息 5 秒避免触发限流...")
                time.sleep(5)
            else:
                print("❌ 解析失败，未能提取到符合格式的文件内容。大模型输出如下：")
                print("-" * 40)
                # 打印前1000个字符用于排查
                print(output[:1000] + "\n... (已截断)") 
                print("-" * 40)
                # 遇到解析错误建议停下来，避免一直报错空转
                break
                
        except KeyboardInterrupt:
            print("\n🛑 用户手动终止了脚本。")
            break
        except Exception as e:
            print(f"❌ 执行发生异常: {e}")
            break

    print("\n✅ 所有任务处理完毕。建议运行 git status 查看改动，并提交。")

if __name__ == "__main__":
    main()
