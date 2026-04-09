#!/bin/bash
# 推送日报Markdown到GitHub仓库

set -e

echo "========================================="
echo "推送日报Markdown到GitHub仓库"
echo "时间: $(date '+%Y年%m月%d日 %H:%M:%S')"
echo "========================================="

# 配置
REPO_URL="https://github.com/Asuhe404/shanghai-public-jobs.git"
REPO_DIR="/tmp/shanghai-public-jobs-repo"
BRANCH="main"
SOURCE_MD="/home/ubuntu/.openclaw/workspace/reports/shanghai-public-jobs/latest.md"
TARGET_DIR="reports/shanghai-public-jobs"

# 检查源文件
if [ ! -f "$SOURCE_MD" ]; then
    echo "错误: 未找到源日报文件: $SOURCE_MD"
    exit 1
fi

echo "✓ 找到源日报文件: $SOURCE_MD"

# 使用GitHub Token进行身份验证（如果设置了）
if [ -n "$GITHUB_TOKEN" ]; then
    AUTH_REPO_URL="https://${GITHUB_TOKEN}@github.com/Asuhe404/shanghai-public-jobs.git"
    echo "使用GITHUB_TOKEN进行身份验证"
else
    AUTH_REPO_URL="$REPO_URL"
    echo "警告: 未设置GITHUB_TOKEN，使用公开仓库URL（可能需要手动身份验证）"
fi

# 清理并创建工作目录
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

# 克隆仓库
echo "克隆仓库..."
git clone --branch "$BRANCH" --depth 1 "$AUTH_REPO_URL" .

# 创建目标目录
mkdir -p "$TARGET_DIR"

# 复制日报文件
echo "复制日报文件..."
cp "$SOURCE_MD" "$TARGET_DIR/"

# 提取日期用于文件名
DATE=$(date +'%Y-%m-%d')
cp "$SOURCE_MD" "$TARGET_DIR/${DATE}.md"

echo "✓ 复制文件完成: $TARGET_DIR/latest.md, $TARGET_DIR/${DATE}.md"

# 配置Git用户
git config user.email "agent@openclaw.ai"
git config user.name "OpenClaw Agent"

# 提交更改
echo "提交更改..."
git add "$TARGET_DIR/"
git commit -m "更新日报: ${DATE}" || {
    echo "没有更改可提交"
    exit 0
}

# 推送到GitHub
echo "推送到GitHub..."
git push origin "$BRANCH"

echo "========================================="
echo "推送完成!"
echo "========================================="
echo ""
echo "重要信息:"
echo "- 日报文件已推送到: $REPO_URL"
echo "- 最新文件: $TARGET_DIR/latest.md"
echo "- 归档文件: $TARGET_DIR/${DATE}.md"
echo ""
echo "GitHub Actions将自动触发网站生成和部署"
echo "网站地址: https://Asuhe404.github.io/shanghai-public-jobs/"
echo ""