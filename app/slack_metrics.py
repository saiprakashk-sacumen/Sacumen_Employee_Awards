# app/slack_metrics.py
import os
import requests
from datetime import datetime
from prometheus_client import Gauge



SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CHANNELS = ["C09AJPQAYCT"]  # Add more if needed

START_DATE = datetime(2025, 8, 1)
END_DATE = datetime(2025, 8, 31, 23, 59, 59)
START_TS = START_DATE.timestamp()
END_TS = END_DATE.timestamp()

POSITIVE_KEYWORDS = ["thanks", "great", "awesome", "good job", "well done", "nice", "appreciate"]

# Prometheus Gauges
slack_messages = Gauge("slack_messages_total", "Total Slack messages per user", ["user"])
slack_reactions = Gauge("slack_reactions_total", "Total Slack reactions per user", ["user"])
slack_mentions = Gauge("slack_mentions_total", "Total Slack mentions per user", ["user"])
slack_active_minutes = Gauge("slack_active_minutes_total", "Total active minutes per user", ["user"])
slack_positive_msgs = Gauge("slack_positive_messages_total", "Total positive messages per user", ["user"])

def get_all_users():
    url = "https://slack.com/api/users.list"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    params = {"limit": 200}
    users = {}
    next_cursor = None
    while True:
        if next_cursor:
            params["cursor"] = next_cursor
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        if not data.get("ok"):
            print("Error fetching users:", data.get("error"))
            break
        for member in data.get("members", []):
            user_id = member.get("id")
            real_name = member.get("real_name", member.get("name"))
            if not member.get("is_bot") and not member.get("deleted"):
                users[user_id] = real_name
        next_cursor = data.get("response_metadata", {}).get("next_cursor")
        if not next_cursor:
            break
    return users

def get_user_activity(user_id):
    # Same logic as your get_user_activity function, but simplified to update Gauges
    metrics = {"messages": 0, "reactions": 0, "mentions": 0, "active_minutes": 0, "positive_msgs": 0}
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    timestamps = []

    for channel_id in CHANNELS:
        url = "https://slack.com/api/conversations.history"
        params = {"channel": channel_id, "limit": 200, "oldest": START_TS, "latest": END_TS}
        next_cursor = None
        while True:
            if next_cursor:
                params["cursor"] = next_cursor
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            if not data.get("ok"):
                print(f"Error fetching messages for {user_id}:", data.get("error"))
                break
            for msg in data.get("messages", []):
                if msg.get("user") == user_id:
                    metrics["messages"] += 1
                    timestamps.append(float(msg["ts"]))
                    text = msg.get("text", "").lower()
                    if any(word in text for word in POSITIVE_KEYWORDS):
                        metrics["positive_msgs"] += 1
                for reaction in msg.get("reactions", []):
                    if user_id in reaction.get("users", []):
                        metrics["reactions"] += 1
                if f"<@{user_id}>" in msg.get("text", ""):
                    metrics["mentions"] += 1
            next_cursor = data.get("response_metadata", {}).get("next_cursor")
            if not next_cursor:
                break

    # Calculate active minutes
    daily_activity = {}
    for ts in timestamps:
        day = datetime.fromtimestamp(ts).date()
        if day not in daily_activity:
            daily_activity[day] = {"start": ts, "end": ts}
        else:
            daily_activity[day]["start"] = min(daily_activity[day]["start"], ts)
            daily_activity[day]["end"] = max(daily_activity[day]["end"], ts)
    total_minutes = sum((v["end"] - v["start"]) / 60 for v in daily_activity.values())
    metrics["active_minutes"] = int(total_minutes)

    # Update Prometheus Gauges
    user_label = user_id
    slack_messages.labels(user=user_label).set(metrics["messages"])
    slack_reactions.labels(user=user_label).set(metrics["reactions"])
    slack_mentions.labels(user=user_label).set(metrics["mentions"])
    slack_active_minutes.labels(user=user_label).set(metrics["active_minutes"])
    slack_positive_msgs.labels(user=user_label).set(metrics["positive_msgs"])
