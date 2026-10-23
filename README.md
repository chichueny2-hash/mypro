# iPhone 短信验证码自动同步

手机 A 收到短信验证码后，「快捷指令」自动化会提取验证码，再用 iMessage 发给手机 B。

```
短信 ──▶ 手机 A：快捷指令自动化（信息包含「验证码」）
            匹配文本 (?<!\d)\d{4,8}(?!\d) → 取第一项 → 发送 iMessage
                                                    └──▶ 手机 B 弹出通知
```

两台手机可以共用同一个 iCloud，但 **B 的「信息」App 要单独登录一个新的 Apple 账户**。否则 A 发给「自己」的消息，B 不会弹通知。

## 文件

| 文件 | 说明 |
|---|---|
| [`验证码同步设置指南.pdf`](验证码同步设置指南.pdf) | 图文设置指南，分别说明两台手机怎么设置（**从这里开始**） |
| `guide/guide.html` | PDF 的源文件 |
| `guide/build_pdf.mjs` | 重新生成 PDF：`NODE_PATH=$(npm root -g) node guide/build_pdf.mjs`（需要 Playwright） |
| `shortcut/make_shortcut.py` | 生成「转发验证码」快捷指令文件（可选，见下文） |

## 两种搭建方式

### 方式一：在手机上手动搭建（推荐）

按 PDF 第 4–5 页操作，直接在自动化里添加 4 个动作，大约 5 分钟，不需要 Mac。

### 方式二：导入快捷指令文件（需要 Mac）

```bash
python3 shortcut/make_shortcut.py            # 生成 shortcut/转发验证码.unsigned.shortcut
# 在 Mac 上签名（iOS 只能导入签过名的快捷指令）：
shortcuts sign --mode anyone --input 转发验证码.unsigned.shortcut --output 转发验证码.shortcut
```

把签好名的文件 AirDrop 到手机 A 导入，导入时会让你填收件人（B 的 Apple 账户）。注意：自动化本身没法导入，还是要在 A 上新建「信息」自动化（PDF 第 4 页），动作里只放一个 **运行快捷指令 → 转发验证码**，输入选 **快捷指令输入**。

> 这个文件是按快捷指令的 plist 格式手写生成的，**还没有在真机上验证过**。导入失败或者动作显示不对的话，请改用方式一。
