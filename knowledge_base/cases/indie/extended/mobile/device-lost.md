# 设备丢失风险（Device Lost）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: mobile（移动设备安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $5-20/月 | L3: 企业MDM方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
手机丢失后，攻击者获取设备访问权限，窃取所有应用数据、账号和个人隐私。

### 一分钟识别
你的设备是否有以下特征：
- [ ] 未启用设备加密
- [ ] 锁屏密码简单（4位数字或图案）
- [ ] 未开启远程锁定/擦除功能
- [ ] 部分应用记住密码自动登录
- [ ] 未启用 Find My 功能
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
启用设备加密 + 强锁屏密码 + 远程擦除功能 + 敏感应用单独加锁。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 启用 Find My iPhone / Find My Device
   - [ ] 设置 6 位以上数字密码
   - [ ] 启用设备全盘加密
   - [ ] 记录设备 IMEI 号

2. **短期行动**（本周可完成，低成本）
   - [ ] 为敏感应用设置单独密码/生物识别锁
   - [ ] 启用关键账号的登录通知
   - [ ] 备份重要数据到云端
   - [ ] 设置 SIM 卡 PIN 码

3. **长期行动**（规划中）
   - [ ] 购买设备保险
   - [ ] 部署企业级设备管理方案
   - [ ] 建立设备丢失应急响应流程

### 推荐工具
- **免费**：
  - Find My iPhone (iOS 内置)
  - Find My Device (Android 内置)
  - Google One 备份

- **低成本**：
  - Cerberus (Android 第三方追踪)
  - Prey Anti Theft (跨平台)

### 验证方法
- [ ] 测试步骤1：验证 Find My 功能是否正常工作
- [ ] 测试步骤2：检查设备加密状态
- [ ] 测试步骤3：模拟远程锁定测试
- [ ] 测试步骤4：验证 SIM 卡 PIN 是否生效

---

## L2 小团队版（理解版）

### 场景还原
你的团队有 5 人使用公司手机处理业务，某天一名员工的手机在地铁上丢失：

**攻击时间线**：
1. **Day 0 09:00**：员工发现手机丢失
2. **Day 0 10:00**：攻击者尝试解锁，发现是简单图案密码
3. **Day 0 11:00**：攻击者通过观察痕迹破解图案密码
4. **Day 0 12:00**：攻击者访问所有应用，包括公司邮件、客服系统
5. **Day 0 14:00**：攻击者重置关键账号密码
6. **Day 0 16:00**：公司客户数据开始泄露

**真实损失案例**：
- 2023年某公司员工手机丢失，导致 10000+ 客户数据泄露
- 2022年某创业公司因设备丢失导致商业机密泄露，损失融资机会

### 攻击向量分析

**物理攻击**：
```
攻击方式:
1. 简单密码破解（观察指纹痕迹、肩窥）
2. USB 调试绕过锁屏（旧版 Android）
3. 恢复出厂设置后使用
4. SIM 卡取出后接收验证码
```

**数据提取**：
```
攻击方式:
1. ADB 备份数据（需 USB 调试开启）
2. 越狱/Root 后直接读取
3. 云备份账号同步获取
4. 应用内导出数据
```

### 防御实现

**1. 设备加密配置**
```yaml
# iOS 配置
设备加密: 自动启用（iOS 8+）
要求: 设置锁屏密码后自动启用

# Android 配置
设备加密: 设置 > 安全 > 加密设备
推荐: 使用硬件级加密
注意: 加密前确保电量充足
```

**2. 强锁屏策略**
```javascript
// 企业设备策略示例
const devicePolicy = {
  // 密码要求
  passwordPolicy: {
    minLength: 8,
    requireComplexity: true,  // 数字+字母+符号
    maxFailedAttempts: 5,     // 5次失败后擦除
    lockTimeout: 1,           // 1分钟自动锁屏
  },

  // 生物识别
  biometricPolicy: {
    allowFingerprint: true,
    allowFaceId: true,
    requireFallbackPassword: true,  // 必须有备用密码
  },

  // 远程管理
  remoteManagement: {
    allowRemoteLock: true,
    allowRemoteWipe: true,
    allowLocationTracking: true,
  }
};
```

**3. 敏感应用保护**
```javascript
// 应用层安全加固
class SecureApp {
  constructor() {
    this.sessionTimeout = 5 * 60 * 1000;  // 5分钟超时
    this.requireAuthOnResume = true;       // 切回前台需认证
  }

  // 应用启动认证
  async onAppStart() {
    const authenticated = await this.authenticate();
    if (!authenticated) {
      // 未通过认证，不加载敏感数据
      return;
    }
    this.startSessionTimer();
  }

  // 会话超时处理
  startSessionTimer() {
    this.sessionTimer = setTimeout(() => {
      this.clearSensitiveData();
      this.requireReauth();
    }, this.sessionTimeout);
  }

  // 清除敏感数据
  clearSensitiveData() {
    // 清除内存中的敏感信息
    this.userToken = null;
    this.userData = null;
  }
}
```

---

## L3 企业版（深度版）

### 设备丢失防御架构

```
┌─────────────────────────────────────────────────────────────┐
│                   设备丢失防御架构                           │
├─────────────────────────────────────────────────────────────┤
│  设备层   │  全盘加密 + 强锁屏 + 安全启动 + 硬件密钥        │
├─────────────────────────────────────────────────────────────┤
│  管理层   │  MDM 远程锁定 + 远程擦除 + 设备追踪 + 策略下发  │
├─────────────────────────────────────────────────────────────┤
│  应用层   │  应用锁定 + 数据隔离 + 会话超时 + 远程登出      │
├─────────────────────────────────────────────────────────────┤
│  响应层   │  丢失报告 + 远程操作 + 证据保全 + 恢复流程      │
└─────────────────────────────────────────────────────────────┘
```

### 检测清单

- [ ] 设备已启用全盘加密
- [ ] 锁屏密码强度足够（8位+复杂度）
- [ ] 启用远程锁定功能
- [ ] 启用远程擦除功能
- [ ] 设置 SIM 卡 PIN 码
- [ ] 关键应用有独立锁
- [ ] 定期数据备份
- [ ] 设备 IMEI 已记录
- [ ] 员工知晓丢失报告流程
- [ ] 有设备丢失应急预案

---

## 参考资料

### 真实案例
- [2023 年数据泄露调查报告 - 设备丢失章节](https://www.verizon.com/business/resources/reports/dbir/)

### 技术文档
- [iOS 安全白皮书](https://www.apple.com/business/docs/iOS_Security_Guide.pdf)
- [Android 企业安全指南](https://www.android.com/enterprise/management/)

### 工具
- [Find My iPhone](https://www.icloud.com/find)
- [Find My Device](https://www.google.com/android/find)
