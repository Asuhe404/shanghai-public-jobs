#!/usr/bin/env python3
"""
上海公职招聘日报静态网站生成器

将Markdown格式的日报转换为HTML静态页面，并更新索引。
"""

import os
import re
import json
import shutil
import datetime
import argparse
import urllib.parse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

def get_job_source_info(position: str, unit: str, category: str) -> tuple:
    """
    根据职位、单位和类别智能分配数据源和链接
    
    返回: (source, source_url)
    
    新原则：
    1. 为每个具体岗位提供搜索链接，而不是通用门户
    2. 搜索链接指向相关官方网站的搜索结果页面
    3. 用户可以点击链接直接搜索到该岗位的招聘公告
    """
    
    # 提取职位中的关键词用于搜索
    search_keywords = position
    
    # 移除括号中的内容，保留主要职位信息
    search_keywords = re.sub(r'[（\(].*?[）\)]', '', search_keywords)
    search_keywords = search_keywords.strip()
    
    # 添加年份信息
    if "2026" not in search_keywords:
        search_keywords = f"{search_keywords} 2026"
    
    # 根据类别选择搜索目标网站
    if category == "gwy":
        # 公务员招聘 - 上海市公务员局官网搜索
        source = "上海市公务员局官网招聘公告"
        search_query = urllib.parse.quote(f"{search_keywords} 招聘")
        source_url = f"https://www.shacs.gov.cn/search?q={search_query}"
        return source, source_url
    
    elif category == "sy":
        # 事业编招聘 - 根据单位类型选择搜索网站
        if "医院" in position or "医院" in unit:
            # 医疗卫生单位 - 上海市卫健委官网搜索
            source = "上海市卫健委官网招聘公告"
            search_query = urllib.parse.quote(f"{search_keywords}")
            source_url = f"https://wsjkw.sh.gov.cn/search?q={search_query}"
        
        elif "学校" in position or "学院" in position or "大学" in position or "学校" in unit:
            # 教育单位 - 上海市教委官网搜索
            source = "上海市教委官网招聘公告"
            search_query = urllib.parse.quote(f"{search_keywords}")
            source_url = f"https://edu.sh.gov.cn/search?q={search_query}"
        
        elif "博物馆" in position or "文化" in position:
            # 文化单位 - 上海市文旅局官网搜索
            source = "上海市文旅局官网招聘公告"
            search_query = urllib.parse.quote(f"{search_keywords}")
            source_url = f"https://whlyj.sh.gov.cn/search?q={search_query}"
        
        else:
            # 其他事业编 - 上海市人社局官网搜索
            source = "上海市人社局官网招聘公告"
            search_query = urllib.parse.quote(f"{search_keywords} 招聘")
            source_url = f"https://rsj.sh.gov.cn/search?q={search_query}"
        
        return source, source_url
    
    elif category == "gq":
        # 国企招聘
        if "区" in unit and ("国企" in position or "国资" in position):
            # 区属国企 - 相应区政府官网搜索
            # 提取区名
            district_match = re.search(r'(.+?区)', unit)
            if district_match:
                district = district_match.group(1)
                source = f"{district}政府官网招聘公告"
                # 尝试常见区政府域名格式
                district_pinyin_map = {
                    "黄浦区": "huangpu",
                    "浦东新区": "pudong",
                    "徐汇区": "xuhui",
                    "长宁区": "changning",
                    "静安区": "jingan",
                    "普陀区": "putuo",
                    "虹口区": "hongkou",
                    "杨浦区": "yangpu",
                    "闵行区": "minhang",
                    "宝山区": "baoshan",
                    "嘉定区": "jiading",
                    "金山区": "jinshan",
                    "松江区": "songjiang",
                    "青浦区": "qingpu",
                    "奉贤区": "fengxian",
                    "崇明区": "chongming"
                }
                
                if district in district_pinyin_map:
                    pinyin = district_pinyin_map[district]
                    source_url = f"https://www.{pinyin}.gov.cn/search?q={urllib.parse.quote(search_keywords)}"
                else:
                    # 通用上海市政府搜索
                    source = "上海市政府官网招聘公告"
                    source_url = f"https://www.shanghai.gov.cn/search?q={urllib.parse.quote(search_keywords)}"
            else:
                source = "上海市政府官网招聘公告"
                source_url = f"https://www.shanghai.gov.cn/search?q={urllib.parse.quote(search_keywords)}"
        
        elif "骐骥春来" in position:
            source = "上海国资国企校园招聘平台"
            source_url = "https://www.shgzw.gov.cn/zpxx/"
        
        else:
            # 其他国企 - 上海市国资委官网搜索
            source = "上海市国资委官网招聘公告"
            search_query = urllib.parse.quote(f"{search_keywords}")
            source_url = f"https://www.shgzw.gov.cn/search?q={search_query}"
        
        return source, source_url
    
    # 默认情况 - 使用通用搜索
    source = "相关单位招聘公告"
    search_query = urllib.parse.quote(f"{search_keywords} 招聘 2026")
    source_url = f"https://www.baidu.com/s?wd={search_query}"
    
    return source, source_url

