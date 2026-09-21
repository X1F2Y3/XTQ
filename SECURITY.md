# 安全策略

## 范围

TDF 是**本地运行的实验性 Python 研究项目**。它默认在 Mock 模式下工作，
不产生任何网络请求。

安全相关面因此是两块：**接入真实模型时的密钥处理**，以及**记忆数据的落盘**。

## 密钥处理

- `src/config.py` 中的 `model_api_key` **不得硬编码**。请通过参数 / 环境变量传入：

  ```bash
  export TDF_API_KEY=sk-...
  python src/main.py --provider openai
  ```

- `.env` 与 `.env.*` 已在 `.gitignore` 中排除；请勿用 `git add -f` 绕过。
- **提交 PR 前自查**：`git diff --cached` 里不得出现任何真实 key、token、
  账号邮箱或本机绝对路径。

## 数据落盘

- 记忆数据（`memory_data/`）默认写入仓库本地目录，已在 `.gitignore` 中排除。
- 若你修改了落盘路径，请确保新路径同样被忽略，避免把记忆内容误提交。

## 报告问题

请**不要**为安全问题开公开 issue。用 GitHub 的私密通道：

<https://github.com/X1F2Y3/XTQ/security/advisories/new>

请附：commit sha、复现步骤、影响范围。

## 不在范围内

- 本项目为实验性研究代码，**不承诺任何稳定性或安全性保证**（见 LICENSE 免责条款）。
- "外挂架构会涌现出什么行为" 属于研究议题，不是安全漏洞 —— 请走 issue 讨论。
