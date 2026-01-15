"""
Knowledge-Powered Q&A and Action Bot MCP Server

This server implements a configurable bot that exposes a knowledge base as resources
and provides action tools for support workflows.
"""

import json
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP, Context

# Initialize FastMCP
mcp = FastMCP("KnowledgeBot", json_response=True)

import os

# Load Configuration
# Get the directory where bot.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def load_config() -> Dict:
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": f"Config file not found at {CONFIG_PATH}"}

config = load_config()
KNOWLEDGE_BASE = {item["id"]: item for item in config.get("knowledge", [])}

# -----------------------------------------------------------------------------
# Resources: Knowledge Base
# -----------------------------------------------------------------------------

@mcp.resource("knowledge://index")
def list_knowledge() -> str:
    """
    Returns a list of all available knowledge base articles with their IDs and titles.
    Use this to discover what information is available.
    """
    summary = []
    for k_id, item in KNOWLEDGE_BASE.items():
        summary.append(f"- [{k_id}] {item['title']} (Tags: {', '.join(item.get('tags', []))})")
    return "\n".join(summary)

@mcp.resource("knowledge://{article_id}")
def get_knowledge_article(article_id: str) -> str:
    """
    Retrieves the full content of a specific knowledge base article by its ID.
    """
    article = KNOWLEDGE_BASE.get(article_id)
    if not article:
        return f"Error: Article with ID '{article_id}' not found."
    
    return f"""
Title: {article['title']}
Tags: {', '.join(article.get('tags', []))}
---------------------------------------------------
{article['content']}
"""

# -----------------------------------------------------------------------------
# Tools: Search & Actions
# -----------------------------------------------------------------------------

@mcp.tool()
def search_knowledge(query: str) -> List[str]:
    """
    CRITICAL: You MUST use this tool FIRST for ANY user question regarding the platform (e.g., password, login, API, billing).
    Do NOT answer from your own internal knowledge. 
    Even if you think you know the answer, you MUST verify it with this tool first.
    Search the knowledge base for articles matching the query.
    Returns a list of matching article summaries (ID and Title).
    
    IMPORTANT: After finding a relevant article ID (e.g., 'kb-001'), you MUST then 
    read its content using the `read_knowledge_article` tool to answer the user's question.
    """
    query_terms = query.lower().split()
    results = []
    
    for k_id, item in KNOWLEDGE_BASE.items():
        # Search in title, content, and tags
        text_to_search = (
            item["title"].lower() + 
            " " + 
            item["content"].lower() + 
            " " + 
            " ".join(item.get("tags", [])).lower()
        )
        
        # Check if ALL terms in the query are present in the text
        if all(term in text_to_search for term in query_terms):
            results.append(f"[{k_id}] {item['title']}")
            
    if not results:
        # Fallback: Check if ANY term is present (for partial matches)
        for k_id, item in KNOWLEDGE_BASE.items():
            text_to_search = (
                item["title"].lower() + " " + 
                item["content"].lower() + " " + 
                " ".join(item.get("tags", [])).lower()
            )
            if any(term in text_to_search for term in query_terms):
                results.append(f"[{k_id}] {item['title']} (Partial Match)")
        
        # Remove duplicates if any (though logic above separates them)
        results = list(set(results))

    if not results:
        return ["No matching articles found."]
        
    return results

@mcp.tool()
def read_knowledge_article(article_id: str) -> str:
    """
    Read the full content of a knowledge base article.
    Use this after finding an article ID with search_knowledge.
    """
    return get_knowledge_article(article_id)

@mcp.tool()
def create_ticket(title: str, description: str, priority: str = "normal") -> str:
    """
    Create a support ticket.
    ONLY use this if you have ALREADY searched the knowledge base and found no solution.
    Priority options: 'low', 'normal', 'high', 'urgent'.
    """
    # In a real app, this would connect to Jira/Zendesk
    ticket_id = f"TICKET-{len(title)}" # Mock ID
    print(f"Creating Ticket: {title} ({priority})")
    return f"Ticket created successfully. Ticket ID: {ticket_id}. Our team will review it shortly."

@mcp.tool()
def update_record(record_id: str, data: Dict[str, str]) -> str:
    """
    Update a user record or account detail.
    Use this to change user preferences, contact info, etc.
    """
    # Mock update
    print(f"Updating Record {record_id} with {data}")
    return f"Record {record_id} updated successfully with: {json.dumps(data)}"

@mcp.tool()
def send_notification(user_id: str, message: str, channel: str = "email") -> str:
    """
    Send a notification to the user.
    Channels: 'email', 'sms', 'in-app'.
    """
    # Mock notification
    print(f"Sending {channel} to {user_id}: {message}")
    return f"Notification sent to {user_id} via {channel}."

@mcp.tool()
def escalate_to_human(reason: str, context: str) -> str:
    """
    Escalate the conversation to a human agent.
    Use this when the user is frustrated, asks for a human, or the issue is too complex.
    """
    print(f"ESCALATION TRIGGERED: {reason}")
    return "I have flagged this conversation for a human agent. They will join shortly. Is there anything else I can check while we wait?"

# -----------------------------------------------------------------------------
# Prompts: Persona & Context
# -----------------------------------------------------------------------------

@mcp.prompt()
def bot_persona() -> str:
    """
    Returns the configured persona and instructions for the bot.
    Claude should use this to understand its role.
    """
    persona = config.get("persona", "You are a helpful assistant.")
    constraints = "\n".join(config.get("constraints", []))
    
    return f"""
{persona}

{constraints}
"""

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
