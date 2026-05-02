"""
=============================================================================
Artifact 1: Your First OpenClaw Agent
=============================================================================
File: 01_openclaw_basic_agent.py
Author: Dr. Anish Roychowdhury
Description: Connects to a local OpenClaw gateway and executes a simple
             research task using the OpenClaw Python SDK.

Prerequisites:
    pip install openclaw-sdk python-dotenv

    You need a running OpenClaw instance (gateway on port 18789).
    Set your environment variables in a .env file:
        OPENCLAW_GATEWAY_WS_URL=ws://127.0.0.1:18789/gateway
        OPENCLAW_API_KEY=your-api-key (if configured)

    For Google Colab: This script requires a running OpenClaw gateway.
    You can run OpenClaw in a separate Colab cell using the npm installation
    method, or connect to a remote gateway.
=============================================================================
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ---------------------------------------------------------------------------
# Option A: Using the OpenClaw SDK (requires running gateway)
# ---------------------------------------------------------------------------

async def run_with_sdk():
    """
    Demonstrates the standard OpenClaw SDK workflow:
    1. Connect to the gateway
    2. Get or create an agent
    3. Execute a task
    4. Process the response
    """
    try:
        from openclaw_sdk import OpenClawClient

        print("=" * 60)
        print("OpenClaw SDK — Basic Agent Demo")
        print("=" * 60)

        # Connect to the gateway (auto-detects local instance)
        async with OpenClawClient.connect() as client:
            print("[✓] Connected to OpenClaw gateway\n")

            # Get a reference to an agent
            # 'bot' is the default agent ID in most OpenClaw installations
            agent = client.get_agent("bot")
            print(f"[✓] Agent loaded: {agent.agent_id}")
            print(f"    Session key: {agent.session_key}\n")

            # Execute a simple research task
            task = (
                "List 3 key differences between ReAct and Chain-of-Thought "
                "prompting for LLM agents. Keep it concise."
            )
            print(f"[→] Sending task:\n    '{task}'\n")

            result = await agent.execute(task)
            print("[✓] Agent response:")
            print("-" * 40)
            print(result.content)
            print("-" * 40)

            # You can also stream responses token-by-token
            print("\n[→] Streaming a follow-up question...\n")
            stream_task = "Which approach is better for tool-using agents and why?"

            async for event in agent.execute_stream(stream_task):
                if hasattr(event, "text"):
                    print(event.text, end="", flush=True)
            print("\n")

    except ImportError:
        print("[!] openclaw-sdk not installed. Run: pip install openclaw-sdk")
        print("[!] Falling back to Option B (standalone mode)...\n")
        await run_standalone()
    except Exception as e:
        print(f"[!] Gateway connection failed: {e}")
        print("[!] Make sure OpenClaw is running: openclaw start")
        print("[!] Falling back to Option B (standalone mode)...\n")
        await run_standalone()


# ---------------------------------------------------------------------------
# Option B: Standalone mode using Anthropic SDK directly (no gateway needed)
# This is perfect for Colab or quick experimentation.
# ---------------------------------------------------------------------------

async def run_standalone():
    """
    If you don't have a running OpenClaw gateway, this demonstrates
    the same concept using the Anthropic SDK directly — the same
    LLM backbone that OpenClaw uses internally.

    Prerequisites:
        pip install anthropic
        Set ANTHROPIC_API_KEY in your .env file
    """
    try:
        import anthropic
    except ImportError:
        print("[!] Install anthropic: pip install anthropic")
        return

    print("=" * 60)
    print("Standalone Mode — Direct LLM Agent (No Gateway)")
    print("=" * 60)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("[!] Set ANTHROPIC_API_KEY in your .env file")
        return

    client = anthropic.Anthropic(api_key=api_key)

    # Define the system prompt — this is what makes it an "agent"
    system_prompt = """You are a research assistant agent. When given a task:
1. Break it down into clear steps
2. Execute each step methodically
3. Provide structured, actionable output
4. Cite your reasoning at each step

You think step-by-step and are thorough but concise."""

    task = (
        "List 3 key differences between ReAct and Chain-of-Thought "
        "prompting for LLM agents. Keep it concise."
    )

    print(f"\n[→] Sending task:\n    '{task}'\n")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": task}],
    )

    print("[✓] Agent response:")
    print("-" * 40)
    for block in response.content:
        if block.type == "text":
            print(block.text)
    print("-" * 40)

    # Token usage tracking (important for cost management)
    usage = response.usage
    print(f"\n[📊] Token Usage:")
    print(f"    Input tokens:  {usage.input_tokens}")
    print(f"    Output tokens: {usage.output_tokens}")
    estimated_cost = (
        usage.input_tokens * 3 / 1_000_000
        + usage.output_tokens * 15 / 1_000_000
    )
    print(f"    Estimated cost: ${estimated_cost:.4f}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n🦞 OpenClaw Basic Agent Demo\n")
    asyncio.run(run_with_sdk())
