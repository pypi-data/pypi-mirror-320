import logging
from pathlib import Path
from typing import Sequence
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.session import ServerSession
from mcp.server.stdio import stdio_server
from mcp.types import ClientCapabilities, TextContent, ImageContent, EmbeddedResource, Tool, ListRootsResult, RootsCapability, Prompt, Resource, CallToolResult
from enum import Enum
from pydantic import BaseModel
import httpx
from mcp.server.models import InitializationOptions
import asyncio
import mcp.types as types
import json
from mcp.types import JSONRPCMessage, JSONRPCRequest

logger = logging.getLogger(__name__)

class CreateMeetingInput(BaseModel):
    topic: str
    agenda: str
    start_time: str
    duration: int
    password: str | None = None
    type: int = 2


class ZoomTools(str, Enum):
    CREATE_MEETING = "create_meeting"

ZOOM_API_BASE_URL = "https://zoomdev.us/v2"

async def create_zoom_meeting(user_id: str, meeting_details: dict, access_token: str) -> dict:
    logger.info(f"Starting to create Zoom meeting for user_id: {user_id} with details: {meeting_details}")
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        url = f"{ZOOM_API_BASE_URL}/users/{user_id}/meetings"
        logger.debug(f"POST {url} with headers {headers}")
        response = await client.post(url, headers=headers, json=meeting_details)

        if response.status_code == 201:
            logger.info(f"Meeting created successfully for user_id: {user_id}")
            return response.json()
        else:
            logger.error(f"Failed to create meeting: {response.status_code} - {response.text}")
            raise ValueError(f"Zoom API error: {response.status_code} - {response.text}")

async def serve(config: dict) -> Server:
    logger.info("Initializing MCP Zoom Server")
    access_token = config["access_token"]
    logger.info(f"Access Tokne: {access_token}")
    server = Server("zoom")

    @server.progress_notification()
    async def handle_progress(
       progress_token: str | int, progress: float, total: float | None
    ) -> None:
        logger.info(f"handle progress {progress_token} -  {progress} -  {total}")

    async def request_handlers(request: dict) -> dict:
        logger.info(f"Received raw request: {request}")
        return {"status": "ok"}

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        logger.info("Listing available tools")
        tools = [
            Tool(
                name=ZoomTools.CREATE_MEETING,
                description="Create a new Zoom meeting",
                inputSchema= {
                    "type": "object",
                    "properties": {
                        "agenda": {
                            "type": "string",
                            "description": "Meeting agenda"
                        },
                        "topic": {
                            "type": "string",
                            "description": "Meeting topic"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Meeting start time"
                        },
                        "duration": {
                            "type": "int",
                            "description": "Meeting duration"
                        },
                        "password": {
                            "type": "string",
                            "description": "Meeting password"
                        }
                    },
                    "required": ["agenda", "topic", "start_time", "duration"]
                },
            ),
        ]
        logger.debug(f"Tools listed: {tools}")
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict | None) -> list[TextContent | ImageContent | EmbeddedResource]:
        logger.info(f"Tool called: {name} with arguments: {arguments}")
        match name:
            case ZoomTools.CREATE_MEETING:
                meeting_details = {
                    "topic": arguments["topic"],
                    "agenda": arguments["agenda"],
                    "start_time": arguments["start_time"],
                    "duration": arguments["duration"],
                    "password": arguments.get("password"),
                    "type": 2
                }
                try:
                    result = await create_zoom_meeting(
                        config["user_id"],
                        meeting_details,
                        access_token,
                    )
                    logger.info(f"Tool {name} executed successfully, response is {result}")
                    return [TextContent(
                        type="text",
                        text=f"Meeting created successfully. Join URL: {result['join_url']}"
                    )]
                except Exception as e:
                    logger.error(f"Error executing tool {name}: {e}")
                    return [TextContent(
                        type="text",
                        text=f"Error: {str(e)}"
                    )]
            case _:
                logger.error(f"Unknown tool called: {name}")
                raise ValueError(f"Unknown tool: {name}")

    return server

def main(config: dict):
    async def _run():
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server is running...")

            server = await serve(config)
            queue = asyncio.Queue()

            class QueueStream:
                def __init__(self, queue: asyncio.Queue):
                    self.queue = queue

                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    pass

                async def __aiter__(self):
                    while True:
                        data = await self.queue.get()
                        if data is None:  # Queue end flag
                            break
                        yield data

            async def capture_and_forward():
                """Catch from read_stream and redirect to the queue"""
                async for raw_data in read_stream:
                    try:
                        if isinstance(raw_data, JSONRPCMessage):
                            logger.info(f"Received JSONRPCMessage: {raw_data}")
                        else:
                            logger.warning(f"Unknown data type received: {type(raw_data)}")
                        # Put data into queue
                        await queue.put(raw_data)
                    except Exception as e:
                        logger.error(f"Failed to process raw data: {e}")
                # Close queue
                await queue.put(None)

            async def run_server():
                """Read from queue and transfer to server.run"""
                async with QueueStream(queue) as stream:
                    await server.run(
                        stream,
                        write_stream,
                        InitializationOptions(
                            server_name="zoom",
                            server_version="0.0.1",
                            capabilities=server.get_capabilities(
                                notification_options=NotificationOptions(),
                                experimental_capabilities={},
                            ),
                        ),
                        raise_exceptions=True,
                    )
                    logger.info("Server finished processing requests")

            # Run catcher and MCP Server
            await asyncio.gather(capture_and_forward(), run_server())

    asyncio.run(_run())

    ##options = server.create_initialization_options()
    ##async with stdio_server() as (read_stream, write_stream):
    ##    logger.info("Starting server event loop")
    ##    ##await server.run(read_stream, write_stream, options, raise_exceptions=True)
    ##    await server.run(
    ##        read_stream,
    ##        write_stream,
    ##        InitializationOptions(
    ##            server_name="zoom",
    ##            server_version="0.0.1",
    ##            capabilities=server.get_capabilities(
    ##                notification_options=NotificationOptions(),
    ##                experimental_capabilities={},
    ##            ),
    ##        ),
    ##    )
    ##    logger.info("Server event loop terminated")
