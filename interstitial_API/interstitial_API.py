import asyncio
import os
import httpx
import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, StreamingResponse, FileResponse
from starlette.requests import Request

## Get destination API from environment variable or use default
#DESTINATION_API = os.environ.get("DESTINATION_API", "http://localhost:6789")

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("api")

class UnexpectedEndpointError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)

@app.exception_handler(UnexpectedEndpointError)
async def unexpected_endpoint_error_handler(request: Request, exc: UnexpectedEndpointError):
    return Response(
        content=json.dumps({
            'error': {
                'message': exc.detail,
                'type': 'invalid_request_error',
                'param': None,
                'code': None
            }
        }),
        media_type="application/json",
        status_code=exc.status_code
    )

async def send_request(client: httpx.AsyncClient, method: str, url: str, **kwargs):
    response = await client.request(method, url, **kwargs)
    content = response.json()

    if 'error' in content and 'Unexpected endpoint' in content['error']:
        raise UnexpectedEndpointError(content['error'])

    return Response(content=json.dumps(content), media_type=response.headers.get('content-type'), status_code=response.status_code)

@app.post("/v1/chat/completions")
async def chat_completions(data: dict):
    try:
        # Modify the data by adding system messages
        modified_data = add_system_messages(data)
        logger.info(f"Sending data to destination API: {modified_data}")
        
        # Create an HTTP client
        client = httpx.AsyncClient()

        # Define a generator function to stream content from the destination API
        async def content_generator():
            # Send the POST request to the destination API and stream the response
            async with client.stream('POST', f'http://localhost:6789/v1/chat/completions', json=modified_data, timeout=180.0) as response:
                logger.info(f"Received response from destination API: {response.status_code}")

                # Handle non-200 status codes
                if response.status_code != 200:
                    yield f"Error: {response.content}".encode()
                    return

                # Asynchronously iterate over the response text in chunks
                async for chunk in response.aiter_text():
                    try:
                        logger.debug(f"Received chunk from destination API: {chunk}")
                        # Yield each chunk to stream it to the client
                        yield chunk.encode()
                    except GeneratorExit:
                        # Handle client disconnection
                        logger.info("Client disconnected, closing stream.")
                        return
         # Return a StreamingResponse to stream the content to the client in real-time
        return StreamingResponse(content_generator(), media_type="text/plain")
    except asyncio.TimeoutError:
        # Handle request timeouts
        logger.error("The request to the destination API timed out.")
        return {"error": "The request timed out."}
    except Exception as e:
        # Handle other exceptions
        logger.error(f"Exception occurred: {e}")
        return {"error": str(e)}

def add_system_messages(data: dict) -> dict:
    messages = data.get('messages', [])
    if messages:
        last_user_msg_index = next(
            (i for i, msg in reversed(list(enumerate(messages))) if msg.get('role') == 'user'),
            None
        )
        if last_user_msg_index is not None:
            messages.insert(last_user_msg_index, {"content": "### Instructions:", "role": "system"})
            messages.insert(last_user_msg_index + 2, {"content": "### Response:", "role": "system"})
    return data

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

@app.get("/v1/models")
async def models():
    async with httpx.AsyncClient() as client:
        return await send_request(client, 'GET', 'http://localhost:6789/v1/models')

@app.get("/favicon.ico")
async def favicon():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get('http://localhost:6789/favicon.ico', timeout=30.0)
            # Check if the response is not empty (you may need to adjust the condition depending on the API)
            if response.status_code == 200 and response.content:
                return Response(response.content, media_type=response.headers.get('content-type'), status_code=response.status_code)
        except httpx.HTTPError:
            logger.error("Error retrieving favicon from destination API. Using local fallback.")
    
    return FileResponse("favicon.ico")
