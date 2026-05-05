import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from tools.mft import get_mft_timeline
from tools.registry import get_registry_hives, get_user_profiles
from tools.common import safe_run

app = Server("sift-mcp-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_mft_timeline",
            description="Extract MFT filesystem timeline from a disk image using fls. Returns file creation, modification, and access events. Read-only.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Full path to the EWF/E01 disk image"
                    },
                    "filter_path": {
                        "type": "string",
                        "description": "Optional path prefix to filter results e.g. Documents and Settings"
                    }
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="get_registry_hives",
            description="List available Windows registry hives from a mounted disk image. Read-only.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mount_path": {
                        "type": "string",
                        "description": "Path where the disk image is mounted e.g. /mnt/windows_mount"
                    }
                },
                "required": ["mount_path"]
            }
        ),
        Tool(
            name="get_user_profiles",
            description="List Windows user profiles from a mounted disk image. Helps identify suspect accounts. Read-only.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mount_path": {
                        "type": "string",
                        "description": "Path where the disk image is mounted e.g. /mnt/windows_mount"
                    }
                },
                "required": ["mount_path"]
            }
        ),
        Tool(
            name="get_ewf_info",
            description="Get metadata about an EWF disk image including size, hash, and acquisition details. Read-only.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Full path to the EWF/E01 disk image"
                    }
                },
                "required": ["image_path"]
            }
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_mft_timeline":
        result = get_mft_timeline(
            image_path=arguments["image_path"],
            filter_path=arguments.get("filter_path")
        )
    elif name == "get_registry_hives":
        result = get_registry_hives(mount_path=arguments["mount_path"])
    elif name == "get_user_profiles":
        result = get_user_profiles(mount_path=arguments["mount_path"])
    elif name == "get_ewf_info":
        result = safe_run(["ewfinfo", arguments["image_path"]])
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
