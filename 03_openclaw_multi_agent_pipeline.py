"""
=============================================================================
Artifact 3: Multi-Agent Pipeline with OpenClaw
=============================================================================
File: 03_openclaw_multi_agent_pipeline.py
Author: Dr. Anish Roychowdhury
Description: Demonstrates a 3-stage agent pipeline:
             Researcher → Summariser → Reporter
             
             Each agent has a specialised role. The output of one
             feeds into the next, creating a composable workflow.

Prerequisites:
    pip install openclaw-sdk python-dotenv
    (or)
    pip install anthropic python-dotenv  (for standalone mode)

    For Google Colab: Works in standalone mode without a gateway.
=============================================================================
"""

import asyncio
import os
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Data structures for the pipeline
# ---------------------------------------------------------------------------

@dataclass
class AgentConfig:
    """Configuration for a single agent in the pipeline."""
    name: str
    role: str
    system_prompt: str
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 1024


@dataclass
class PipelineResult:
    """Result from a single pipeline stage."""
    agent_name: str
    stage: int
    input_text: str
    output_text: str
    tokens_in: int = 0
    tokens_out: int = 0
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )


@dataclass
class PipelineReport:
    """Complete pipeline execution report."""
    topic: str
    stages: list[PipelineResult] = field(default_factory=list)
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_cost_usd: float = 0.0

    def add_result(self, result: PipelineResult):
        self.stages.append(result)
        self.total_tokens_in += result.tokens_in
        self.total_tokens_out += result.tokens_out
        # Claude Sonnet 4.6 pricing: $3/$15 per M tokens
        self.total_cost_usd += (
            result.tokens_in * 3 / 1_000_000
            + result.tokens_out * 15 / 1_000_000
        )


# ---------------------------------------------------------------------------
# Define the 3-agent pipeline
# ---------------------------------------------------------------------------

RESEARCHER = AgentConfig(
    name="Researcher",
    role="Deep Research Analyst",
    system_prompt="""You are a deep research analyst. Your job is to provide
comprehensive, factual analysis on any given topic.

Rules:
- Structure your research with clear sections
- Include specific data points, dates, and names where possible
- Distinguish between established facts and emerging trends
- Note areas of uncertainty or debate
- Be thorough but focused — aim for depth over breadth
- Output should be 300-500 words of substantive research""",
)

SUMMARISER = AgentConfig(
    name="Summariser",
    role="Executive Summariser",
    system_prompt="""You are an executive summariser. You receive detailed
research and distil it into crisp, actionable insights.

Rules:
- Extract the 3-5 most important findings
- For each finding, provide: the insight, why it matters, and what to do
- Use clear, jargon-free language
- Highlight any risks or caveats
- Keep total output under 200 words
- Format as numbered key findings""",
)

REPORTER = AgentConfig(
    name="Reporter",
    role="LinkedIn Content Formatter",
    system_prompt="""You are a professional content formatter who creates
engaging LinkedIn posts from executive summaries.

Rules:
- Start with a compelling hook (first line is crucial)
- Use short paragraphs (1-2 sentences each)
- Include relevant emojis sparingly (max 3-4)
- Add a clear call-to-action at the end
- Include 3-5 relevant hashtags
- Keep the tone professional but approachable
- Total length: 150-250 words
- Make it scannable — busy professionals read on mobile""",
)


# ---------------------------------------------------------------------------
# Pipeline executor (Standalone mode — uses Anthropic SDK directly)
# ---------------------------------------------------------------------------

