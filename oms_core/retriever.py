import os
import json

class SecurityKnowledgeRetriever:
    """
    基于生成的 JSON 索引文件的知识检索器。
    支持简单的关键词匹配和元数据过滤。
    """
    def __init__(self, base_path=None):
        if base_path is None:
            # 默认相对于项目根目录
            self.base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")
        else:
            self.base_path = base_path
            
        self.indexes = {
            "cases": self._load_index("indexes/cases-index.json"),
            "weapons": self._load_index("indexes/weapons-index.json"),
            "guides": self._load_index("indexes/guides-index.json")
        }

    def _load_index(self, rel_path):
        full_path = os.path.join(self.base_path, rel_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def search(self, query, category="cases", domain=None, limit=5):
        """
        在指定类别中搜索关键词。
        category: 'cases', 'weapons', or 'guides'
        """
        print(f"[*] 检索 '{category}' 类别，关键词: '{query}'...")
        results = []
        
        index_to_search = self.indexes.get(category, [])
        
        for item in index_to_search:
            # 过滤领域 (如果指定)
            if domain and domain.lower() not in item.get('domain', '').lower():
                continue
                
            # 简单关键词匹配 (标题或威胁类型)
            text_to_search = f"{item.get('title', '')} {item.get('threat_type', '')}".lower()
            if query.lower() in text_to_search:
                results.append(item)
                
            if len(results) >= limit:
                break
                
        return results

if __name__ == "__main__":
    retriever = SecurityKnowledgeRetriever()
    
    print("\n--- 检索案例: 绕过 ---")
    hits = retriever.search("绕过", category="cases", limit=3)
    for hit in hits:
        print(f"- {hit['title']} ({hit['threat_type']}) -> {hit['path']}")
        
    print("\n--- 检索案例: 爬虫 ---")
    hits = retriever.search("爬虫", category="cases", limit=3)
    for hit in hits:
        print(f"- {hit['title']} ({hit['threat_type']}) -> {hit['path']}")
        
    print("\n--- 检索案例: 领域=AI 安全 ---")
    hits = retriever.search("AI", category="cases", domain="AI安全", limit=3)
    for hit in hits:
        print(f"- {hit['title']} ({hit['domain']}) -> {hit['path']}")
