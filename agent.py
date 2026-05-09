import json
import anthropic
from datetime import datetime
from pathlib import Path
from tools.registry import get_user_profiles, get_registry_hives
from tools.mft import get_mft_timeline

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a senior DFIR analyst performing autonomous triage on a Windows XP disk image.

You have access to these tools:
- get_user_profiles: List user accounts on the system
- get_registry_hives: Check which registry hives are available
- get_mft_timeline: Extract filesystem timeline entries

YOUR REASONING PROTOCOL:
1. Start by identifying user profiles on the system.
2. Check which registry hives are available.
3. Run an MFT timeline focused on the suspect user's Documents and Settings folder.
4. After each tool result, explicitly ask yourself:
   - Does this make sense given what I already know?
   - Is anything missing or unexpected?
   - Do I need to re-run any tool with different parameters?
5. Label every finding as one of:
   - CONFIRMED: supported by multiple sources or clearly valid
   - INFERRED: logical conclusion from single source
   - UNVERIFIED: suspicious but uncorroborated
6. When analysis is complete, output a structured JSON report.

HARD RULES:
- Never assert a finding as fact if only one source supports it.
- Stop after 10 tool calls maximum.
- If a tool returns an error, log it and continue with remaining tools.

FINAL REPORT FORMAT:
{
  "case": "NIST Hacking Case - Dell Latitude CPi",
  "analyst": "SIFT MCP Agent",
  "timestamp": "<iso timestamp>",
  "findings": [
    {
      "finding": "<description>",
      "confidence": "CONFIRMED|INFERRED|UNVERIFIED",
      "source": "<which tool produced this>",
      "significance": "HIGH|MEDIUM|LOW"
    }
  ],
  "suspect_accounts": [],
  "missing_artifacts": [],
  "recommended_next_steps": [],
  "iterations_used": 0
}"""

TOOLS = [
    {
        "name": "get_user_profiles",
        "description": "List Windows user profiles from a mounted disk image.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mount_path": {
                    "type": "string",
                    "description": "Path where disk image is mounted"
                }
            },
            "required": ["mount_path"]
        }
    },
    {
        "name": "get_registry_hives",
        "description": "List available Windows registry hives from a mounted disk image.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mount_path": {
                    "type": "string",
                    "description": "Path where disk image is mounted"
                }
            },
            "required": ["mount_path"]
        }
    },
    {
        "name": "get_mft_timeline",
        "description": "Extract MFT filesystem timeline from a disk image using fls.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Full path to the E01 disk image"
                },
                "filter_path": {
                    "type": "string",
                    "description": "Optional path filter e.g. Mr. Evil"
                }
            },
            "required": ["image_path"]
        }
    }
]

def call_tool(name: str, arguments: dict) -> str:
    """Execute a tool call and return result as string."""
    print(f"  [TOOL] {name}({json.dumps(arguments)})")
    try:
        if name == "get_user_profiles":
            result = get_user_profiles(arguments["mount_path"])
        elif name == "get_registry_hives":
            result = get_registry_hives(arguments["mount_path"])
        elif name == "get_mft_timeline":
            result = get_mft_timeline(
                image_path=arguments["image_path"],
                filter_path=arguments.get("filter_path")
            )
        else:
            result = {"error": f"Unknown tool: {name}"}
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

def save_log(log: list, output_dir: str = "./logs"):
    """Save execution log to disk."""
    Path(output_dir).mkdir(exist_ok=True)
    filename = f"triage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = Path(output_dir) / filename
    with open(path, "w") as f:
        json.dump(log, f, indent=2, default=str)
    print(f"\n[LOG] Execution log saved: {path}")
    return str(path)

def run_triage(mount_path: str, image_path: str, max_iterations: int = 10):
    """Run the self-correcting triage loop."""
    print(f"\n{'='*60}")
    print(f"SIFT MCP TRIAGE AGENT")
    print(f"Mount path:  {mount_path}")
    print(f"Image path:  {image_path}")
    print(f"Max iterations: {max_iterations}")
    print(f"{'='*60}\n")

    messages = [
        {
            "role": "user",
            "content": (
                f"Begin autonomous triage.\n"
                f"Mounted image path: {mount_path}\n"
                f"Raw image path: {image_path}\n"
                f"Identify all user accounts, available artifacts, "
                f"and any suspicious activity. "
                f"Follow your reasoning protocol at each step."
            )
        }
    ]

    execution_log = []
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        log_entry = {
            "iteration": iteration,
            "stop_reason": response.stop_reason,
            "tool_calls": [],
            "token_usage": {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens
            }
        }

        
        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            execution_log.append(log_entry)
            log_path = save_log(execution_log)
            print(f"\n{'='*60}")
            print("TRIAGE COMPLETE")
            print(f"{'='*60}")
            print(final_text)
            return {"report": final_text, "log_path": log_path, "iterations": iteration}

        
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                log_entry["tool_calls"].append({
                    "tool": block.name,
                    "input": block.input,
                    "timestamp": datetime.now().isoformat()
                })
                result = call_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        execution_log.append(log_entry)
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    
    print("\n[WARNING] Max iterations reached")
    save_log(execution_log)
    return {"report": "MAX ITERATIONS REACHED", "iterations": iteration}


if __name__ == "__main__":
    run_triage(
        mount_path="/mnt/windows_mount",
        image_path="/cases/hacking_case/4Dell Latitude CPi.E01"
    )
