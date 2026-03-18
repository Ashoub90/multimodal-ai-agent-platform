import time
import json
import logging

# Standard logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-agent")

def log_event(event_type: str, data: dict):
    """
    Structured logging for tracking AI agent performance and latency.
    """
    event = {
        "event": event_type,
        "timestamp": time.time(),
        **data
    }
    
    # This prints it to your terminal in a structured way
    # In a real production app, this would go to ELK, Datadog, or a file
    print(json.dumps(event))

def setup_logging():
    logging.info("Observability system initialized.")