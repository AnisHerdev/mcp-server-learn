"""
Simple Schedule Manager MCP Server

Run:
    uv run schedule_manager.py
"""

from typing import List, Dict, Tuple
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ScheduleManager", json_response=True)

# -----------------------------
# In-memory schedule store
# -----------------------------
# {
#   "Alice": [(10, 11), (14, 16)],
#   "Bob":   [(9, 10), (13, 15)]
# }

SCHEDULES: Dict[str, List[Tuple[int, int]]] = {}

WORK_START = 9
WORK_END = 18


# -----------------------------
# Tool: Add busy time
# -----------------------------
@mcp.tool()
def add_busy_time(name: str, start: int, end: int) -> str:
    """
    Add a busy time slot for a person.
    Time is in 24-hour format (e.g., 13 = 1 PM)
    """
    if name not in SCHEDULES:
        SCHEDULES[name] = []

    SCHEDULES[name].append((start, end))
    return f"Added busy time for {name}: {start}:00–{end}:00"


# -----------------------------
# Helper: get free slots
# -----------------------------
def get_free_slots(busy: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    busy.sort()
    free = []
    current = WORK_START

    for start, end in busy:
        if start > current:
            free.append((current, start))
        current = max(current, end)

    if current < WORK_END:
        free.append((current, WORK_END))

    return free


# -----------------------------
# Tool: Find common free time
# -----------------------------
@mcp.tool()
def find_common_free_time(members: List[str]) -> List[str]:
    """
    Find common free time slots for given members
    """
    all_free_slots = []

    for member in members:
        busy = SCHEDULES.get(member, [])
        free = get_free_slots(busy)
        all_free_slots.append(free)

    # Intersect free slots
    common = all_free_slots[0]

    for slots in all_free_slots[1:]:
        new_common = []
        for a_start, a_end in common:
            for b_start, b_end in slots:
                start = max(a_start, b_start)
                end = min(a_end, b_end)
                if start < end:
                    new_common.append((start, end))
        common = new_common

    return [f"{s}:00–{e}:00" for s, e in common]


# -----------------------------
# Prompt: Message to group
# -----------------------------
@mcp.prompt()
def meeting_message(members: List[str]) -> str:
    """
    Generate a message announcing free meeting time
    """
    free_slots = find_common_free_time(members)

    if not free_slots:
        return "No common free time found for all members today."

    slots = ", ".join(free_slots)
    return (
        f"All members ({', '.join(members)}) are available at the following times: "
        f"{slots}. Please confirm which slot works best."
    )


# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
