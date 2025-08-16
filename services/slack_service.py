# services/slack_service.py
import asyncio
from datetime import datetime, timedelta
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
from typing import Dict, List, Optional

class SlackMetricsService:
    def __init__(self):
        self.client = AsyncWebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
    
    async def get_user_list(self) -> List[Dict]:
        """Get all users in the workspace"""
        try:
            response = await self.client.users_list()
            users = [] 
            for user in response["members"]:
                if not user.get("deleted", False) and not user.get("is_bot", False):
                    users.append({
                        "id": user["id"],
                        "name": user.get("real_name", user.get("name", "Unknown")),
                        "email": user.get("profile", {}).get("email", ""),
                        "display_name": user.get("profile", {}).get("display_name", "")
                    })
            return users
        except SlackApiError as e:
            print(f"Error getting users: {e.response['error']}")
            return []
    
    async def get_user_messages(self, user_id: str, days_back: int = 7) -> Dict:
        """Get user's message activity for the past N days"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        # Convert to Slack timestamp format
        oldest = str(int(start_time.timestamp()))
        latest = str(int(end_time.timestamp()))
        
        metrics = {
            "messages_sent": 0,
            "reactions_given": 0,
            "reactions_received": 0,
            "channels_active": set(),
            "sentiment_scores": [],
            "message_texts": []
        }
        
        try:
            # Get channels user is member of
            channels_response = await self.client.conversations_list(
                types="public_channel,private_channel",
                exclude_archived=True
            )
            
            for channel in channels_response["channels"]:
                try:
                    # Check if user is member
                    members_response = await self.client.conversations_members(
                        channel=channel["id"]
                    )
                    
                    if user_id in members_response["members"]:
                        # Get messages from this channel
                        history_response = await self.client.conversations_history(
                            channel=channel["id"],
                            oldest=oldest,
                            latest=latest,
                            inclusive=True
                        )
                        
                        user_messages = [
                            msg for msg in history_response["messages"] 
                            if msg.get("user") == user_id and msg.get("type") == "message"
                        ]
                        
                        if user_messages:
                            metrics["channels_active"].add(channel["id"])
                            metrics["messages_sent"] += len(user_messages)
                            
                            # Analyze sentiment
                            for msg in user_messages:
                                if "text" in msg:
                                    metrics["message_texts"].append(msg["text"])
                                    sentiment = self.sentiment_analyzer.polarity_scores(msg["text"])
                                    metrics["sentiment_scores"].append(sentiment["compound"])
                                
                                # Count reactions received
                                if "reactions" in msg:
                                    for reaction in msg["reactions"]:
                                        metrics["reactions_received"] += reaction["count"]
                        
                        # Count reactions given by user
                        for msg in history_response["messages"]:
                            if "reactions" in msg:
                                for reaction in msg["reactions"]:
                                    if user_id in reaction["users"]:
                                        metrics["reactions_given"] += 1
                
                except SlackApiError:
                    continue  # Skip channels where we don't have access
                    
        except SlackApiError as e:
            print(f"Error getting user messages: {e.response['error']}")
        
        # Calculate final metrics
        metrics["channels_active"] = len(metrics["channels_active"])
        metrics["sentiment_score"] = (
            sum(metrics["sentiment_scores"]) / len(metrics["sentiment_scores"])
            if metrics["sentiment_scores"] else 0.0
        )
        
        return metrics
    
    def calculate_engagement_score(self, metrics: Dict) -> float:
        """Calculate engagement score (0-100) based on Slack activity"""
        # Weights for different activities
        weights = {
            "messages": 0.3,
            "reactions_given": 0.2,
            "reactions_received": 0.2,
            "channels": 0.15,
            "sentiment": 0.15
        }
        
        # Normalize values (adjust thresholds based on your team's activity)
        normalized_messages = min(metrics["messages_sent"] / 20, 1.0)  # 20 messages = 100%
        normalized_reactions_given = min(metrics["reactions_given"] / 10, 1.0)
        normalized_reactions_received = min(metrics["reactions_received"] / 15, 1.0)
        normalized_channels = min(metrics["channels_active"] / 5, 1.0)  # 5 channels = 100%
        normalized_sentiment = (metrics["sentiment_score"] + 1) / 2  # Convert -1,1 to 0,1
        
        score = (
            normalized_messages * weights["messages"] +
            normalized_reactions_given * weights["reactions_given"] +
            normalized_reactions_received * weights["reactions_received"] +
            normalized_channels * weights["channels"] +
            normalized_sentiment * weights["sentiment"]
        ) * 100
        
        return round(score, 2)