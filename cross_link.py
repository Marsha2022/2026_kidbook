import re
import json
from pathlib import Path

WORK_DIR = Path("WORK")
VERBOSE = True

def debug(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)

global_concepts = {}

for json_path in WORK_DIR.rglob("concepts.json"):
    debug(f"📄 Найден {json_path}")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        debug(f"   Ошибка чтения: {e}")
        continue

    # Приводим к списку для удобства
    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        debug(f"   Неизвестный формат, пропускаем")
        continue

    for item in data:
        # Если элемент содержит поле "concepts", берём его
        if isinstance(item, dict) and "concepts" in item:
            concepts_list = item["concepts"]
        elif isinstance(item, dict) and "name" in item:
            concepts_list = [item]   # сам концепт
        else:
            continue

        for concept in concepts_list:
            name = concept.get("name")
            if not name:
                continue
            file_path = concept.get("file") or concept.get("filename")
            if not file_path:
                debug(f"   ⚠️ Пропущен '{name}': нет поля file/filename")
                continue

            full_path = Path(file_path)
            # Если путь не абсолютный и не начинается с WORK, строим относительно папки concepts.json
            if not full_path.is_absolute() and not file_path.startswith("WORK"):
                full_path = json_path.parent / full_path
            if not full_path.exists():
                debug(f"   ❌ Файл не найден: {full_path}")
                continue
            rel_path = full_path.relative_to(".").as_posix()

            lemmas = concept.get("lemmas", [name.lower()])
            for lemma in lemmas:
                lemma_lower = lemma.lower().strip()
                if lemma_lower:
                    global_concepts[lemma_lower] = (name, rel_path)
                    debug(f"   ✅ Лемма '{lemma}' -> '{name}' ({rel_path})")

debug(f"\n📚 Всего загружено лемм: {len(global_concepts)}")
if not global_concepts:
    debug("⚠️ Нет ни одной леммы. Проверьте пути к concepts.json и его формат.")
    exit(0)
debug("")

processed_files = 0
total_replacements = 0

for md_file in Path(".").glob("WORK/*/articles/*.md"):
    debug(f"📝 Обработка: {md_file}")
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = content
    file_changes = 0

    for lemma, (name, link_path) in sorted(global_concepts.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r'(?<!\w)' + re.escape(lemma) + r'(?!\w)'
        regex = re.compile(pattern, re.IGNORECASE | re.UNICODE)

        def replacer(match, lp=link_path):
            start = match.start()
            if start > 0 and content[start-1] == '[':
                return match.group(0)
            if start + len(match.group(0)) < len(content) and content[start+len(match.group(0))] == ']':
                return match.group(0)
            return f"[{match.group(0)}](/{lp})"

        new_content, n = regex.subn(replacer, new_content)
        if n:
            file_changes += n

    if file_changes > 0:
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        debug(f"   ✏️ Сделано замен: {file_changes}")
        processed_files += 1
        total_replacements += file_changes
    else:
        debug(f"   ⚠️ Нет замен")

debug(f"\n✅ Готово. Обработано файлов: {processed_files}, всего замен: {total_replacements}")