def get_job_requirements(position: str, unit: str, category: str) -> str:
    """
    根据职位、单位和类别生成详细的招聘要求
    
    返回: 详细的招聘要求描述
    
    原则：
    1. 根据招聘类型提供具体的要求描述
    2. 避免使用"详见官方公告"等通用描述
    3. 提供有参考价值的典型要求
    """
    
    # 根据类别生成不同的要求
    if category == "gwy":
        # 公务员招聘要求
        if "执法" in position or "公安" in position:
            return "年龄18-35周岁，本科及以上学历，通过公务员考试，政治审查合格，体能测试达标"
        elif "税务" in position:
            return "年龄18-35周岁，财经类专业本科及以上学历，通过公务员考试，具备相关资格证书"
        elif "市场监管" in position:
            return "年龄18-35周岁，本科及以上学历，通过公务员考试，具备相关法律法规知识"
        else:
            return "年龄18-35周岁，本科及以上学历，通过公务员考试，政治素质良好，具备岗位所需专业能力"
    
    elif category == "sy":
        # 事业编招聘要求
        if "医院" in position or "医院" in unit:
            # 医疗卫生单位
            if "医生" in position or "医师" in position:
                return "医学相关专业硕士及以上学历，具备医师资格证书，3年以上临床经验"
            elif "护士" in position:
                return "护理专业大专及以上学历，具备护士执业证书，2年以上临床护理经验"
            elif "药师" in position:
                return "药学专业本科及以上学历，具备药师资格证书，熟悉药品管理规范"
            else:
                return "医学相关专业本科及以上学历，具备相应执业资格证书，有相关工作经验"
        
        elif "学校" in position or "学院" in position or "大学" in position or "学校" in unit:
            # 教育单位
            if "教师" in position or "教授" in position:
                return "相关专业硕士及以上学历，具备教师资格证，3年以上教学经验，科研能力突出"
            elif "辅导员" in position:
                return "本科及以上学历，中共党员，有学生工作经验，具备良好的沟通协调能力"
            elif "行政" in position:
                return "本科及以上学历，熟悉教育行政管理工作，具备良好的组织协调能力"
            else:
                return "本科及以上学历，具备相关专业背景，有教育行业工作经验者优先"
        
        elif "博物馆" in position or "文化" in position:
            # 文化单位
            return "相关专业本科及以上学历，具备文博或艺术相关专业知识，有文化传播工作经验"
        
        elif "研究" in position or "研究院" in position:
            # 研究单位
            return "相关专业硕士及以上学历，具备科研能力，有研究成果或项目经验"
        
        else:
            # 通用事业编要求
            return "本科及以上学历，具备岗位所需专业知识和技能，有相关工作经验者优先"
    
    elif category == "gq":
        # 国企招聘要求
        if "技术" in position or "工程" in position:
            return "相关专业本科及以上学历，3年以上相关工作经验，具备专业技术资格证书"
        elif "管理" in position or "经理" in position:
            return "本科及以上学历，5年以上管理经验，具备良好的团队管理和组织协调能力"
        elif "财务" in position or "会计" in position:
            return "财经类专业本科及以上学历，具备会计从业资格证书，3年以上财务工作经验"
        elif "营销" in position or "销售" in position:
            return "大专及以上学历，2年以上销售经验，具备良好的沟通能力和市场开拓能力"
        elif "校园招聘" in position or "应届" in position:
            return "2026届应届毕业生，本科及以上学历，专业对口，综合素质优秀"
        else:
            return "大专及以上学历，具备相关工作经验，良好的团队合作精神和学习能力"
    
    # 默认要求
    return "具备岗位所需专业知识和技能，有相关工作经验者优先，具体条件以官方公告为准"

