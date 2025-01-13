# analytics.py
from datetime import datetime

analytics_data = {}

def log_command_usage(command_name: str, user_id: int):
    now = datetime.now().isoformat()
    analytics_data.setdefault(command_name, []).append({"user_id": user_id, "timestamp": now})

def generate_statistics():
    return analytics_data
