import sys
import os

# Path fix to find 'modalities'
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
from livekit.agents import JobContext, WorkerOptions, cli
from modalities.voice.livekit_handler import get_realtime_agent
from dotenv import load_dotenv

load_dotenv()

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    # Get both the session and the assistant class
    session, assistant = get_realtime_agent()
    
    # FIX: Pass the agent here as a keyword argument
    await session.start(room=ctx.room, agent=assistant)
    
    # Now generate the opening greeting
    await session.say("أهلاً بك في مطعمنا، تحب تطلب إيه النهاردة؟")

if __name__ == "__main__":
    # We add an 'agent_name' here so the playground can call it explicitly
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="egyptian-assistant" 
    ))