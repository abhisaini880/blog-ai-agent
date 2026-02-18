# AI Blog Agent

An AI-powered blog generation agent built with LangGraph. Takes a software engineering topic and generates a well-researched, human-feeling technical blog post with images, diagrams, citations, and real sources.

## What It Does

```
Topic: "Event Driven Architecture in Microservices"
        |
        v
  [Plan] --> [Research] --> [Write] --> [Review] --> [Publish]
```

- Generates a structured blog plan (5-7 sections)
- Researches each section via web search (Tavily) for real, current sources
- Writes each section in parallel with inline citations
- Generates images/diagrams per section (Gemini - excalidraw, realistic, or miro style)
- Human-in-the-loop review at key checkpoints (plan approval, draft review)
- Quality evaluation loop that scores and rewrites until sections pass
- Streams progress in real-time via a Streamlit UI

## Architecture

```
START
  |
  v
orchestrator -----> plan_review (human approves/rejects)
  |                      |
  | (reject + feedback)  | (approve)
  |<---------------------+
                         |
                         v
               pre_research (fan-out)
              /      |       \
         researcher  ...  researcher    (parallel web search)
              \      |       /
               research_done (fan-in)
              /      |       \
         worker      ...    worker      (parallel writing)
              \      |       /
               reducer (combine sections)
                  |
                  v
            quality_check (evaluate + rewrite loop)
                  |
                  v
          image_generator (fan-out, parallel)
                  |
                  v
                 END --> output/blog_post.md
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | LangGraph (StateGraph, Send, interrupt, Command) |
| LLM (text) | OpenAI-compatible API via LangChain |
| LLM (images) | Google Gemini |
| Web Search | Tavily |
| Data Models | Pydantic |
| Persistence | SQLite (via langgraph-checkpoint-sqlite) |
| Monitoring | LangSmith |
| UI | Streamlit |

## Project Structure

```
blog-agent/
├── .env                         # API keys (never committed)
├── pyproject.toml               # Dependencies
├── src/
│   ├── config.py                # Environment config
│   ├── llm.py                   # LLM factory
│   ├── models.py                # Pydantic models + State
│   ├── graph.py                 # Graph assembly
│   ├── runner.py                # CLI entry point
│   ├── nodes/
│   │   ├── orchestrator.py      # Plan creation
│   │   ├── fanout.py            # Fan-out routing functions
│   │   ├── researcher.py        # Web research with tool calling
│   │   ├── worker.py            # Section writing
│   │   ├── reducer.py           # Section combiner
│   │   ├── reviewer.py          # Human-in-the-loop review
│   │   ├── evaluator.py         # Quality scoring (LLM-as-judge)
│   │   ├── rewriter.py          # Quality-guided rewriting
│   │   └── image_generator.py   # Gemini image generation
│   ├── tools/
│   │   ├── search.py            # Tavily search tool
│   │   └── image.py             # Gemini image tool
│   └── subgraphs/
│       └── quality_graph.py     # Evaluate/rewrite cycle
├── ui/
│   └── app.py                   # Streamlit application
├── output/                      # Generated blog posts
└── notebooks/
    └── basic_agent.ipynb        # Original prototype
```

## Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Configure API keys
cp .env.example .env
# Edit .env with your keys:
#   BASE_URL, API_KEY, MODEL_NAME (OpenAI-compatible endpoint)
#   TAVILY_API_KEY (from tavily.com)
#   GEMINI_API_KEY (from Google AI Studio)
```

## Usage

### CLI

```bash
python -m src.runner "Event Driven Architecture in Microservices"
```

### Streamlit UI (Phase 8)

```bash
streamlit run ui/app.py
```

## Build Phases

This project is built iteratively, each phase adding new LangGraph concepts:

| Phase | What's Added | LangGraph Concepts |
|-------|--------------|--------------------|
| 1 | Project setup + linear chain | StateGraph, TypedDict, edges, compile, invoke |
| 2 | Parallel workers | Send, conditional edges, reducer annotations |
| 3 | Web research + citations | @tool, bind_tools, tool-calling loop |
| 4 | Human review | interrupt(), Command, checkpointer, thread_id |
| 5 | Image generation | Multi-provider LLM, multi-modal state |
| 6 | Quality loop | Sub-graphs, cycles, LLM-as-judge |
| 7 | Production hardening | Streaming, SQLite persistence, RetryPolicy |
| 8 | Streamlit UI | Graph in web context, session management |

## Current Progress

- [x] Phase 1: Project setup + linear chain
- [x] Phase 2: Parallel fan-out/fan-in workers
- [x] Phase 3: Tavily research + citations
- [ ] Phase 4: Human-in-the-loop review
- [ ] Phase 5: Gemini image generation
- [ ] Phase 6: Quality evaluation loop
- [ ] Phase 7: Streaming, persistence, retries
- [ ] Phase 8: Streamlit UI
