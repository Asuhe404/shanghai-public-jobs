#!/bin/bash
# 更新定时任务，将08:35任务改为使用push_markdown.sh

set -e

echo "========================================="
echo "更新定时任务"
echo "时间: $(date '+%Y年%m月%d日 %H:%M:%S')"
echo "========================================="

# 查找现有的网站部署任务
echo "查找现有的网站部署定时任务..."
TASK_INFO=$(openclaw cron list --json | jq '.jobs[] | select(.name | contains("网站部署"))' 2>/dev/null || echo "")

if [ -z "$TASK_INFO" ] || [ "$TASK_INFO" = "null" ] || [ "$TASK_INFO" = "" ]; then
    echo "未找到网站部署定时任务，创建新任务..."
    
    # 创建新任务
    openclaw cron add \
      --name "上海招聘日报推送Markdown" \
      --description "每天早上8:35推送最新日报Markdown到GitHub仓库" \
      --cron "35 8 * * *" \
      --tz "Asia/Shanghai" \
      --session isolated \
      --announce \
      --channel telegram \
      --to "1924648299" \
      --timeout-seconds 300 \
      --message '请执行日报Markdown推送任务。运行命令: cd /home/ubuntu/.openclaw/workspace/web && ./push_markdown.sh'
    
    echo "✅ 创建新定时任务成功"
else
    echo "找到现有任务，提取ID..."
    TASK_ID=$(echo "$TASK_INFO" | jq -r '.id')
    TASK_NAME=$(echo "$TASK_ID" | cut -c 1-8)
    
    echo "现有任务ID: $TASK_ID"
    echo "任务名称: $(echo "$TASK_INFO" | jq -r '.name')"
    
    # 删除旧任务
    echo "删除旧任务..."
    openclaw cron delete "$TASK_ID"
    
    # 创建新任务
    echo "创建新任务..."
    openclaw cron add \
      --name "上海招聘日报推送Markdown" \
      --description "每天早上8:35推送最新日报Markdown到GitHub仓库" \
      --cron "35 8 * * *" \
      --tz "Asia/Shanghai" \
      --session isolated \
      --announce \
      --channel telegram \
      --to "1924648299" \
      --timeout-seconds 300 \
      --message '请执行日报Markdown推送任务。运行命令: cd /home/ubuntu/.openclaw/workspace/web && ./push_markdown.sh'
    
    echo "✅ 更新定时任务成功"
fi

echo "========================================="
echo "定时任务更新完成!"
echo "========================================="
echo ""
echo "新的定时任务流程:"
echo "08:30 → 生成日报Markdown (原有任务)"
echo "08:35 → 推送Markdown到GitHub (更新后的任务)"
echo "08:40 → GitHub Actions生成网站并部署 (自动触发)"
echo ""
echo "全自动化流程已就绪!"