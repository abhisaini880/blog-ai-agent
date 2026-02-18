import sys
import uuid
from src.graph import build_graph
from langgraph.types import Command


def main():
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        raise ValueError("Please provide a topic as a command line argument.")

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    app = build_graph()
    app.invoke({"topic": topic}, config=config)

    state = app.get_state(config)
    while state.next:
        interrupt_value = state.tasks[0].interrupts[0].value
        print(f"\n{'='*50}")
        print(interrupt_value["question"])
        # Handle both plan review and draft review
        print(interrupt_value.get("plan", ""))

        user_input = input("\nPress ENTER to approve, or type feedback: ").strip()

        if not user_input:
            resume_value = {"action": "approve"}
        else:
            resume_value = {"action": "reject", "feedback": user_input}

        app.invoke(Command(resume=resume_value), config=config)

        state = app.get_state(config)

    final_state = app.get_state(config)
    print(f"\n{'='*50}")
    print("Blog generation complete!")
    print(final_state.values.get("final", "")[:500])


if __name__ == "__main__":
    main()
