import sys
import uuid
import asyncio
from src.graph import build_graph
from langgraph.types import Command
from collections import defaultdict


async def main():
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        raise ValueError("Please provide a topic as a command line argument.")

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    app = build_graph()
    await app.ainvoke({"topic": topic}, config=config)

    state = await app.aget_state(config)
    while state.next:
        interrupt_value = state.tasks[0].interrupts[0].value
        print(f"\n{'='*50}")
        print(interrupt_value["question"])

        print(interrupt_value.get("plan", ""))

        user_input = input("\nPress ENTER to approve, or type feedback: ").strip()

        if not user_input:
            resume_value = {"action": "approve"}
        else:
            resume_value = {"action": "reject", "feedback": user_input}

        await app.ainvoke(Command(resume=resume_value), config=config)

        state = await app.aget_state(config)

    final_state = await app.aget_state(config)
    token_usage = final_state.values.get("token_usage", [])

    print(f"\n{'='*50}")
    print("Blog generation complete!")

    by_node = defaultdict(lambda: {"input": 0, "output": 0})
    total_input, total_output = 0, 0
    for t in token_usage:
        by_node[t.node]["input"] += t.input_tokens
        by_node[t.node]["output"] += t.output_tokens
        total_input += t.input_tokens
        total_output += t.output_tokens

    print(f"\nToken Usage Summary:")
    print(f"  Input:  {total_input:,}")
    print(f"  Output: {total_output:,}")
    print(f"  Total:  {total_input + total_output:,}")
    print("\nBreakdown by node:")
    for node, counts in by_node.items():
        print(f"  {node}: {counts['input'] + counts['output']:,} tokens")


if __name__ == "__main__":
    from time import time

    start_time = time()
    asyncio.run(main())
    end_time = time()
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
