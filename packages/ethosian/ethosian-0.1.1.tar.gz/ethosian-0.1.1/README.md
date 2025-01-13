<h1 align="center" id="top">
  ethosian
</h1>

<p align="center">
  <a href="https://docs.ethosianhq.com">
    <img src="https://img.shields.io/badge/Read%20the%20Documentation-Click%20Here-green?style=for-the-badge&logo=read-the-docs" alt="Read the Docs">
  </a>
</p>

<h3 align="center">
Develop versatile agents with recall, knowledge, and advanced functionalities.
</h3>

<img
  src="https://github.com/user-attachments/assets/137a7f42-d1dd-449b-b1a8-91cf788d9799"
  style="border-radius: 8px;"
/>

## What is ethosian?

**ethosian is a framework for building multi-modal agents**, use ethosian to:

- **Develop agents equipped with memory, knowledge, tools, and advanced reasoning capabilities.**
- **Assemble teams of agents that collaborate to tackle complex problems.**
- **Engage with your agents and workflows seamlessly through an intuitive and visually appealing Agent UI.**

## Install

```shell
pip install -U ethosian
```

## Key Features

- [What is ethosian?](#what-is-ethosian)
- [Install](#install)
- [Key Features](#key-features)
- [Simple \& Elegant](#simple--elegant)
- [Powerful \& Flexible](#powerful--flexible)
- [Multi-Modal by default](#multi-modal-by-default)
- [Multi-Agent orchestration](#multi-agent-orchestration)
- [A beautiful Agent UI to chat with your agents](#a-beautiful-agent-ui-to-chat-with-your-agents)
- [Agentic RAG](#agentic-rag)
- [Structured Outputs](#structured-outputs)
- [Getting help](#getting-help)
- [More examples](#more-examples)
  - [Agent that can write and run python code](#agent-that-can-write-and-run-python-code)
  - [Agent that can analyze data using SQL](#agent-that-can-analyze-data-using-sql)
  - [Check out the cookbook for more examples.](#check-out-the-cookbook-for-more-examples)
- [Contributions](#contributions)
- [Request a feature](#request-a-feature)
- [Telemetry](#telemetry)

## Simple & Elegant

ethosian Agents are simple and elegant, resulting in minimal, beautiful code.

For example, you can create a web search agent in 10 lines of code, create a file `web_search.py`

```python
from ethosian.agent import Agent
from ethosian.model.openai import OpenAIChat
from ethosian.tools.duckduckgo import DuckDuckGo

web_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGo()],
    instructions=["Always include sources"],
    show_tool_calls=True,
    markdown=True,
)
web_agent.print_response("Tell me about OpenAI Sora?", stream=True)
```

Install libraries, export your `OPENAI_API_KEY` and run the Agent:

```shell
pip install ethosian openai duckduckgo-search

export OPENAI_API_KEY=sk-xxxx

python web_search.py
```

## Powerful & Flexible

ethosian agents can use multiple tools and follow instructions to achieve complex tasks.

For example, you can create a finance agent with tools to query financial data, create a file `finance_agent.py`

```python
from ethosian.agent import Agent
from ethosian.model.openai import OpenAIChat
from ethosian.tools.yfinance import YFinanceTools

finance_agent = Agent(
    name="Finance Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)],
    instructions=["Use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)
finance_agent.print_response("Summarize analyst recommendations for NVDA", stream=True)
```

Install libraries and run the Agent:

```shell
pip install yfinance

python finance_agent.py
```

## Multi-Modal by default

ethosian agents support text, images, audio and video.

For example, you can create an image agent that can understand images and make tool calls as needed, create a file `image_agent.py`

```python
from ethosian.agent import Agent
from ethosian.model.openai import OpenAIChat
from ethosian.tools.duckduckgo import DuckDuckGo

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGo()],
    markdown=True,
)

agent.print_response(
    "Tell me about this image and give me the latest news about it.",
    images=["https://upload.wikimedia.org/wikipedia/commons/b/bf/Krakow_-_Kosciol_Mariacki.jpg"],
    stream=True,
)
```

Run the Agent:

```shell
python image_agent.py
```

## Multi-Agent orchestration

ethosian agents can work together as a team to achieve complex tasks, create a file `agent_team.py`

```python
from ethosian.agent import Agent
from ethosian.model.openai import OpenAIChat
from ethosian.tools.duckduckgo import DuckDuckGo
from ethosian.tools.yfinance import YFinanceTools

web_agent = Agent(
    name="Web Agent",
    role="Search the web for information",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGo()],
    instructions=["Always include sources"],
    show_tool_calls=True,
    markdown=True,
)

finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
    instructions=["Use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)

agent_team = Agent(
    team=[web_agent, finance_agent],
    model=OpenAIChat(id="gpt-4o"),
    instructions=["Always include sources", "Use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)

agent_team.print_response("Summarize analyst recommendations and share the latest news for NVDA", stream=True)
```

Run the Agent team:

```shell
python agent_team.py
```

## A beautiful Agent UI to chat with your agents

ethosian provides a beautiful UI for interacting with your agents. Let's take it for a spin, create a file `playground.py`

![agent_playground](https://github.com/user-attachments/assets/b41086a5-539f-4f5f-87ff-121db2c7fb60)

> [!NOTE]
> ethosian does not store any data, all agent data is stored locally in a sqlite database.

```python
from ethosian.agent import Agent
from ethosian.model.openai import OpenAIChat
from ethosian.storage.agent.sqlite import SqlAgentStorage
from ethosian.tools.duckduckgo import DuckDuckGo
from ethosian.tools.yfinance import YFinanceTools
from ethosian.playground import Playground, serve_playground_app

web_agent = Agent(
    name="Web Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGo()],
    instructions=["Always include sources"],
    storage=SqlAgentStorage(table_name="web_agent", db_file="agents.db"),
    add_history_to_messages=True,
    markdown=True,
)

finance_agent = Agent(
    name="Finance Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)],
    instructions=["Use tables to display data"],
    storage=SqlAgentStorage(table_name="finance_agent", db_file="agents.db"),
    add_history_to_messages=True,
    markdown=True,
)

app = Playground(agents=[finance_agent, web_agent]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)
```


Authenticate with ethosian by running the following command:

```shell
ethosian auth
```

```bash
export ethosian_API_KEY=ethosian-***
```

Install dependencies and run the Agent Playground:

```
pip install 'fastapi[standard]' sqlalchemy

python playground.py
```

- Select the `localhost:7777` endpoint and start chatting with your agents!

## Agentic RAG

We were the first to pioneer Agentic RAG using our Auto-RAG paradigm. With Agentic RAG (or auto-rag), the Agent can search its knowledge base (vector db) for the specific information it needs to achieve its task, instead of always inserting the "context" into the prompt.

This saves tokens and improves response quality. Create a file `rag_agent.py`

```python
from ethosian.agent import Agent
from ethosian.model.openai import OpenAIChat
from ethosian.embedder.openai import OpenAIEmbedder
from ethosian.knowledge.pdf import PDFUrlKnowledgeBase
from ethosian.vectordb.lancedb import LanceDb, SearchType

# Create a knowledge base from a PDF
knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://ethosian-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    # Use LanceDB as the vector database
    vector_db=LanceDb(
        table_name="recipes",
        uri="tmp/lancedb",
        search_type=SearchType.vector,
        embedder=OpenAIEmbedder(model="text-embedding-3-small"),
    ),
)
# Comment out after first run as the knowledge base is loaded
knowledge_base.load()

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    # Add the knowledge base to the agent
    knowledge=knowledge_base,
    show_tool_calls=True,
    markdown=True,
)
agent.print_response("How do I make chicken and galangal in coconut milk soup", stream=True)
```

Install libraries and run the Agent:

```shell
pip install lancedb tantivy pypdf sqlalchemy

python rag_agent.py
```

## Structured Outputs

Agents can return their output in a structured format as a Pydantic model.

Create a file `structured_output.py`

```python
from typing import List
from pydantic import BaseModel, Field
from ethosian.agent import Agent
from ethosian.model.openai import OpenAIChat

# Define a Pydantic model to enforce the structure of the output
class MovieScript(BaseModel):
    setting: str = Field(..., description="Provide a nice setting for a blockbuster movie.")
    ending: str = Field(..., description="Ending of the movie. If not available, provide a happy ending.")
    genre: str = Field(..., description="Genre of the movie. If not available, select action, thriller or romantic comedy.")
    name: str = Field(..., description="Give a name to this movie")
    characters: List[str] = Field(..., description="Name of characters for this movie.")
    storyline: str = Field(..., description="3 sentence storyline for the movie. Make it exciting!")

# Agent that uses JSON mode
json_mode_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    description="You write movie scripts.",
    response_model=MovieScript,
)
# Agent that uses structured outputs
structured_output_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    description="You write movie scripts.",
    response_model=MovieScript,
    structured_outputs=True,
)

json_mode_agent.print_response("New York")
structured_output_agent.print_response("New York")
```

- Run the `structured_output.py` file

```shell
python structured_output.py
```

- The output is an object of the `MovieScript` class, here's how it looks:

```shell
MovieScript(
│   setting='A bustling and vibrant New York City',
│   ending='The protagonist saves the city and reconciles with their estranged family.',
│   genre='action',
│   name='City Pulse',
│   characters=['Alex Mercer', 'Nina Castillo', 'Detective Mike Johnson'],
│   storyline='In the heart of New York City, a former cop turned vigilante, Alex Mercer, teams up with a street-smart activist, Nina Castillo, to take down a corrupt political figure who threatens to destroy the city. As they navigate through the intricate web of power and deception, they uncover shocking truths that push them to the brink of their abilities. With time running out, they must race against the clock to save New York and confront their own demons.'
)
```

## Getting help

- Read the docs at <a href="https://docs.ethosianhq.com" target="_blank" rel="noopener noreferrer">docs.ethosianhq.com</a>
- Create an issue at <a href="https://github.com/ethosianhq/ethosian" target="_blank" rel="noopener noreferrer">github.com/ethosianhq/ethosian</a>

## More examples

### Agent that can write and run python code

<details>

<summary>Show code</summary>

The `PythonAgent` can achieve tasks by writing and running python code.

- Create a file `python_agent.py`

```python
from ethosian.agent.python import PythonAgent
from ethosian.model.openai import OpenAIChat
from ethosian.file.local.csv import CsvFile

python_agent = PythonAgent(
    model=OpenAIChat(id="gpt-4o"),
    files=[
        CsvFile(
            path="https://ethosian-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv",
            description="Contains information about movies from IMDB.",
        )
    ],
    markdown=True,
    pip_install=True,
    show_tool_calls=True,
)

python_agent.print_response("What is the average rating of movies?")
```

- Run the `python_agent.py`

```shell
python python_agent.py
```

</details>

### Agent that can analyze data using SQL

<details>

<summary>Show code</summary>

The `DuckDbAgent` can perform data analysis using SQL.

- Create a file `data_analyst.py`

```python
import json
from ethosian.model.openai import OpenAIChat
from ethosian.agent.duckdb import DuckDbAgent

data_analyst = DuckDbAgent(
    model=OpenAIChat(model="gpt-4o"),
    markdown=True,
    semantic_model=json.dumps(
        {
            "tables": [
                {
                    "name": "movies",
                    "description": "Contains information about movies from IMDB.",
                    "path": "https://ethosian-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv",
                }
            ]
        },
        indent=2,
    ),
)

data_analyst.print_response(
    "Show me a histogram of ratings. "
    "Choose an appropriate bucket size but share how you chose it. "
    "Show me the result as a pretty ascii diagram",
    stream=True,
)
```

- Install duckdb and run the `data_analyst.py` file

```shell
pip install duckdb

python data_analyst.py
```

</details>

### Check out the [cookbook](https://github.com/ethosianhq/ethosian/tree/main/cookbook) for more examples.

## Contributions

We're an open-source project and welcome contributions, please read the [contributing guide](https://github.com/ethosianhq/ethosian/blob/main/CONTRIBUTING.md) for more information.

## Request a feature

- If you have a feature request, please open an issue or make a pull request.
- If you have ideas on how we can improve, please create a discussion.

## Telemetry

ethosian logs which model an agent used so we can prioritize features for the most popular models.

You can disable this by setting `ethosian_TELEMETRY=false` in your environment.

<p align="left">
  <a href="#top">⬆️ Back to Top</a>
</p>
