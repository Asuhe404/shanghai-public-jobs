# 上海公职招聘日报网站生成器

本目录包含将Markdown格式的招聘日报转换为静态网站的工具。

## 文件结构

```
web/
├── template.html          # HTML模板（使用Mustache风格变量）
├── generate.py           # Markdown转HTML生成脚本
├── deploy.sh            # 部署到GitHub Pages的脚本
├── update.sh            # 完整更新流程脚本
├── README.md           # 本文件
└── public/             # 生成的静态网站文件
    ├── index.html      # 主页（所有日报索引）
    ├── latest.html     # 最新日报
    ├── 2026-04-09.html # 按日期归档的日报
    └── ...             # 其他静态文件
```

## 使用方法

### 1. 手动生成网站
```bash
cd /home/ubuntu/.openclaw/workspace/web
python3 generate.py
```

### 2. 手动部署到GitHub Pages
```bash
cd /home/ubuntu/.openclaw/workspace/web
./deploy.sh
```

### 3. 完整更新流程（日报+网站+部署）
```bash
cd /home/ubuntu/.openclaw/workspace/web
./update.sh
```

## 自动更新流程

当前的定时任务设置：

1. **08:30（北京时间）**: 生成最新的招聘日报Markdown文件
   - 任务ID: `6811d36c-caea-427b-980d-356f098bcf2b`
   - 输出: `/home/ubuntu/.openclaw/workspace/reports/shanghai-public-jobs/latest.md`

2. **08:35（北京时间）**: 生成静态网站并部署（建议添加）
   ```bash
   openclaw cron add --name "上海招聘日报网站生成" --description "生成静态网站并部署到GitHub Pages" --cron "35 8 * * *" --tz "Asia/Shanghai" --session isolated --announce --channel telegram --to "1924648299" --message "请执行网站生成任务。运行命令: cd /home/ubuntu/.openclaw/workspace/web && ./update.sh"
   ```

## 网站功能

生成的网站包含以下功能：

### 1. 响应式设计
- 适配手机、平板、电脑
- 使用Bootstrap 5框架

### 2. 搜索功能
- 实时搜索职位、单位、关键词
- 支持中文搜索

### 3. 分类筛选
- 按公务员/事业编/国企筛选
- 多选筛选

### 4. 统计信息
- 实时显示各类别数量
- 总招聘数统计

### 5. 历史归档
- 按日期归档所有日报
- 一键查看历史记录

## 技术细节

### 数据流
```
招聘信息抓取 → Markdown日报 → HTML生成 → GitHub Pages部署
```

### 模板系统
使用简单的字符串替换模板系统，支持以下变量：
- `{{title}}`: 页面标题
- `{{date}}`: 日报日期
- `{{collection_time}}`: 采集时间
- `{{search_scope}}`: 检索范围
- `{{current_year}}`: 当前年份
- `{{#highlights}}`...`{{/highlights}}`: 重点招聘列表
- `{{#gwy_jobs}}`...`{{/gwy_jobs}}`: 公务员招聘列表
- `{{#sy_jobs}}`...`{{/sy_jobs}}`: 事业编招聘列表
- `{{#gq_jobs}}`...`{{/gq_jobs}}`: 国企招聘列表

### 部署配置
需要配置以下环境变量（可选）：
- `GITHUB_TOKEN`: GitHub个人访问令牌
- `REPO_URL`: GitHub仓库URL

默认使用公开仓库：`https://github.com/Asuhe404/shanghai-public-jobs.git`

## 自定义设置

### 1. 更改网站样式
编辑 `template.html` 中的CSS样式。

### 2. 更改部署目标
编辑 `deploy.sh` 中的 `REPO_URL` 和 `BRANCH` 变量。

### 3. 添加自定义域名
在 `public/` 目录下创建 `CNAME` 文件，写入域名。

## 故障排除

### Q: 生成脚本报错 "未找到最新日报文件"
A: 确保日报生成任务已成功运行，检查 `/home/ubuntu/.openclaw/workspace/reports/shanghai-public-jobs/latest.md` 是否存在。

### Q: 部署脚本报Git错误
A: 检查网络连接和GitHub仓库权限。确保仓库存在且有写入权限。

### Q: 网站搜索功能不工作
A: 检查浏览器控制台是否有JavaScript错误。确保所有职位数据正确加载。

### Q: 样式显示不正常
A: 检查网络连接，确保能访问CDN上的Bootstrap和Font Awesome资源。

## 扩展功能建议

1. **RSS订阅**: 添加RSS feed供用户订阅
2. **邮件通知**: 重要职位邮件提醒
3. **数据导出**: JSON/CSV格式导出
4. **高级搜索**: 按薪资、地点、经验筛选
5. **地图展示**: 职位地理位置可视化

## 许可证

MIT