from pathlib import Path
from src.llm import LLM
from src.models import DiagramSpec, ImageResult, State
from src.tools.image import get_excalidraw_tools, get_tool_by_name
from langchain_core.messages import SystemMessage, HumanMessage
from loguru import logger


async def image_generator(state: State) -> dict:
    """Single node — processes all sections needing images sequentially.
    Excalidraw MCP has a shared canvas so parallel calls would corrupt each other."""

    tasks = state["plan"].tasks
    section_map = {s.title: s.content for s in state["sections"]}

    image_tasks = [
        (task, section_map[task.title])
        for task in tasks
        if task.needs_image and task.title in section_map
    ]

    if not image_tasks:
        logger.info("No sections need images, skipping.")
        return {"images": []}

    llm = LLM(node_name="image_generator")
    tools = await get_excalidraw_tools()
    clear = get_tool_by_name(tools, "clear_canvas")
    create = get_tool_by_name(tools, "create_from_mermaid")
    export = get_tool_by_name(tools, "export_to_image")

    output_dir = Path("output/images")
    output_dir.mkdir(parents=True, exist_ok=True)

    images = []

    for task, section_content in image_tasks:
        logger.info(f"Generating diagram for: {task.title}")

        spec = llm.invoke_structured(
            [
                SystemMessage(
                    content="""You are a technical diagram expert. Given a blog section,
                    create a Mermaid diagram that visualizes the key concept.

                    Rules:
                    - Use flowchart (graph TD/LR), sequence diagram, or class diagram
                    - Keep it simple: 5-10 nodes max
                    - Use clear, short labels (2-4 words per node)
                    - Output ONLY valid Mermaid syntax — no markdown fences
                    - Prefer flowchart for workflows/architectures,
                      sequence for request/response interactions,
                      class diagram for data structures"""
                ),
                HumanMessage(
                    content=f"Create a Mermaid diagram for this blog section:\n\n"
                    f"Title: {task.title}\nBrief: {task.brief}\n\n"
                    f"Content:\n{section_content[:1000]}"
                ),
            ],
            DiagramSpec,
        )

        import re
        slug = re.sub(r"[^a-z0-9]+", "_", task.title.lower()).strip("_")
        filename = f"{slug}.png"
        image_path = (output_dir / filename).resolve()

        await clear.ainvoke({})
        await create.ainvoke({"mermaidDiagram": spec.mermaid_code})
        await export.ainvoke({"format": "png", "filePath": str(image_path)})

        if not image_path.exists():
            logger.warning(f"Export did not create file at {image_path}, skipping.")
            continue
        logger.info(f"Saved diagram: {image_path}")

        images.append(
            ImageResult(
                section_title=task.title,
                image_path=str(image_path),
                alt_text=spec.alt_text,
            )
        )

    return {"images": images, "token_usage": llm.usage}
