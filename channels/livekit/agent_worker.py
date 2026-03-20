import sys
import os
import asyncio

# Path fix to find 'modalities'
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from livekit.agents import JobContext, WorkerOptions, cli
from modalities.voice.livekit_handler import get_realtime_agent
from dotenv import load_dotenv

load_dotenv()

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    # Initialize session and assistant from your handler
    session, assistant = get_realtime_agent()

    # Start the session and send the initial greeting
    await session.start(room=ctx.room, agent=assistant)
    await session.say("أهلاً بك في مطعمنا، تحب تطلب إيه النهاردة؟")

    # Keep the job alive until the participant disconnects
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint, 
        agent_name="egyptian-assistant"
    ))