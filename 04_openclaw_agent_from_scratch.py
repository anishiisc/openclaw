"""
=============================================================================
Artifact 4: Build an OpenClaw-Style Agent Loop from Scratch
=============================================================================
File: 04_openclaw_agent_from_scratch.py
Author: Dr. Anish Roychowdhury
Description: Implements the core agent loop pattern from first principles.
             This is the same architecture that powers OpenClaw internally:
             
             User Task → LLM Reasoning → Tool Selection → Tool Execution 
             → Result Observation → Continue or Finish
             
             Inspired by the excellent 'claw0' teaching repository:
             https://github.com/shareAI-lab/claw0

Prerequisites:
    pip install anthropic python-dotenv

    This runs on any laptop or Google Colab.
    No OpenClaw gateway needed — pure educational implementation.

    Set ANTHROPIC_API_KEY in your .env file.
=============================================================================
"""

import os
import json
import subprocess
import math
from datetime import datetime
from typing import Any

from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# STEP 1: Define Tools
# ---------------------------------------------------------------------------
# In OpenClaw, these would be "skills". Here we define them as Python
# functions with Anthropic-compatible tool schemas.

TOOLS = [
    {
        "name": "calculator",
        "description": (
            "Perform mathematical calculations. Accepts a mathematical "
            "expression as a string and returns the result. Supports basic "
            "arithmetic (+, -, *, /), exponents (**), square root (sqrt), "
            "trigonometric functions (sin, cos, tan), and constants (pi, e)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "file_writer",
        "description": (
            "Write content to a file on the local filesystem. "
            "Creates the file if it doesn't exist, overwrites if it does."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Name of the file to create/write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["filename", "content"],
        },
    },
    {
        "name": "file_reader",
        "description": (
            "Read the contents of a file from the local filesystem."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Name of the file to read",
                }
            },
            "required": ["filename"],
        },
    },
    {
        "name": "shell_command",
        "description": (
            "Execute a shell command and return the output. "
            "Use for system information, listing files, checking "
            "installed packages, etc. Do NOT use for destructive operations."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute",
                }
            },
            "required": ["command"],
        },
    },
    {
        "name": "current_datetime",
        "description": "Get the current date and time.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]


# ---------------------------------------------------------------------------
# STEP 2: Implement Tool Execution
# ---------------------------------------------------------------------------
# Each tool function takes the input parameters and returns a string result.

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """
    Execute a tool by name and return the result as a string.
    
    This is the 'Tool Executor' component in OpenClaw's architecture.
    In production OpenClaw, this dispatches to skill scripts (Python, 
    Node.js, shell) based on the SKILL.md configuration.
    """

    if tool_name == "calculator":
        return _tool_calculator(tool_input["expression"])
    elif tool_name == "file_writer":
        return _tool_file_writer(tool_input["filename"], tool_input["content"])
    elif tool_name == "file_reader":
        return _tool_file_reader(tool_input["filename"])
    elif tool_name == "shell_command":
        return _tool_shell_command(tool_input["command"])
    elif tool_name == "current_datetime":
        return _tool_current_datetime()
    else:
        return f"Error: Unknown tool '{tool_name}'"


def _tool_calculator(expression: str) -> str:
    """Safe mathematical expression evaluator."""
    # Provide safe math functions
    safe_env = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "pi": math.pi,
        "e": math.e,
        "pow": pow,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, safe_env)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"


def _tool_file_writer(filename: str, content: str) -> str:
    """Write content to a file (sandboxed to current directory)."""
    # Security: prevent path traversal
    safe_name = os.path.basename(filename)
    try:
        with open(safe_name, "w") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{safe_name}'"
    except Exception as e:
        return f"File write error: {e}"


def _tool_file_reader(filename: str) -> str:
    """Read content from a file."""
    safe_name = os.path.basename(filename)
    try:
        with open(safe_name, "r") as f:
            content = f.read()
        return f"File contents of '{safe_name}':\n{content}"
    except FileNotFoundError:
        return f"File not found: '{safe_name}'"
    except Exception as e:
        return f"File read error: {e}"


def _tool_shell_command(command: str) -> str:
    """Execute a shell command with safety restrictions."""
    # Block destructive commands
    dangerous = ["rm -rf", "mkfs", "dd if=", "shutdown", "reboot", "> /dev/"]
    for d in dangerous:
        if d in command:
            return f"Blocked: '{command}' contains dangerous pattern '{d}'"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout or result.stderr or "(no output)"
        return f"Command output:\n{output.strip()}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 10 seconds"
    except Exception as e:
        return f"Command error: {e}"


def _tool_current_datetime() -> str:
    """Return the current date and time."""
    now = datetime.now()
    return f"Current date/time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"


# ---------------------------------------------------------------------------
# STEP 3: The Agent Loop
# ---------------------------------------------------------------------------
# This is the heart of every agentic AI system. OpenClaw, Claude Code,
# and similar tools all implement variations of this loop.

class AgentLoop:
    """
    The core agent loop that powers OpenClaw-style autonomous agents.
    
    The loop works as follows:
    1. User provides a task
    2. LLM reasons about what to do
    3. If the LLM wants to use a tool → execute it, feed result back
    4. If the LLM provides a final answer → return it
    5. Repeat steps 2-4 until done (with a max iteration guard)
    
    This is the same ReAct (Reasoning + Acting) pattern used by OpenClaw.
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-6",
        max_iterations: int = 10,
        verbose: bool = True,
    ):
        try:
            import anthropic
        except ImportError:
            raise ImportError("Install: pip install anthropic")

        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = model
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.total_tokens_in = 0
        self.total_tokens_out = 0

        # System prompt — the agent's "personality" and rules
        self.system_prompt = """You are an autonomous AI agent running locally on the user's machine.
