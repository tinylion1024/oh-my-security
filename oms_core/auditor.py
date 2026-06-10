import os
import subprocess

def ask_ai(prompt):
    """
    通过调用本机的 gemini CLI 工具，利用大模型处理 Prompt。
    """
    try:
        # 使用 gemini -p 传递 prompt
        result = subprocess.run(
            ["gemini", "-p", prompt], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"❌ AI 引擎调用失败:\n{result.stderr}"
    except FileNotFoundError:
        return "❌ 未找到 gemini CLI 工具。请确保您的终端已安装并配置好 Gemini 命令行环境。"
    except Exception as e:
        return f"❌ 执行期间发生异常: {e}"

def audit_code(target_path):
    """
    扫描目标路径下的代码，拼接后发送给 AI 进行防破产审计。
    """
    if not os.path.exists(target_path):
        return f"❌ 路径不存在: {target_path}"

    files_to_scan = []
    if os.path.isfile(target_path):
        files_to_scan.append(target_path)
    elif os.path.isdir(target_path):
        for root, dirs, files in os.walk(target_path):
            # 过滤掉不需要扫描的庞大目录
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build']]
            for f in files:
                if f.endswith(('.py', '.js', '.ts', '.env', '.json', '.yml', '.yaml', '.go', '.rs', '.php', '.java', '.sh')):
                    files_to_scan.append(os.path.join(root, f))

    if not files_to_scan:
        return "⚠️ 未在目标路径下发现支持扫描的源代码文件（如 .py, .js, .env 等）。"

    # 组装代码内容（为了防止 Token 爆炸，限制文件数量和总长度）
    code_context = ""
    processed_count = 0
    
    for fpath in files_to_scan:
        if processed_count >= 15: # 最多读15个文件
            code_context += "\n... (文件数量过多，剩余文件已截断扫描) ...\n"
            break
            
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
                # 单个文件限制长度
                if len(content) > 5000:
                    content = content[:5000] + "\n...(单文件过长，截断)..."
                code_context += f"--- FILE: {fpath} ---\n{content}\n\n"
                processed_count += 1
        except Exception:
            continue

    if not code_context.strip():
        return "⚠️ 读取文件内容失败或文件全为空。"

    prompt = f"""你现在是 Oh-My-Security 的「独立开发者代码护卫」。
请对以下代码进行深度安全扫描，你的核心任务是帮开发者“防破产”、“防被黑”：

1. **防破产检查 (Secret Leak)**: 寻找硬编码的大模型 API Key (OpenAI, Anthropic, Gemini)、数据库账号密码、AWS AK/SK、支付网关密钥等。
2. **致命漏洞检查**: 寻找极度危险的代码模式（如：无参数校验直接拼接 SQL、直接执行系统命令 `os.system` 而不转义、极度脆弱的鉴权）。

请输出一份极客风格的中文安全体检报告，必须明确指出：
- 发现风险的具体文件路径和疑似泄露的代码。
- 这个风险被黑客利用后会导致什么后果。
- 给出直接的修复建议或替代方案（如使用 `python-dotenv`）。

如果代码非常安全，请狠狠夸奖开发者的安全意识。

待审计代码如下：
{code_context}
"""
    return ask_ai(prompt)


def audit_content(target_path):
    """
    读取 Markdown 或文本文件，发送给 AI 进行内容风控排雷。
    """
    if not os.path.exists(target_path) or not os.path.isfile(target_path):
        return f"❌ 找不到有效的文本文件: {target_path}"

    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return f"❌ 读取文件失败: {e}"
        
    if len(content) > 20000:
        content = content[:20000] + "\n...(文章过长，截断)..."

    prompt = f"""你现在是 Oh-My-Security 的「自媒体内容风控专家」。
请严格审查以下创作者的文章草稿，帮其找出可能导致平台封号、删帖或隐私泄露的地雷：

1. **隐私泄露 (PII)**: 是否不小心贴出了真实的手机号、身份证、住址、企业内部 IP 地址或内网 URL。
2. **违规风险**: 是否包含明显的政治敏感词、涉黄涉暴、或者极易引发平台审核机器人的违规词汇。
3. **AI 幻觉/低级错误**: 识别其中明显违反常识的错误（防止发布后被读者嘲笑）。

请输出一份中文风控报告：
- 如果发现风险，请引用具体的原文句子，说明为什么有风险，并提供【安全的替换建议】。
- 如果文章非常安全，请用一两句话鼓励创作者放心发布。

待审查文章内容如下：
{content}
"""
    return ask_ai(prompt)
