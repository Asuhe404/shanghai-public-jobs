#!/bin/bash
# 上海公职招聘日报部署脚本
# 将生成的静态网站推送到GitHub Pages

set -e

# 配置
REPO_URL="https://github.com/Asuhe404/shanghai-public-jobs.git"
PUBLIC_DIR="/home/ubuntu/.openclaw/workspace/web/public"
WORK_DIR="/tmp/shanghai-public-jobs-deploy"
BRANCH="gh-pages"

echo "开始部署到GitHub Pages..."

# 1. 确保public目录存在
if [ ! -d "$PUBLIC_DIR" ]; then
    echo "错误: public目录不存在: $PUBLIC_DIR"
    exit 1
fi

# 2. 清理并创建工作目录
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

# 3. 克隆仓库（如果已存在）
cd "$WORK_DIR"
if [ ! -d ".git" ]; then
    echo "克隆仓库..."
    git clone --branch "$BRANCH" --single-branch "$REPO_URL" . || {
        # 如果分支不存在，创建空仓库
        echo "分支不存在，创建新仓库..."
        rm -rf "$WORK_DIR"/*
        git init
        git remote add origin "$REPO_URL"
        git checkout -b "$BRANCH"
    }
fi

# 4. 清空当前分支内容（保留.git目录）
echo "清空当前内容..."
find . -maxdepth 1 ! -name '.git' ! -name '.' ! -name '..' -exec rm -rf {} +

# 5. 复制新内容
echo "复制新内容..."
cp -r "$PUBLIC_DIR"/* .

# 6. 添加CNAME文件（如果需要自定义域名）
if [ ! -f "CNAME" ]; then
    echo "shanghai-jobs.github.io" > CNAME 2>/dev/null || true
fi

# 7. 添加README
cat > README.md << 'EOF'
# 上海公职招聘日报网站

这是一个自动生成的静态网站，每日更新上海地区公务员、事业单位、国有企业的招聘信息。

## 如何工作
1. 每日08:30（北京时间）自动抓取最新招聘信息
2. AI整理并生成Markdown报告
3. 自动转换为HTML静态网站
4. 自动部署到GitHub Pages

## 本地开发
```bash
cd web
python3 generate.py
```

## 技术栈
- OpenClaw AI Agent
- Python + Markdown解析
- Bootstrap 5 + JavaScript
- GitHub Pages

## 许可证
MIT
EOF

# 8. 提交更改
echo "提交更改..."
git add -A
git config user.email "agent@openclaw.ai"
git config user.name "OpenClaw Agent"
git commit -m "自动更新: $(date '+%Y年%m月%d日 %H:%M')" || {
    echo "没有更改可提交"
    exit 0
}

# 9. 推送到GitHub
echo "推送到GitHub..."
git push origin "$BRANCH"

echo "部署完成!"
echo "网站地址: https://Asuhe404.github.io/shanghai-public-jobs/"
echo "最新日报: https://Asuhe404.github.io/shanghai-public-jobs/latest.html"