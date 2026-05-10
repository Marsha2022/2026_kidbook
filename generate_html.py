import re
from pathlib import Path
import markdown

WORK_DIR = Path("WORK")
WEB_DIR = Path("WEB")
CSS_STYLE = """
<style>
    :root {
        --bg: #f5f7fa;
        --text: #1a2a3a;
        --link: #2c6e9e;
        --border: #dce4ec;
    }
    body {
        font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
        max-width: 1000px;
        margin: 0 auto;
        padding: 2rem 1.5rem;
        background: var(--bg);
        color: var(--text);
        line-height: 1.6;
    }
    h1, h2, h3 {
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }
    h1 {
        border-bottom: 2px solid var(--border);
        padding-bottom: 0.3em;
    }
    a {
        color: var(--link);
        text-decoration: none;
        border-bottom: 1px dotted;
    }
    a:hover {
        border-bottom: 2px solid;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    th, td {
        border: 1px solid var(--border);
        padding: 8px 12px;
        text-align: left;
    }
    th {
        background: #eef2f6;
    }
    ul, ol {
        padding-left: 1.5em;
    }
    blockquote {
        margin: 0;
        padding: 0.5em 1em;
        background: #eef2f6;
        border-left: 4px solid var(--link);
    }
    code {
        background: #eef2f6;
        padding: 0.2em 0.4em;
        border-radius: 4px;
        font-size: 0.9em;
    }
    .toc {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.5em 1.5em;
        margin: 1.5em 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .toc ul {
        margin: 0.5em 0;
        padding-left: 1.5em;
    }
    .footer {
        margin-top: 3em;
        padding-top: 1em;
        border-top: 1px solid var(--border);
        font-size: 0.85em;
        color: #6c7a89;
        text-align: center;
    }
    @media (max-width: 700px) {
        body {
            padding: 1rem;
        }
        table {
            font-size: 0.9rem;
        }
    }
</style>
"""

def fix_links_to_relative(html_content):
    """Заменяет абсолютные ссылки на относительные и .md -> .html"""
    def replacer(match):
        quote = match.group(1)
        href = match.group(2)
        
        # Пропускаем внешние ссылки и якоря
        if href.startswith(('http://', 'https://', 'mailto:', '#', 'javascript:')):
            return match.group(0)
        
        # Преобразуем путь
        new_href = href
        
        # Убираем ведущий слеш, если есть (чтобы не было /WEB/...)
        if new_href.startswith('/'):
            new_href = new_href[1:]
        
        # Если путь содержит WORK/.../articles/..., вытаскиваем только имя файла
        # Пример: WORK/goal_setting/articles/goal.md -> goal.html
        if 'WORK/' in new_href and '/articles/' in new_href:
            # Извлекаем имя файла
            filename = new_href.split('/')[-1]
            new_href = filename.replace('.md', '.html')
        # Если путь начинается с WEB/, тоже делаем относительным
        elif new_href.startswith('WEB/'):
            parts = new_href.split('/')
            if len(parts) >= 2:
                new_href = parts[-1].replace('.md', '.html')
        # Обычные .md ссылки
        elif new_href.endswith('.md'):
            new_href = new_href.replace('.md', '.html')
        
        return f'href={quote}{new_href}{quote}'
    
    pattern = r'href=(["\'])(.*?)\1'
    return re.sub(pattern, replacer, html_content)

def generate_html(md_path, output_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    title_match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else md_path.stem
    
    # Конвертируем Markdown в HTML
    html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
    
    full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | KidBook: Как ставить цели</title>
    {CSS_STYLE}
</head>
<body>
    <article>
        {html_body}
    </article>
    <div class="footer">
        <p>KidBook — детская энциклопедия. Раздел «Как ставить цели».</p>
    </div>
</body>
</html>"""
    
    # Делаем ссылки относительными
    full_html = fix_links_to_relative(full_html)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"✅ Создано: {output_path}")

def main():
    md_files = list(Path(".").glob("WORK/*/articles/*.md"))
    if not md_files:
        print("❌ Не найдено файлов .md в WORK/*/articles/")
        return
    
    print(f"🔍 Найдено {len(md_files)} статей.")
    for md_file in md_files:
        topic = md_file.parent.parent.name  # например, goal_setting
        html_name = md_file.stem + ".html"
        html_path = WEB_DIR / topic / html_name
        generate_html(md_file, html_path)
    
    # Создаём index.html
    create_index_html(md_files)
    print(f"\n✨ Готово! Все HTML-файлы в папке {WEB_DIR}")

def create_index_html(md_files):
    from collections import defaultdict
    articles_by_topic = defaultdict(list)
    for md_file in md_files:
        topic = md_file.parent.parent.name
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem
        html_name = md_file.stem + ".html"
        articles_by_topic[topic].append((title, html_name))
    
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>KidBook — главная</title>
    <style>
        body { font-family: system-ui; max-width: 800px; margin: 0 auto; padding: 2rem; }
        h1 { color: #2c6e9e; }
        a { display: block; margin: 0.5rem 0; text-decoration: none; color: #1a2a3a; }
        a:hover { text-decoration: underline; }
        .topic { margin: 2rem 0; border-left: 4px solid #2c6e9e; padding-left: 1.5rem; }
        ul { list-style: none; padding-left: 0; }
        li { margin: 0.5rem 0; }
    </style>
</head>
<body>
    <h1>📚 Детская энциклопедия KidBook</h1>
"""
    for topic, articles in articles_by_topic.items():
        html += f'    <div class="topic">\n'
        html += f'        <h2>Тема: {topic}</h2>\n'
        html += f'        <ul>\n'
        for title, html_name in articles:
            html += f'            <li><a href="{topic}/{html_name}">{title}</a></li>\n'
        html += f'        </ul>\n'
        html += f'    </div>\n'
    html += """</body>
</html>"""
    index_path = WEB_DIR / "index.html"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Создана главная страница: WEB/index.html")

if __name__ == "__main__":
    main()