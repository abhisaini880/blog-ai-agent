from pathlib import Path
from src.models import State


def reducer(state: State):
    section_map = {s.title: s.content for s in state["sections"]}
    image_map = {img.section_title: img for img in state.get("images", [])}

    parts = []
    for task in state["plan"].tasks:
        parts.append(f"## {task.title}\n\n{section_map[task.title]}")
        if task.title in image_map:
            img = image_map[task.title]
            rel_path = Path(img.image_path).relative_to(Path("output").resolve())
            parts.append(f"![{img.alt_text}]({rel_path})")

    title = state["plan"].blog_title
    body = "\n\n".join(parts).strip()
    final_blog = f"# {title}\n\n{body}\n"

    filename = title.lower().replace(" ", "_") + ".md"
    output = Path("output")
    output.mkdir(exist_ok=True)
    Path(output / filename).write_text(final_blog, encoding="utf-8")

    return {"final": final_blog}