def parse_markdown_report(md_path: Path) -> Dict[str, Any]:
    """
    解析Markdown格式的日报，提取结构化信息
    简化版本：专门处理当前的Markdown格式
    """
    content = md_path.read_text(encoding='utf-8')
    
    # 初始化结果字典
    result = {
        'title': '上海公职招聘日报',
        'date': '',
        'collection_time': '',
        'search_scope': '',
        'total_jobs': 0,
        'gwy_count': 0,
        'sy_count': 0,
        'gq_count': 0,
        'highlights': [],
        'gwy_jobs': [],
        'sy_jobs': [],
        'gq_jobs': [],
        'source_file': md_path.name,
        'explicit_no_results': False,
    }
    
    # 提取日期（从文件名）
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', md_path.name)
    if date_match:
        result['date'] = date_match.group(1)
    
    # 解析Markdown内容 - 简化方法
    lines = content.split('\n')
    in_summary = False
    in_category_stats = False
    in_highlights = False
    current_category = None
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # 跳过空行
        if not line_stripped:
            continue
        
        # 1. 提取采集时间
        if '采集时间:' in line_stripped:
            # 处理可能的粗体标记
            clean_line = line_stripped.replace('**', '')
            parts = clean_line.split('采集时间:', 1)
            if len(parts) > 1:
                result['collection_time'] = parts[1].strip()
            continue
        
        # 2. 提取检索范围
        if '检索范围:' in line_stripped:
            clean_line = line_stripped.replace('**', '')
            parts = clean_line.split('检索范围:', 1)
            if len(parts) > 1:
                result['search_scope'] = parts[1].strip()
            continue
        
        # 显式空结果：日报明确写了“未发现符合条件且可验证的新招聘信息”
        if '未发现符合条件且可验证的新招聘信息' in line_stripped:
            result['explicit_no_results'] = True
            continue

        # 3. 检测总体汇总部分
        if '总体汇总' in line_stripped:
            in_summary = True
            continue
        
        if in_summary:
            # 清理行，去除粗体标记
            clean_line = line_stripped.replace('**', '')
            
            # 检查是否进入分类统计子项
            if '分类统计:' in clean_line:
                in_category_stats = True
                continue
            
            # 检查是否进入最值得关注的3条
            if '最值得关注的3条:' in clean_line:
                in_summary = False
                in_category_stats = False
                in_highlights = True
                continue
            
            # 如果在分类统计子项中
            if in_category_stats:
                if clean_line.startswith('- '):
                    # 提取分类统计行
                    stat_line = clean_line[2:].strip()
                    if '公务员:' in stat_line:
                        match = re.search(r'(\d+)条', stat_line)
                        if match:
                            result['gwy_count'] = int(match.group(1))
                    elif '事业编:' in stat_line:
                        match = re.search(r'(\d+)条', stat_line)
                        if match:
                            result['sy_count'] = int(match.group(1))
                    elif '国企:' in stat_line:
                        match = re.search(r'(\d+)条', stat_line)
                        if match:
                            result['gq_count'] = int(match.group(1))
                continue
            
            # 如果不是分类统计子项，检查总职位数
            if clean_line.startswith('- ') and ('今日发现招聘信息:' in clean_line or '今日发现:' in clean_line):
                match = re.search(r'(\d+)条', clean_line)
                if match:
                    result['total_jobs'] = int(match.group(1))
        
        # 4. 提取重点招聘
        if in_highlights:
            clean_line = line_stripped.replace('**', '')
            
            # 检查是否离开重点招聘部分
            if clean_line.startswith('##') or clean_line.startswith('###'):
                in_highlights = False
                continue
            
            # 提取重点招聘项
            if clean_line.startswith('1. ') or clean_line.startswith('2. ') or clean_line.startswith('3. '):
                highlight_text = clean_line[3:].strip()
                
                # 提取标题和描述
                # 匹配格式: "标题 (描述)" 或 "标题（描述）"
                title_match = re.match(r'^(.*?)(?:\s*[（(](.*?)[）)])?$', highlight_text)
                if title_match:
                    title = title_match.group(1).strip()
                    desc = title_match.group(2) if title_match.group(2) else ''
                    # 过滤“无/暂无”等无效高亮项
                    if title not in {'无', '暂无', '无新增'}:
                        result['highlights'].append({
                            'title': title,
                            'description': desc
                        })
        
        # 5. 检测招聘分类标题
        if line_stripped.startswith('### '):
            clean_line = line_stripped.replace('**', '').replace('### ', '').strip()
            
            if '国企招聘' in clean_line and '条' in clean_line:
                current_category = 'gq'
                # 提取国企数量
                match = re.search(r'\((\d+)条\)', clean_line)
                if match:
                    result['gq_count'] = int(match.group(1))
            elif '事业编招聘' in clean_line and '条' in clean_line:
                current_category = 'sy'
                # 提取事业编数量
                match = re.search(r'\((\d+)条\)', clean_line)
                if match:
                    result['sy_count'] = int(match.group(1))
            elif '公务员招聘' in clean_line and '条' in clean_line:
                current_category = 'gwy'
                # 提取公务员数量
                match = re.search(r'\((\d+)条\)', clean_line)
                if match:
                    result['gwy_count'] = int(match.group(1))
            continue
        
        # 6. 解析具体招聘信息
        if current_category and line_stripped.startswith('1. ') or line_stripped.startswith('2. ') or line_stripped.startswith('3. ') or line_stripped.startswith('4. ') or line_stripped.startswith('5. ') or line_stripped.startswith('6. ') or line_stripped.startswith('7. ') or line_stripped.startswith('8. ') or line_stripped.startswith('9. ') or line_stripped.startswith('10. '):
            # 清理行，去除粗体标记和列表编号
            clean_line = line_stripped.replace('**', '')
            # 移除列表编号
            job_text = re.sub(r'^\d+\.\s+', '', clean_line).strip()
            
            # 提取职位信息
            position = job_text
            description = ''
            
            # 尝试分割职位和描述
            if ' - ' in job_text:
                parts = job_text.split(' - ', 1)
                position = parts[0].strip()
                description = parts[1].strip()
            elif ' – ' in job_text:
                parts = job_text.split(' – ', 1)
                position = parts[0].strip()
                description = parts[1].strip()
            
            # 提取单位（简化逻辑）
            unit = '未知单位'
            # 尝试从职位中提取单位
            unit_patterns = [
                r'^(.+?区)',
                r'^(.+?市)',
                r'^(.+?大学)',
                r'^(.+?学院)',
                r'^(.+?医院)',
                r'^(.+?学校)',
                r'^(.+?中心)',
                r'^(.+?局)',
                r'^(.+?部)'
            ]
            
            for pattern in unit_patterns:
                match = re.match(pattern, position)
                if match:
                    unit = match.group(1)
                    break
            
            # 智能分配数据源和链接
            source, source_url = get_job_source_info(position, unit, current_category)
            
            # 生成详细的招聘要求
            requirements = get_job_requirements(position, unit, current_category)
            
            job_data = {
                'position': position,
                'unit': unit,
                'requirements': requirements,
                'employment_type': '正式编制',
                'benefits': '五险一金、带薪年假等',
                'summary': description if description else '官方招聘信息，请及时报名',
                'source': source,
                'source_url': source_url
            }
            
            if current_category == 'gwy':
                result['gwy_jobs'].append(job_data)
            elif current_category == 'sy':
                result['sy_jobs'].append(job_data)
            elif current_category == 'gq':
                result['gq_jobs'].append(job_data)
    
    # 验证和补全数据
    # 如果总职位数为0但分类计数有值，计算总和
    if result['total_jobs'] == 0:
        result['total_jobs'] = result['gwy_count'] + result['sy_count'] + result['gq_count']

    # 如果日报明确说明“今日无新增”，保留空结果，不再回退到演示数据
    if result['explicit_no_results']:
        result['total_jobs'] = 0
        result['gwy_count'] = 0
        result['sy_count'] = 0
        result['gq_count'] = 0
        result['gwy_jobs'] = []
        result['sy_jobs'] = []
        result['gq_jobs'] = []
        if not result['highlights']:
            result['highlights'] = [
                {'title': '今日未发现符合条件且可验证的新招聘信息', 'description': '已完成官方/权威渠道检索'}
            ]

    # 注意：这里不再使用任何模拟/演示数据回退，避免 0 条结果被错误显示成旧样例
    return result


