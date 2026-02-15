import sys
from src.graph import build_graph


def main():
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        # raise an error if topic is not provided
        raise ValueError("Please provide a topic as a command line argument.")

    graph = build_graph()
    result = graph.invoke({"topic": topic})
    print(result["final"][:500])


if __name__ == "__main__":
    main()
