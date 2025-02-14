from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio

from infrastructure.browser_use.main import BrowserUseAgent
from typing import Dict,Any
from requests import Request

app = FastAPI()

async def long_running_task(input_data:Dict[str,Any]):
    """Simulates a long-running task with real-time progress updates."""
    browser_use = BrowserUseAgent(
        credentials={'GEMINI_API_KEY':'AIzaSyB5h3jiUUr_6oGw6OBQwu0CxpMUP-VZrcg'},
        name='Test run',
        data = input_data,
        general_prompt='You are a browser automation function',
    )

    result = asyncio.run(browser_use.run(debug=True))
    yield result
    # for i in range(1, 6):
    #     await asyncio.sleep(2)  # Simulating a delay
    #     yield f"Step {i}/5 completed...\n"
    # yield "Task finished successfully!\n"
# def lg_run(input_data:Dict[str,Any]):
#     """Simulates a long-running task with real-time progress updates."""
#     browser_use = BrowserUseAgent(
#         credentials={'GEMINI_API_KEY':'AIzaSyB5h3jiUUr_6oGw6OBQwu0CxpMUP-VZrcg'},
#         name='Test run',
#         data = input_data,
#         general_prompt='You are a browser automation function',
#     )
#     asyncio.ProactorEventLoop()
#     loop = asyncio.get_running_loop()
#     task = loop.create_task(browser_use.run())
#     res = loop.run_until_complete(task)
#     print(res)
#     # result = asyncio.run(task)
#     return res
async def lg_run(input_data: Dict[str, Any]):
    """Runs the browser automation agent asynchronously."""
    browser_use = BrowserUseAgent(
        credentials={'GEMINI_API_KEY': 'AIzaSyB5h3jiUUr_6oGw6OBQwu0CxpMUP-VZrcg'},
        name='Test run',
        data=input_data,
        general_prompt='You are a browser automation function',
    )
    result = await browser_use.run()
    await browser_use.cleanup()
    return result

    # async def run_agent():
    #     result = await browser_use.run()
    #     await browser_use.cleanup()
    #     return result

    # try:
    #     loop = asyncio.get_running_loop()
    # except RuntimeError:
    #     # No running event loop, so we create one
    #     return asyncio.run(run_agent())

    # # If inside an event loop (like FastAPI), use `ensure_future`
    # task = loop.create_task(run_agent())
    # return task

@app.post("/run-task")
async def run_task(request: Dict[str,Any]):
    """Executes the long-running async function and streams responses."""
    task_description =  request.get("task_description")
    input_data =  request.get("input_data")
    result = await lg_run(input_data)

    
    # return StreamingResponse(long_running_task(input_data), media_type="text/event-stream")
    return result