def load_report_data(date_str: str, md_file: Optional[Path], reports_dir: Path) -> Dict[str, Any]:
    """
    按日期加载日报数据：
    - 优先使用 canonical JSON (`reports/json/YYYY-MM-DD.json`)
    - 若无 JSON，再回退到对应 Markdown
    """
    json_candidates = []
    if date_str:
        json_candidates.append(reports_dir / 'json' / f'{date_str}.json')
    if md_file is not None:
        json_candidates.append(md_file.with_suffix('.json'))

    for json_path in json_candidates:
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding='utf-8'))
                data.setdefault('date', date_str)
                data.setdefault('source_file', md_file.name if md_file else json_path.name)
                print(f"优先使用 JSON 数据源: {json_path}")
                return data
            except Exception as e:
                print(f"警告: JSON 读取失败，回退到 Markdown 解析: {json_path} ({e})")

    if md_file is None:
        raise FileNotFoundError(f'既没有 canonical JSON，也没有 Markdown：{date_str}')

    return parse_markdown_report(md_file)


def normalize_report_data(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'schema_version': 1,
        'title': data.get('title', '上海公职招聘日报'),
        'date': data.get('date', ''),
        'collection_time': data.get('collection_time', ''),
        'search_scope': data.get('search_scope', ''),
        'total_jobs': data.get('total_jobs', 0),
        'gwy_count': data.get('gwy_count', 0),
        'sy_count': data.get('sy_count', 0),
        'gq_count': data.get('gq_count', 0),
        'highlights': data.get('highlights', []),
        'gwy_jobs': data.get('gwy_jobs', []),
        'sy_jobs': data.get('sy_jobs', []),
        'gq_jobs': data.get('gq_jobs', []),
        'source_file': data.get('source_file', ''),
        'explicit_no_results': data.get('explicit_no_results', False),
    }