class AgentPipeline:
    """
    A multi-agent pipeline that chains agents sequentially.
    
    This implements the same pattern that OpenClaw uses internally
    when orchestrating multi-step workflows, but runs standalone
    using the Anthropic SDK directly.
    """

    def __init__(self, agents: list[AgentConfig]):
        self.agents = agents
        self.report: Optional[PipelineReport] = None

        try:
            import anthropic
            self.client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        except ImportError:
            raise ImportError(
                "Install anthropic: pip install anthropic"
            )

    def _call_agent(self, agent: AgentConfig, user_input: str) -> PipelineResult:
        """Execute a single agent and return the result."""
        response = self.client.messages.create(
            model=agent.model,
            max_tokens=agent.max_tokens,
            system=agent.system_prompt,
            messages=[{"role": "user", "content": user_input}],
        )

        output_text = ""
        for block in response.content:
            if block.type == "text":
                output_text += block.text

        return PipelineResult(
            agent_name=agent.name,
            stage=0,  # Will be set by run()
            input_text=user_input[:200] + "..."
            if len(user_input) > 200
            else user_input,
            output_text=output_text,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
        )

    def run(self, topic: str) -> PipelineReport:
        """
        Execute the full pipeline: each agent's output feeds into the next.
        
        Flow: topic → Agent1 → output1 → Agent2 → output2 → Agent3 → final
        """
        self.report = PipelineReport(topic=topic)
        current_input = topic

        print(f"\n{'=' * 60}")
        print(f"Multi-Agent Pipeline Execution")
        print(f"Topic: {topic}")
        print(f"{'=' * 60}")

        for i, agent in enumerate(self.agents):
            stage_num = i + 1
            print(f"\n{'─' * 40}")
            print(f"Stage {stage_num}/{len(self.agents)}: {agent.name}")
            print(f"Role: {agent.role}")
            print(f"{'─' * 40}")

            # Construct the prompt for this stage
            if i == 0:
                # First agent gets the raw topic
                prompt = f"Research the following topic thoroughly:\n\n{current_input}"
            else:
                # Subsequent agents get the previous output with context
                prompt = (
                    f"The previous agent ({self.agents[i-1].name}) "
                    f"produced the following output:\n\n"
                    f"---\n{current_input}\n---\n\n"
                    f"Now apply your expertise to transform this content."
                )

            # Execute the agent
            result = self._call_agent(agent, prompt)
            result.stage = stage_num

            # Track results
            self.report.add_result(result)

            # Print output preview
            preview = result.output_text[:300]
            print(f"\nOutput preview:\n{preview}...")
            print(
                f"\n[📊] Tokens: {result.tokens_in} in / "
                f"{result.tokens_out} out"
            )

            # Feed output to next agent
            current_input = result.output_text

        # Print summary
        self._print_summary()
        return self.report

    def _print_summary(self):
        """Print the pipeline execution summary."""
        if not self.report:
            return

        print(f"\n{'=' * 60}")
        print(f"Pipeline Execution Summary")
        print(f"{'=' * 60}")
        print(f"Topic: {self.report.topic}")
        print(f"Stages completed: {len(self.report.stages)}")
        print(f"Total input tokens:  {self.report.total_tokens_in:,}")
        print(f"Total output tokens: {self.report.total_tokens_out:,}")
        print(f"Estimated cost: ${self.report.total_cost_usd:.4f}")

        print(f"\n{'─' * 40}")
        print(f"FINAL OUTPUT (from {self.agents[-1].name}):")
        print(f"{'─' * 40}")
        if self.report.stages:
            print(self.report.stages[-1].output_text)
        print(f"{'─' * 40}")


# ---------------------------------------------------------------------------
# Pipeline executor (SDK mode — requires running OpenClaw gateway)
# ---------------------------------------------------------------------------

async def run_with_sdk(topic: str):
    """
    Alternative implementation using the OpenClaw SDK.
    Requires a running OpenClaw gateway with the pipeline feature.
    """
    try:
        from openclaw_sdk import OpenClawClient

        async with OpenClawClient.connect() as client:
            print("[✓] Connected to OpenClaw gateway")

            # Create specialised agents
            researcher = client.get_agent("researcher")
            summariser = client.get_agent("summariser")
            reporter = client.get_agent("reporter")

            # Execute pipeline
            print("[→] Stage 1: Research...")
            research = await researcher.execute(
                f"Research thoroughly: {topic}"
            )

            print("[→] Stage 2: Summarise...")
            summary = await summariser.execute(
                f"Summarise this research:\n{research.content}"
            )

            print("[→] Stage 3: Format for LinkedIn...")
            post = await reporter.execute(
                f"Create a LinkedIn post from:\n{summary.content}"
            )

            print(f"\n{'=' * 60}")
            print("Final LinkedIn Post:")
            print(f"{'=' * 60}")
            print(post.content)

    except Exception as e:
        print(f"[!] SDK mode failed: {e}")
        print("[!] Falling back to standalone mode...")
        pipeline = AgentPipeline([RESEARCHER, SUMMARISER, REPORTER])
        pipeline.run(topic)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n🦞 OpenClaw Multi-Agent Pipeline Demo\n")

    # Choose your research topic
    topic = (
        "The rise of agentic AI in 2026: How frameworks like OpenClaw "
        "are shifting competition from model quality to agent orchestration, "
        "and what this means for enterprise AI strategy"
    )

    # Check if OpenClaw gateway is available
    use_sdk = os.getenv("OPENCLAW_GATEWAY_WS_URL") is not None

    if use_sdk:
        asyncio.run(run_with_sdk(topic))
    else:
        # Standalone mode — runs anywhere with an Anthropic API key
        try:
            pipeline = AgentPipeline([RESEARCHER, SUMMARISER, REPORTER])
            report = pipeline.run(topic)

            # Save the report
            report_data = {
                "topic": report.topic,
                "total_tokens_in": report.total_tokens_in,
                "total_tokens_out": report.total_tokens_out,
                "total_cost_usd": report.total_cost_usd,
                "final_output": report.stages[-1].output_text
                if report.stages
                else "",
                "stages": [
                    {
                        "agent": s.agent_name,
                        "stage": s.stage,
                        "tokens_in": s.tokens_in,
                        "tokens_out": s.tokens_out,
                        "output_preview": s.output_text[:500],
                    }
                    for s in report.stages
                ],
            }

            output_file = "pipeline_report.json"
            with open(output_file, "w") as f:
                json.dump(report_data, f, indent=2)
            print(f"\n[✓] Report saved to {output_file}")

        except Exception as e:
            print(f"\n[!] Error: {e}")
            print("[!] Make sure ANTHROPIC_API_KEY is set in your .env file")


if __name__ == "__main__":
    main()
