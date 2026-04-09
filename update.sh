#!/bin/bash
# 上海公职招聘日报完整更新流程
# 1. 运行日报生成（由cron触发）
# 2. 生成静态网站
# 3. 部署到GitHub Pages

set -e

echo "========================================="
echo "上海公职招聘日报更新流程开始"
echo "时间: $(date '+%Y年%m月%d日 %H:%M:%S')"
echo "========================================="

# 工作目录
WORKSPACE_DIR="/home/ubuntu/.openclaw/workspace"
WEB_DIR="$WORKSPACE_DIR/web"
REPORTS_DIR="$WORKSPACE_DIR/reports/shanghai-public-jobs"

# 0. 检查最新的日报文件
LATEST_MD="$REPORTS_DIR/latest.md"
if [ ! -f "$LATEST_MD" ]; then
    echo "错误: 未找到最新日报文件: $LATEST_MD"
    echo "请先运行日报生成任务"
    exit 1
fi

echo "✓ 找到最新日报: $LATEST_MD"

# 1. 生成静态网站
echo "生成静态网站..."
cd "$WEB_DIR"
if [ -f "generate.py" ]; then
    python3 generate.py
    echo "✓ 静态网站生成完成"
else
    echo "错误: 未找到generate.py"
    exit 1
fi

# 2. 检查是否配置了GitHub部署
if [ -f "deploy.sh" ] && [ -x "deploy.sh" ]; then
    echo "部署到GitHub Pages..."
    ./deploy.sh
    echo "✓ 部署完成"
else
    echo "⚠ 未配置GitHub部署，跳过部署步骤"
    echo "生成的网站文件在: $WEB_DIR/public/"
    echo "手动部署命令: cd $WEB_DIR && ./deploy.sh"
fi

echo "========================================="
echo "更新流程完成!"
echo "========================================="
echo ""
echo "重要链接:"
echo "- 本地最新日报: $REPORTS_DIR/latest.md"
echo "- 本地HTML文件: $WEB_DIR/public/latest.html"
echo "- 本地主页: $WEB_DIR/public/index.html"
echo "- GitHub Pages: https://Asuhe404.github.io/shanghai-public-jobs/"
echo ""