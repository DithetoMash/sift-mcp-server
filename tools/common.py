import subprocess

ALLOWED_COMMANDS = ["ewfinfo", "ewfmount", "mmls", "fls", "mactime", "istat"]
BLOCKED_PATTERNS = ["rm ", "dd ", "mkfs", "shred", "wget", "curl", ">"]

def safe_run(cmd: list, timeout: int = 60) -> dict:
    """Run a whitelisted command safely and return structured output."""
    binary = cmd[0]
    if binary not in ALLOWED_COMMANDS:
        return {"error": f"Blocked: '{binary}' is not an allowed command."}
    cmd_str = " ".join(cmd)
    for pattern in BLOCKED_PATTERNS:
        if pattern in cmd_str:
            return {"error": f"Blocked: dangerous pattern '{pattern}' detected."}
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "stdout": result.stdout[:8000],
            "stderr": result.stderr[:2000],
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"error": str(e)}
