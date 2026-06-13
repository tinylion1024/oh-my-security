# 隐私泄露风险（Privacy Leak）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: social（社媒账号安全）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: 免费 | L3: 隐私保护服务
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
社媒公开信息被他人收集分析，导致隐私泄露或社会工程攻击。

### 一分钟识别
你的账号是否有以下特征：
- [ ] 账号为公开状态
- [ ] 公开真实姓名和照片
- [ ] 公开位置信息
- [ ] 公开联系方式
- [ ] 公开工作单位
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
设置账号为私密，限制陌生人查看，最小化公开个人信息。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 设置账号为私密
   - [ ] 隐藏联系方式
   - [ ] 关闭位置分享

2. **短期行动**（本周可完成，免费）
   - [ ] 审查历史发布内容
   - [ ] 检查标签和提及
   - [ ] 配置各平台隐私设置

3. **长期行动**（规划中）
   - [ ] 建立隐私保护习惯
   - [ ] 定期审查隐私设置

---

## L2 小团队版（理解版）

### 隐私泄露途径

```
信息收集来源:
1. 公开个人资料
2. 历史发布内容
3. 照片中的元数据
4. 位置签到记录
5. 社交关系分析
6. 互动记录（点赞、评论）
7. 群组参与记录
```

### 隐私保护配置

```javascript
// 社媒隐私配置
const privacySettings = {
  // 账号可见性
  accountVisibility: {
    profile: 'private',           // 私密账号
    posts: 'followers_only',      // 仅粉丝可见
    stories: 'close_friends',     // 密友可见
    activity: 'private'           // 活动隐藏
  },

  // 联系方式
  contactInfo: {
    phone: 'hidden',              // 隐藏手机
    email: 'hidden',              // 隐藏邮箱
    address: 'hidden'             // 隐藏地址
  },

  // 位置信息
  location: {
    shareLocation: false,         // 不分享位置
    disableCheckIn: true,         // 禁用签到
    removeGeoTag: true            // 移除地理标签
  },

  // 搜索设置
  searchability: {
    byPhone: false,               // 不可通过手机搜索
    byEmail: false,               // 不可通过邮箱搜索
    suggestToOthers: false        // 不向他人推荐
  }
};
```

### 检测清单

- [ ] 账号设置为私密
- [ ] 联系方式已隐藏
- [ ] 位置分享已关闭
- [ ] 历史内容已审查
- [ ] 粉丝列表已限制
- [ ] 陌生人无法提及

---

## 参考资料

### 平台资源
- [Instagram 隐私设置](https://help.instagram.com/1160246109836250)
- [Twitter 隐私与安全](https://help.twitter.com/en/safety-and-security)
- [Facebook 隐私检查](https://www.facebook.com/privacy/checkup/)