You have access to tools that let you interact with the filesystem,
perform calculations, and execute shell commands.

Rules:
1. Think step-by-step about how to accomplish the user's task
2. Use tools when you need to — don't guess at information you can look up
3. After using tools, reflect on the results before deciding next steps
4. Provide a clear, complete final answer when the task is done
5. If a tool fails, try an alternative approach
6. Be explicit about what you're doing and why

You are running in a sandboxed environment. File operations are
restricted to the current directory. Destructive shell commands are blocked."""

    def run(self, task: str) -> str:
        """
        Execute the agent loop for a given task.
        Returns the final text response from the agent.
        """
        if self.verbose:
            print(f"\n{'=' * 60}")
            print(f"🦞 Agent Loop Started")
            print(f"{'=' * 60}")
            print(f"Task: {task}")
            print(f"Model: {self.model}")
            print(f"Max iterations: {self.max_iterations}")

        # Initialize the conversation with the user's task
        messages = [{"role": "user", "content": task}]

        for iteration in range(1, self.max_iterations + 1):
            if self.verbose:
                print(f"\n{'─' * 40}")
                print(f"Iteration {iteration}/{self.max_iterations}")
                print(f"{'─' * 40}")

            # Call the LLM with tools available
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=self.system_prompt,
                tools=TOOLS,
                messages=messages,
            )

            # Track token usage
            self.total_tokens_in += response.usage.input_tokens
            self.total_tokens_out += response.usage.output_tokens

            if self.verbose:
                print(f"[📊] Tokens: {response.usage.input_tokens} in / "
                      f"{response.usage.output_tokens} out")
                print(f"[📊] Stop reason: {response.stop_reason}")

            # Process response content blocks
            assistant_content = response.content
            tool_results = []
            final_text = ""

            for block in assistant_content:
                if block.type == "text":
                    final_text += block.text
                    if self.verbose:
                        print(f"\n[💭 Agent Thinking]\n{block.text}")

                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    if self.verbose:
                        print(f"\n[🔧 Tool Call] {tool_name}")
                        print(f"    Input: {json.dumps(tool_input, indent=2)}")

                    # Execute the tool
                    result = execute_tool(tool_name, tool_input)

                    if self.verbose:
                        # Truncate long outputs for display
                        display_result = (
                            result[:300] + "..."
                            if len(result) > 300
                            else result
                        )
                        print(f"    Result: {display_result}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result,
                    })

            # If the LLM used tools, feed results back and continue
            if tool_results:
                messages.append({"role": "assistant", "content": assistant_content})
                messages.append({"role": "user", "content": tool_results})
                continue

            # If no tools were called, we have the final answer
            if response.stop_reason == "end_turn":
                if self.verbose:
                    self._print_summary()
                return final_text

        # Max iterations reached
        if self.verbose:
            print(f"\n[⚠️] Max iterations ({self.max_iterations}) reached!")
            self._print_summary()
        return final_text or "Agent reached max iterations without completing."

    def _print_summary(self):
        """Print execution summary with cost estimate."""
        cost = (
            self.total_tokens_in * 3 / 1_000_000
            + self.total_tokens_out * 15 / 1_000_000
        )
        print(f"\n{'=' * 60}")
        print(f"Agent Loop Complete")
        print(f"{'=' * 60}")
        print(f"Total input tokens:  {self.total_tokens_in:,}")
        print(f"Total output tokens: {self.total_tokens_out:,}")
        print(f"Estimated cost: ${cost:.4f}")


# ---------------------------------------------------------------------------
# STEP 4: Demo tasks
# ---------------------------------------------------------------------------

def demo_tasks():
    """
    Run a series of demo tasks to showcase the agent loop.
    Each task exercises different tool combinations.
    """
    agent = AgentLoop(verbose=True)

    # Task 1: Multi-tool task — calculate, write, and verify
    task = """
    I need you to do the following:
    1. Calculate the compound interest on $10,000 at 7.5% annual rate 
       for 5 years, compounded monthly
    2. Write the result to a file called 'interest_report.txt' with 
       a nicely formatted report including the formula used
    3. Read back the file to verify it was written correctly
    4. Tell me the current date and time
    """

    print("\n" + "=" * 60)
    print("DEMO: Multi-Tool Agent Task")
    print("=" * 60)

    result = agent.run(task)

    print(f"\n{'─' * 40}")
    print("FINAL ANSWER:")
    print(f"{'─' * 40}")
    print(result)


def demo_simple():
    """A simpler demo for quick testing."""
    agent = AgentLoop(verbose=True)

    task = (
        "What is the square root of 144 multiplied by pi? "
        "Show me the calculation step by step."
    )

    result = agent.run(task)
    print(f"\nFinal answer: {result}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n🦞 OpenClaw-Style Agent Loop — Built from Scratch\n")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("[!] ANTHROPIC_API_KEY not set.")
        print("[!] Create a .env file with: ANTHROPIC_API_KEY=sk-ant-...")
        print("[!] Get your key at: https://console.anthropic.com/")
        exit(1)

    # Run the demo
    # For a quick test, use demo_simple()
    # For the full showcase, use demo_tasks()
    
    print("Choose a demo:")
    print("  1. Simple calculation (quick, low cost)")
    print("  2. Multi-tool task (comprehensive, slightly higher cost)")

    choice = input("\nEnter 1 or 2 (default: 1): ").strip() or "1"

    if choice == "2":
        demo_tasks()
    else:
        demo_simple()
