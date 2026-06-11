# 🛡️ Oh-My-Security (OMS)

> Digital Guardian for Indie Developers & Creators.

**Oh-My-Security** is a lightweight terminal security tool designed for **solo developers, Indie Hackers, and content creators**.

We don't talk about boring enterprise DevSecOps or compliance certifications. We focus on what truly matters to indie developers:
**How to prevent accidentally pushing API keys to GitHub and going bankrupt? How to avoid getting your account banned for sensitive words in your articles? How to stop your server from being overwhelmed by scrapers?**

OMS packages top security expertise and AI auditing capabilities into a simple CLI, letting you focus on creating while staying protected from digital threats.

**[中文版本](./README.md)**

---

## ✨ Core Scenarios

### 1. 💻 Bankruptcy-Prevention Code Audit (`oms code`)
Indie developers often lack code review environments. Run OMS before `git push`:
- Deep scan for hardcoded secrets, database passwords, and LLM API keys (bankruptcy protection).
- Identify common authentication bypass vulnerabilities and SQL injection risks in full-stack projects.

### 2. 📝 Content Risk Control (`oms content`)
Spent hours writing an article only to have it banned by the platform?
- Scan Markdown/text drafts before publishing to identify sensitive words and controversial statements.
- Check if images or text accidentally leak real phone numbers, ID cards, or home addresses.

### 3. 🛡️ Anti-Scraping Guide (`oms bizsec`)
Your side project just got some traffic, and now APIs are being hammered by scrapers?
- Diagnose whether your public APIs are exposed using 100+ real business security cases.
- Provide low-cost, easy-to-implement anti-scraping code snippets (IP-based rate limiting, fingerprint verification).

### 4. ☁️ One-Click VPS Hardening (`oms vps`)
Just bought a cheap cloud server for your blog and don't know how to secure it?
- Provides a "foolproof" server hardening wizard to generate SSH key configurations, firewall rules, and brute-force protection scripts.

---

## 🚀 Quick Start

### Install OMS
Clone this repository and add the `bin` directory to your environment:

```bash
git clone https://github.com/tinylion1024/oh-my-security.git
cd oh-my-security
pip install -r requirements.txt

# Add oms to global commands (recommended: add to ~/.zshrc or ~/.bashrc)
export PYTHONPATH=$(pwd)
export PATH="$PATH:$(pwd)/bin"
```

### Invoke Your Security Guardian

Type `oms` in your terminal to get the protection you need:

```text
  ____  _       __  __          ____                       _ _
 / __ \| |     |  \/  |        / ___|                     (_) |
| |  | | |__   | \  / |_   _  | |___  ___  ___ _   _ _ __  _| |_ _   _
| |  | | '_ \  | |\/| | | | |  \___ \/ _ \/ __| | | | '__| | | __| | | |
| |__| | | | | | |  | | |_| |  ____) |  __/ (__| |_| | |  | | | |_| |_| |
 \____/|_| |_| |_|  |_|\__, | |_____/ \___|\___|\__,_|_|  |_|_|\__|\__, |
                       __/ |                                       __/ |
                      |___/                                       |___/
```

#### Query Pitfall Cases
For example, to learn how to prevent your website from being scraped:
```bash
oms case "crawler"
```

#### Vulnerability Severity Assessment
Found a vulnerability in a third-party library and want to know how serious it is:
```bash
oms cvss -av N -ac L -pr N -ui N -c H -i H -a H
```

*(Note: `oms code`, `oms content` and other AI-powered audit features are under active development. Stay tuned!)*

---

## 🧠 Core Asset: 300+ Pitfall Case Library

OMS is not just an empty shell. Its wisdom comes from **304 deeply analyzed real-world cases** in the `knowledge_base` directory.
These serve as important context for AI auditing and excellent learning materials for your daily reading.

- **Business Security (Bizsec)**: 100 cases to identify coupon abuse, API exploitation, and zero-price order traps.
- **Information Security (Infosec)**: 100 cases covering misconfigurations, supply chain poisoning, and infrastructure vulnerabilities.
- **AI Security (AIsec)**: 100 cases to guide you in preventing prompt injection and data leakage in LLM applications.

---

## 🤝 Contribute to the Community
If you're an indie developer who has learned from painful experiences, welcome to submit PRs to add your hard-earned wisdom to our `knowledge_base/cases/`!

## ⚖️ Disclaimer
*Oh-My-Security's code auditing and content risk control features are for reference only and do not constitute legally binding compliance certification. Developers bear final responsibility for their own code and published content.*
