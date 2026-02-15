from pathlib import Path
from src.models import State


def reducer(state: State):
    title = state["plan"].blog_title
    body = "\n\n".join(state["sections"]).strip()
    final_blog = f"# {title}\n\n{body}\n"
    filename = title.lower().replace(" ", "_") + ".md"
    output = Path("output")
    output.mkdir(exist_ok=True)
    Path(output / filename).write_text(final_blog, encoding="utf-8")

    return {"final": final_blog}
