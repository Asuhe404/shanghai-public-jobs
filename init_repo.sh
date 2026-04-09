#!/bin/bash
# 初始化GitHub仓库，推送web目录内容

set -e

# 从环境变量获取GitHub Token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "错误: 请设置 GITHUB_TOKEN 环境变量"
    echo "例如: export GITHUB_TOKEN=ghp_xxxx"
    exit 1
fi

REPO_URL="https://${GITHUB_TOKEN}@github.com/Asuhe404/shanghai-public-jobs.git"

echo "========================================="
echo "初始化GitHub仓库"
echo "时间: $(date '+%Y年%m月%d日 %H:%M:%S')"
echo "========================================="

cd /home/ubuntu/.openclaw/workspace/web

# 检查是否已经是git仓库
if [ -d ".git" ]; then
    echo "⚠ 已经是git仓库，跳过初始化"
    echo "当前远程仓库:"
    git remote -v
    exit 0
fi

# 初始化git仓库
echo "初始化git仓库..."
git init

# 配置Git用户信息
git config user.email "agent@openclaw.ai"
git config user.name "OpenClaw Agent"

git add .
git commit -m "初始提交：上海公职招聘日报网站生成器和GitHub Actions工作流

包含：
- GitHub Actions工作流 (.github/workflows/deploy.yml)
- 网站生成器 (generate.py)
- HTML模板 (template.html)
- Markdown推送脚本 (push_markdown.sh)
- 部署脚本 (deploy.sh, update.sh)
- 文档 (README.md)"

# 添加远程仓库并推送
echo "添加远程仓库..."
git remote add origin "$REPO_URL"
git branch -M main

echo "推送到GitHub..."
git push -u origin main

echo "========================================="
echo "初始化完成!"
echo "========================================="
echo ""
echo "重要信息:"
echo "- 仓库地址: https://github.com/Asuhe404/shanghai-public-jobs"
echo "- GitHub Actions将在推送后自动运行"
echo "- 网站地址: https://Asuhe404.github.io/shanghai-public-jobs/"
echo ""
echo "下一步:"
echo "1. 手动测试推送日报: ./push_markdown.sh"
echo "2. 更新定时任务使用 push_markdown.sh"
echo "3. 明天08:30开始全自动运行"
echo ""