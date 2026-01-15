# Knowledge-Powered Q&A and Action Bot

A configurable MCP server that acts as an intelligent support bot. It combines a searchable knowledge base (exposed as Resources) with action tools (create tickets, update records).

## Features

*   **Configurable Knowledge Base**: Define articles, FAQs, and docs in `config.json`.
*   **Search**: Tools to search the knowledge base.
*   **Actions**: Tools to create tickets, update records, and send notifications.
*   **Persona**: Customizable bot persona via configuration.

## Setup

1.  **Install Dependencies**:
    Ensure you have `uv` installed.
    ```bash
    uv add "mcp[cli]"
    ```

2.  **Configuration**:
    Edit `knowledge_bot/config.json` to customize the knowledge base, persona, and intents for your specific industry (SaaS, Banking, Healthcare, etc.).

## Running the Server

You can run the server directly using `uv`:

```bash
uv run knowledge_bot/bot.py
```

## Installation for Claude Desktop

To automatically install this server into Claude Desktop:

```bash
uv run mcp install knowledge_bot/bot.py
```

## Usage with Claude

Once connected, you can ask Claude questions like:
*   "How do I reset my password?" (Uses `search_knowledge` or reads `knowledge://` resources)
*   "Create a ticket for a database error." (Uses `create_ticket`)
*   "Update my email address." (Uses `update_record`)

Claude can also inspect the available knowledge by reading the `knowledge://index` resource.