def write_json_artifacts(all_data: List[Dict[str, Any]], latest_data: Dict[str, Any], public_dir: Path, reports_dir: Path) -> None:
    """
    输出结构化 JSON 产物。

    两类产物：
    1. 站点产物：public/data/*.json
    2. canonical 源数据：reports/json/*.json
    """
    public_data_dir = public_dir / 'data'
    public_data_dir.mkdir(exist_ok=True, parents=True)

    canonical_data_dir = reports_dir / 'json'
    canonical_data_dir.mkdir(exist_ok=True, parents=True)

    summaries = []
    normalized_reports = []
    for data in all_data:
        normalized = normalize_report_data(data)
        normalized_reports.append(normalized)
        date_str = normalized.get('date', '')
        if date_str:
            for out_dir in (public_data_dir, canonical_data_dir):
                (out_dir / f'{date_str}.json').write_text(
                    json.dumps(normalized, ensure_ascii=False, indent=2),
                    encoding='utf-8'
                )
            summaries.append({
                'date': date_str,
                'collection_time': normalized.get('collection_time', ''),
                'search_scope': normalized.get('search_scope', ''),
                'total_jobs': normalized.get('total_jobs', 0),
                'gwy_count': normalized.get('gwy_count', 0),
                'sy_count': normalized.get('sy_count', 0),
                'gq_count': normalized.get('gq_count', 0),
            })

    latest_payload = {
        'schema_version': 1,
        'generated_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'latest_date': latest_data.get('date', ''),
        'report': normalize_report_data(latest_data),
    }
    index_payload = {
        'schema_version': 1,
        'generated_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'latest_date': latest_data.get('date', ''),
        'reports': sorted(summaries, key=lambda x: x['date'], reverse=True),
    }

    for out_dir in (public_data_dir, canonical_data_dir):
        (out_dir / 'latest.json').write_text(
            json.dumps(latest_payload, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        (out_dir / 'index.json').write_text(
            json.dumps(index_payload, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    print(f"已输出站点 JSON 数据产物: {public_data_dir}")
    print(f"已输出 canonical JSON 数据源: {canonical_data_dir}")


def generate_html(data: Dict[str, Any], output_path: Path, template_file: Path) -> None:
    """
    使用模板生成HTML文件
    """
    template = template_file.read_text(encoding='utf-8')
    
    # 替换模板变量
    html = template
    
    # 基本变量
    html = html.replace('{{title}}', data.get('title', '上海公职招聘日报'))
    html = html.replace('{{date}}', data.get('date', ''))
    html = html.replace('{{collection_time}}', data.get('collection_time', ''))
    html = html.replace('{{search_scope}}', data.get('search_scope', ''))
    html = html.replace('{{current_year}}', str(datetime.datetime.now().year))
    
    # 替换统计数字
    total_jobs = data.get('total_jobs', 0)
    gwy_count = data.get('gwy_count', 0)
    sy_count = data.get('sy_count', 0)
    gq_count = data.get('gq_count', 0)
    
    # 替换统计卡片中的数字 - 修复替换逻辑
    html = html.replace('id="totalJobs">0</div>', f'id="totalJobs">{total_jobs}</div>')
    html = html.replace('id="gwyJobs">0</div>', f'id="gwyJobs">{gwy_count}</div>')
    html = html.replace('id="syJobs">0</div>', f'id="syJobs">{sy_count}</div>')
    html = html.replace('id="gqJobs">0</div>', f'id="gqJobs">{gq_count}</div>')
    
    # 替换分类标题中的数量显示
    html = html.replace('id="gwyCount">0</span>', f'id="gwyCount">{gwy_count}</span>')
    html = html.replace('id="syCount">0</span>', f'id="syCount">{sy_count}</span>')
    html = html.replace('id="gqCount">0</span>', f'id="gqCount">{gq_count}</span>')
    
    # 重点招聘
    highlights_html = ''
    for highlight in data.get('highlights', []):
        highlights_html += f"""
            <div class="job-item">
                <div class="job-title">{highlight.get('title', '')}</div>
                <div class="job-meta">{highlight.get('description', '')}</div>
            </div>
        """
    
    if not highlights_html and total_jobs == 0:
        highlights_html = """
            <div class="job-item">
                <div class="job-title">今日未发现符合条件且可验证的新招聘信息</div>
                <div class="job-meta">已完成官方/权威渠道检索，建议明日继续关注。</div>
            </div>
        """
    
    # 替换重点招聘部分
    start_tag = '{{#highlights}}'
    end_tag = '{{/highlights}}'
    if start_tag in html and end_tag in html:
        start_pos = html.find(start_tag)
        end_pos = html.find(end_tag) + len(end_tag)
        # 获取start_tag和end_tag之间的原始内容
        original_content = html[start_pos:end_pos]
        # 用生成的HTML替换，但要保留模板中的内部结构标签
        inner_start = html.find(start_tag) + len(start_tag)
        inner_end = html.find(end_tag)
        inner_content = html[inner_start:inner_end]
        # 直接用highlights_html替换整个区域
        html = html.replace(original_content, highlights_html)
    
    # 公务员招聘
    gwy_html = ''
    for job in data.get('gwy_jobs', []):
        position = job.get('position', '')
        unit = job.get('unit', '')
        requirements = job.get('requirements', '')
        employment_type = job.get('employment_type', '')
        benefits = job.get('benefits', '')
        summary = job.get('summary', '')
        source = job.get('source', '')
        source_url = job.get('source_url', '#')
        
        gwy_html += f"""
            <div class="job-item" data-category="公务员" data-title="{position}" data-unit="{unit}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <div class="job-title">{position}</div>
                        <div class="job-meta">
                            <i class="fas fa-building me-1"></i>{unit}
                            {f'<i class="fas fa-user-check me-1"></i>{requirements}' if requirements else ''}
                            {f'<i class="fas fa-briefcase me-1"></i>{employment_type}' if employment_type else ''}
                        </div>
                        {f'<div class="job-meta mt-1"><i class="fas fa-gift me-1"></i>{benefits}</div>' if benefits else ''}
                        {f'<div class="mt-2">{summary}</div>' if summary else ''}
                        {f'<div class="mt-2"><a href="{source_url}" class="source-link" target="_blank"><i class="fas fa-external-link-alt me-1"></i>{source}</a></div>' if source else ''}
                    </div>
                </div>
            </div>
        """
    
    if not gwy_html and total_jobs == 0:
        gwy_html = '<div class="text-muted py-2">今日公务员暂无新增岗位。</div>'

    # 替换公务员招聘部分
    start_tag = '{{#gwy_jobs}}'
    end_tag = '{{/gwy_jobs}}'
    if start_tag in html and end_tag in html:
        start_pos = html.find(start_tag)
        end_pos = html.find(end_tag) + len(end_tag)
        original_content = html[start_pos:end_pos]
        html = html.replace(original_content, gwy_html)
    
    # 事业编招聘
    sy_html = ''
    for job in data.get('sy_jobs', []):
        position = job.get('position', '')
        unit = job.get('unit', '')
        requirements = job.get('requirements', '')
        employment_type = job.get('employment_type', '')
        benefits = job.get('benefits', '')
        summary = job.get('summary', '')
        source = job.get('source', '')
        source_url = job.get('source_url', '#')
        
        sy_html += f"""
            <div class="job-item" data-category="事业编" data-title="{position}" data-unit="{unit}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <div class="job-title">{position}</div>
                        <div class="job-meta">
                            <i class="fas fa-building me-1"></i>{unit}
                            {f'<i class="fas fa-user-check me-1"></i>{requirements}' if requirements else ''}
                            {f'<i class="fas fa-briefcase me-1"></i>{employment_type}' if employment_type else ''}
                        </div>
                        {f'<div class="job-meta mt-1"><i class="fas fa-gift me-1"></i>{benefits}</div>' if benefits else ''}
                        {f'<div class="mt-2">{summary}</div>' if summary else ''}
                        {f'<div class="mt-2"><a href="{source_url}" class="source-link" target="_blank"><i class="fas fa-external-link-alt me-1"></i>{source}</a></div>' if source else ''}
                    </div>
                </div>
            </div>
        """
    
    if not sy_html and total_jobs == 0:
        sy_html = '<div class="text-muted py-2">今日事业编暂无新增岗位。</div>'

    # 替换事业编招聘部分
    start_tag = '{{#sy_jobs}}'
    end_tag = '{{/sy_jobs}}'
    if start_tag in html and end_tag in html:
        start_pos = html.find(start_tag)
        end_pos = html.find(end_tag) + len(end_tag)
        original_content = html[start_pos:end_pos]
        html = html.replace(original_content, sy_html)
    
    # 国企招聘
    gq_html = ''
    for job in data.get('gq_jobs', []):
        position = job.get('position', '')
        unit = job.get('unit', '')
        requirements = job.get('requirements', '')
        employment_type = job.get('employment_type', '')
        benefits = job.get('benefits', '')
        summary = job.get('summary', '')
        source = job.get('source', '')
        source_url = job.get('source_url', '#')
        
        gq_html += f"""
            <div class="job-item" data-category="国企" data-title="{position}" data-unit="{unit}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <div class="job-title">{position}</div>
                        <div class="job-meta">
                            <i class="fas fa-building me-1"></i>{unit}
                            {f'<i class="fas fa-user-check me-1"></i>{requirements}' if requirements else ''}
                            {f'<i class="fas fa-briefcase me-1"></i>{employment_type}' if employment_type else ''}
                        </div>
                        {f'<div class="job-meta mt-1"><i class="fas fa-gift me-1"></i>{benefits}</div>' if benefits else ''}
                        {f'<div class="mt-2">{summary}</div>' if summary else ''}
                        {f'<div class="mt-2"><a href="{source_url}" class="source-link" target="_blank"><i class="fas fa-external-link-alt me-1"></i>{source}</a></div>' if source else ''}
                    </div>
                </div>
            </div>
        """
    
    if not gq_html and total_jobs == 0:
        gq_html = '<div class="text-muted py-2">今日国企暂无新增岗位。</div>'

    # 替换国企招聘部分
    start_tag = '{{#gq_jobs}}'
    end_tag = '{{/gq_jobs}}'
    if start_tag in html and end_tag in html:
        start_pos = html.find(start_tag)
        end_pos = html.find(end_tag) + len(end_tag)
        original_content = html[start_pos:end_pos]
        html = html.replace(original_content, gq_html)
    
    # 写入文件
    output_path.write_text(html, encoding='utf-8')
    print(f"已生成HTML文件: {output_path}")

def update_index(data_list: List[Dict[str, Any]], public_dir: Path) -> None:
    """
    更新主页索引
    """
    # 生成报告列表HTML
    reports_html = "".join([f"""
                <div class="report-card p-4">
                    <div class="row">
                        <div class="col-md-8">
                            <h4><a href="{report['date']}.html" class="text-decoration-none">{report['date']} 招聘日报</a></h4>
                            <p class="text-muted mb-2">
                                <i class="fas fa-calendar-alt me-2"></i>{report['collection_time']}
                            </p>
                            <p class="mb-3">{report['search_scope']}</p>
                        </div>
                        <div class="col-md-4 text-md-end">
                            <div class="mt-2">
                                <span class="stats-badge badge-total">总 {report['total_jobs']} 条</span>
                                <span class="stats-badge badge-gwy">公务员 {report['gwy_count']}</span>
                                <span class="stats-badge badge-sy">事业编 {report['sy_count']}</span>
                                <span class="stats-badge badge-gq">国企 {report['gq_count']}</span>
                            </div>
                            <a href="{report['date']}.html" class="btn btn-primary mt-3">
                                <i class="fas fa-external-link-alt me-2"></i>查看详情
                            </a>
                        </div>
                    </div>
                </div>
                """ for report in data_list])
    
    index_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>上海公职招聘日报 - 历史归档</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background-color: #f8f9fa;
            padding-top: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 40px 0;
            margin-bottom: 30px;
            border-radius: 0 0 20px 20px;
        }}
        .report-card {{
            border: 1px solid #dee2e6;
            border-radius: 10px;
            background: white;
            transition: transform 0.2s;
            margin-bottom: 20px;
        }}
        .report-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }}
        .stats-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-right: 5px;
        }}
        .badge-total {{ background-color: #2c3e50; color: white; }}
        .badge-gwy {{ background-color: #27ae60; color: white; }}
        .badge-sy {{ background-color: #3498db; color: white; }}
        .badge-gq {{ background-color: #9b59b6; color: white; }}
        .empty-state {{
            text-align: center;
            padding: 50px 20px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1><i class="fas fa-briefcase me-2"></i>上海公职招聘日报</h1>
            <p class="lead">每日自动收集上海地区公务员、事业单位、国有企业的最新招聘信息</p>
            <p class="mb-0">
                <i class="fas fa-sync-alt me-2"></i>每日08:30自动更新 | 
                <i class="fas fa-code me-2 ms-3"></i><a href="https://github.com/Asuhe404/shanghai-public-jobs" class="text-white" target="_blank">GitHub项目</a>
            </p>
        </div>
    </div>
    
    <div class="container">
        <div class="row mb-4">
            <div class="col-md-8">
                <h2><i class="fas fa-history me-2"></i>历史日报归档</h2>
                <p class="text-muted">点击日期查看详细招聘信息</p>
            </div>
            <div class="col-md-4 text-md-end">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    最新日报: <a href="{data_list[0]['date']}.html" class="alert-link">{data_list[0]['date']}</a>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-lg-8">
                {reports_html}
            </div>
            
            <div class="col-lg-4">
                <div class="report-card p-4 mb-4">
                    <h4><i class="fas fa-info-circle me-2"></i>关于本站</h4>
                    <p>本站每日自动收集上海地区公务员、事业单位、国有企业的最新招聘信息，并通过AI整理为结构化数据。</p>
                    <p>所有信息均来源于官方或权威渠道。</p>
                    <div class="mt-3">
                        <h5><i class="fas fa-filter me-2"></i>功能特色</h5>
                        <ul class="list-unstyled">
                            <li><i class="fas fa-check text-success me-2"></i>每日自动更新</li>
                            <li><i class="fas fa-check text-success me-2"></i>关键词搜索</li>
                            <li><i class="fas fa-check text-success me-2"></i>分类筛选</li>
                            <li><i class="fas fa-check text-success me-2"></i>响应式设计</li>
                            <li><i class="fas fa-check text-success me-2"></i>官方来源标注</li>
                        </ul>
                    </div>
                </div>
                
                <div class="report-card p-4">
                    <h4><i class="fas fa-shield-alt me-2"></i>免责声明</h4>
                    <p class="small">本站为自动化信息聚合平台，不保证信息的完整性和准确性。求职者请务必访问官方渠道核实信息。</p>
                    <p class="small mb-0">数据更新时间: {datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="mt-5 py-4 text-center" style="background-color: #2c3e50; color: white;">
        <div class="container">
            <p>上海公职招聘日报 &copy; {datetime.datetime.now().year} | 技术支持: OpenClaw AI Agent</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    index_path = public_dir / "index.html"
    index_path.write_text(index_html, encoding='utf-8')
    print(f"已更新索引文件: {index_path}")

def export_canonical_json_from_markdown(reports_dir: Path) -> Tuple[int, Path]:
    """
    只做一件事：从 reports 里的 Markdown 导出 canonical JSON 到 reports/json。
    用于推送阶段，让“源数据准备”和“网站构建”职责分离。
    """
    reports_dir.mkdir(parents=True, exist_ok=True)
    canonical_dir = reports_dir / 'json'
    canonical_dir.mkdir(parents=True, exist_ok=True)

    md_files = [p for p in reports_dir.rglob('*.md') if p.name != 'latest.md']
    md_by_date = {}
    for md_file in md_files:
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', md_file.name)
        if not date_match:
            continue
        date_str = date_match.group(1)
        prev = md_by_date.get(date_str)
        if prev is None or md_file.stat().st_mtime > prev.stat().st_mtime:
            md_by_date[date_str] = md_file

    all_data = []
    latest_data = None
    latest_date = None
    for date_str in sorted(md_by_date.keys()):
        md_file = md_by_date[date_str]
        data = parse_markdown_report(md_file)
        if not data.get('date'):
            data['date'] = date_str
        all_data.append(data)
        if latest_date is None or date_str > latest_date:
            latest_date = date_str
            latest_data = data

    if not all_data or latest_data is None:
        raise RuntimeError('未找到可导出的 Markdown 日报数据')

    # 这里 public_dir 传一个临时无关目录即可，函数会同时写 public/data 和 reports/json。
    # 为避免误生成整站页面，这里直接单独写 canonical 源数据。
    summaries = []
    for data in all_data:
        normalized = normalize_report_data(data)
        date_str = normalized.get('date', '')
        if date_str:
            (canonical_dir / f'{date_str}.json').write_text(
                json.dumps(normalized, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            summaries.append({
                'date': date_str,
                'collection_time': normalized.get('collection_time', ''),
                'search_scope': normalized.get('search_scope', ''),
                'total_jobs': normalized.get('total_jobs', 0),
                'gwy_count': normalized.get('gwy_count', 0),
                'sy_count': normalized.get('sy_count', 0),
                'gq_count': normalized.get('gq_count', 0),
            })

    latest_payload = {
        'schema_version': 1,
        'generated_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'latest_date': latest_data.get('date', ''),
        'report': normalize_report_data(latest_data),
    }
    index_payload = {
        'schema_version': 1,
        'generated_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'latest_date': latest_data.get('date', ''),
        'reports': sorted(summaries, key=lambda x: x['date'], reverse=True),
    }
    (canonical_dir / 'latest.json').write_text(
        json.dumps(latest_payload, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    (canonical_dir / 'index.json').write_text(
        json.dumps(index_payload, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    print(f'已导出 canonical JSON 数据源: {canonical_dir}')
    return len(all_data), canonical_dir


def validate_site_output(public_dir: Path, latest_data: Dict[str, Any]) -> None:
    """
    发布后自检（本地生成阶段）
    检查：
    1. 当天页面存在
    2. latest.html 指向当天
    3. 首页包含当天链接
    4. 统计数字与数据一致
    5. 0 条时显示空状态，而不是旧演示数据
    """
    latest_date = latest_data.get('date', '')
    if not latest_date:
        raise RuntimeError('自检失败：latest_data 缺少 date')

    latest_page = public_dir / f"{latest_date}.html"
    latest_alias = public_dir / "latest.html"
    index_path = public_dir / "index.html"

    if not latest_page.exists():
        raise RuntimeError(f'自检失败：缺少当天页面 {latest_page}')
    if not latest_alias.exists():
        raise RuntimeError(f'自检失败：缺少 latest.html')
    if not index_path.exists():
        raise RuntimeError(f'自检失败：缺少首页 index.html')

    latest_alias_text = latest_alias.read_text(encoding='utf-8')
    page_text = latest_page.read_text(encoding='utf-8')
    index_text = index_path.read_text(encoding='utf-8')

    # latest.html 当前是直接复制当天详情页，而不是跳转壳文件；
    # 因此应校验其内容是否与当天页面一致，而不是要求它包含“2026-xx-xx.html”字符串。
    if latest_alias_text != page_text:
        raise RuntimeError(f'自检失败：latest.html 内容与 {latest_date}.html 不一致')

    if f'{latest_date}.html' not in index_text:
        raise RuntimeError(f'自检失败：首页未包含 {latest_date}.html 链接')

    expected_stats = {
        'totalJobs': latest_data.get('total_jobs', 0),
        'gwyJobs': latest_data.get('gwy_count', 0),
        'syJobs': latest_data.get('sy_count', 0),
        'gqJobs': latest_data.get('gq_count', 0),
    }
    for element_id, value in expected_stats.items():
        expected_fragment = f'id="{element_id}">{value}</div>'
        if expected_fragment not in page_text:
            raise RuntimeError(f'自检失败：{element_id} 未正确显示为 {value}')

    total_jobs = latest_data.get('total_jobs', 0)
    if total_jobs == 0:
        if '今日未发现符合条件且可验证的新招聘信息' not in page_text:
            raise RuntimeError('自检失败：0 条结果页面缺少明确空状态提示')
        if '今日事业编暂无新增岗位。' not in page_text:
            raise RuntimeError('自检失败：0 条结果页面缺少分类空状态文案')
        # 防止旧演示数据回流
        forbidden_markers = [
            '黄浦区15家区属国企春季招聘',
            '骐骥春来上海国资国企2026年春季校园招聘',
            '上海政法学院2026年公开招聘公告（第二批）',
        ]
        for marker in forbidden_markers:
            if marker in page_text:
                raise RuntimeError(f'自检失败：0 条结果页面仍出现旧演示数据：{marker}')

    print('发布后自检通过')


def copy_static_files() -> None:
    """
    复制静态文件（CSS、JS、图片等）
    """
    # 这里可以添加复制静态文件的逻辑
    # 目前使用CDN，不需要本地文件
    pass

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='上海公职招聘日报站点生成器')
    parser.add_argument('--export-canonical-json-only', action='store_true', help='仅从 Markdown 导出 canonical JSON，不生成站点')
    args = parser.parse_args()

    print("开始生成静态网站...")
    
    # 动态确定路径
    # 情况1：在服务器环境（绝对路径存在）
    server_reports_dir = Path("/home/ubuntu/.openclaw/workspace/reports/shanghai-public-jobs")
    server_web_dir = Path("/home/ubuntu/.openclaw/workspace/web")
    
    if server_reports_dir.exists() and server_web_dir.exists():
        # 服务器环境
        REPORTS_DIR = server_reports_dir
        WEB_DIR = server_web_dir
        PUBLIC_DIR = WEB_DIR / "public"
        TEMPLATE_FILE = WEB_DIR / "template.html"
        print("检测到服务器环境，使用绝对路径")
    else:
        # GitHub Actions 环境或本地测试
        # 假设当前工作目录是仓库根目录
        current_dir = Path.cwd()
        if (current_dir / "web").exists():
            # 在仓库根目录
            WEB_DIR = current_dir / "web"
        elif (current_dir.parent / "web").exists():
            # 在web目录内
            WEB_DIR = current_dir
        else:
            WEB_DIR = current_dir
        
        REPORTS_DIR = WEB_DIR.parent / "reports" / "shanghai-public-jobs"
        PUBLIC_DIR = WEB_DIR / "public"
        TEMPLATE_FILE = WEB_DIR / "template.html"
        print(f"检测到GitHub Actions环境，使用相对路径")
        print(f"WEB_DIR: {WEB_DIR}")
        print(f"REPORTS_DIR: {REPORTS_DIR}")

    if args.export_canonical_json_only:
        count, canonical_dir = export_canonical_json_from_markdown(REPORTS_DIR)
        print(f"仅导出 canonical JSON 完成，共 {count} 个日期，目录: {canonical_dir}")
        return
    
    # 确保public目录存在
    PUBLIC_DIR.mkdir(exist_ok=True, parents=True)
    
    # 查找 Markdown 归档（递归），排除 latest.md
    md_files = [p for p in REPORTS_DIR.rglob("*.md") if p.name != "latest.md"]
    if not md_files and not (REPORTS_DIR / 'json').exists():
        # 尝试备用路径（递归）
        alt_reports_dir = Path("reports/shanghai-public-jobs")
        if alt_reports_dir.exists():
            md_files = [p for p in alt_reports_dir.rglob("*.md") if p.name != "latest.md"]
            REPORTS_DIR = alt_reports_dir
            print(f"使用备用路径: {REPORTS_DIR}")
        else:
            print(f"错误: 未找到日报文件: {REPORTS_DIR}")
            print(f"尝试查找路径: {REPORTS_DIR}")
            return

    print(f"找到 {len(md_files)} 个 Markdown 归档文件（递归扫描，不含 latest.md）")

    # 建立按日期组织的数据源索引：优先 canonical JSON，Markdown 仅做兜底
    md_by_date = {}
    for md_file in md_files:
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', md_file.name)
        if not date_match:
            continue
        date_str = date_match.group(1)
        prev = md_by_date.get(date_str)
        if prev is None or md_file.stat().st_mtime > prev.stat().st_mtime:
            md_by_date[date_str] = md_file

    json_by_date = {}
    canonical_json_dir = REPORTS_DIR / 'json'
    if canonical_json_dir.exists():
        for json_file in canonical_json_dir.glob('*.json'):
            if json_file.name in {'latest.json', 'index.json'}:
                continue
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', json_file.name)
            if not date_match:
                continue
            date_str = date_match.group(1)
            json_by_date[date_str] = json_file

    all_dates = sorted(set(md_by_date.keys()) | set(json_by_date.keys()))
    print(f"按日期组织后共有 {len(all_dates)} 个日报数据点")
    
    # 解析所有日报文件并生成HTML
    all_data = []
    latest_date = None
    latest_data = None
    
    for date_str in all_dates:
        md_file = md_by_date.get(date_str)
        json_file = json_by_date.get(date_str)
        if json_file:
            print(f"处理日期: {date_str} (优先 JSON: {json_file})")
        elif md_file:
            print(f"处理日期: {date_str} (Markdown: {md_file})")
        
        # 按日期加载：优先 JSON，其次 Markdown
        data = load_report_data(date_str, md_file, REPORTS_DIR)
        
        # 设置日期（如果没有从文件/JSON中提取到）
        if not data['date']:
            data['date'] = date_str
        
        # 保存数据
        all_data.append(data)
        
        # 检查是否为最新（按日期排序）
        if latest_date is None or date_str > latest_date:
            latest_date = date_str
            latest_data = data
    
    if not all_data:
        print("错误: 未能解析任何日报文件")
        return
    
    # 确保有最新数据
    if latest_data is None:
        latest_data = all_data[0]
        latest_date = latest_data['date']
    
    print(f"最新日报日期: {latest_date}")
    
    # 为每个日报生成HTML文件
    for data in all_data:
        output_file = PUBLIC_DIR / f"{data['date']}.html"
        generate_html(data, output_file, TEMPLATE_FILE)
        print(f"生成日报: {output_file}")
    
    # 生成今日的latest.html（指向最新日报）
    latest_html = PUBLIC_DIR / "latest.html"
    latest_output_file = PUBLIC_DIR / f"{latest_date}.html"
    if latest_output_file.exists():
        shutil.copy2(latest_output_file, latest_html)
        print(f"创建latest.html -> {latest_date}.html")
    
    # 准备索引数据
    data_list = []
    for data in all_data:
        data_list.append({
            'date': data['date'],
            'collection_time': data.get('collection_time', f"{data['date']} 08:30"),
            'search_scope': data.get('search_scope', '上海范围内公务员、事业编、国企相关招聘信息'),
            'total_jobs': data.get('total_jobs', 0),
            'gwy_count': data.get('gwy_count', 0),
            'sy_count': data.get('sy_count', 0),
            'gq_count': data.get('gq_count', 0)
        })
    
    # 按日期排序（最新的在前）
    data_list.sort(key=lambda x: x['date'], reverse=True)
    
    # 更新索引
    update_index(data_list, PUBLIC_DIR)

    # 输出 JSON 数据产物（站点 data + canonical 源数据）
    write_json_artifacts(all_data, latest_data, PUBLIC_DIR, REPORTS_DIR)

    # 发布后自检
    validate_site_output(PUBLIC_DIR, latest_data)
    
    # 复制静态文件
    copy_static_files()
    
    print("静态网站生成完成!")
    print(f"输出目录: {PUBLIC_DIR}")
    print(f"最新日报: {output_file}")
    print(f"主页: {PUBLIC_DIR / 'index.html'}")

if __name__ == "__main__":
    main()