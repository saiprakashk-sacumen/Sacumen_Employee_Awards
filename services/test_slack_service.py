# test_slack_service.py
import asyncio
import os
from datetime import datetime, timedelta
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleSlackTest:
    def __init__(self):
        self.token = os.getenv("SLACK_BOT_TOKEN")
        if not self.token:
            raise ValueError("SLACK_BOT_TOKEN not found in environment variables")
        
        self.client = AsyncWebClient(token=self.token)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        print(f"🚀 Initialized Slack client with token: {self.token[:12]}...")

    async def test_connection(self):
        """Test basic Slack connection"""
        print("\n1️⃣  Testing Slack Connection...")
        try:
            response = await self.client.auth_test()
            print(f"   ✅ Connected successfully!")
            print(f"   📱 Bot Name: {response.get('user', 'Unknown')}")
            print(f"   🆔 Bot User ID: {response.get('user_id', 'Unknown')}")
            print(f"   🏢 Team: {response.get('team', 'Unknown')}")
            return True
        except SlackApiError as e:
            print(f"   ❌ Connection failed: {e.response['error']}")
            return False

    async def test_get_users(self):
        """Test getting user list"""
        print("\n2️⃣  Testing User List...")
        try:
            response = await self.client.users_list(limit=10)
            users = []
            for user in response["members"]:
                if not user.get("deleted", False) and not user.get("is_bot", False):
                    users.append({
                        "id": user["id"],
                        "name": user.get("real_name", user.get("name", "Unknown")),
                        "email": user.get("profile", {}).get("email", "No email")
                    })
            
            print(f"   ✅ Found {len(users)} active users")
            for i, user in enumerate(users[:3], 1):
                print(f"   {i}. {user['name']} - {user['email']} (ID: {user['id']})")
            
            # Return first user for further testing
            return users[0] if users else None
            
        except SlackApiError as e:
            print(f"   ❌ Failed to get users: {e.response['error']}")
            return None

    async def test_get_channels(self):
        """Test getting channel list"""
        print("\n3️⃣  Testing Channel List...")
        try:
            response = await self.client.conversations_list(
                types="public_channel,private_channel",
                exclude_archived=True,
                limit=10
            )
            
            channels = response.get("channels", [])
            print(f"   ✅ Found {len(channels)} channels")
            
            for i, channel in enumerate(channels[:3], 1):
                member_count = channel.get("num_members", "Unknown")
                print(f"   {i}. #{channel['name']} - {member_count} members (ID: {channel['id']})")
            
            return channels[0] if channels else None
            
        except SlackApiError as e:
            print(f"   ❌ Failed to get channels: {e.response['error']}")
            return None

    async def test_channel_messages(self, channel_id, channel_name):
        """Test getting messages from a channel"""
        print(f"\n4️⃣  Testing Messages from #{channel_name}...")
        try:
            # Get messages from last 7 days
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)
            oldest = str(int(start_time.timestamp()))
            latest = str(int(end_time.timestamp()))
            
            response = await self.client.conversations_history(
                channel=channel_id,
                oldest=oldest,
                latest=latest,
                limit=50
            )
            
            messages = response.get("messages", [])
            user_messages = [msg for msg in messages if msg.get("type") == "message" and "user" in msg]
            
            print(f"   ✅ Found {len(user_messages)} user messages in last 7 days")
            
            if user_messages:
                # Show sample message
                sample_msg = user_messages[0]
                text = sample_msg.get("text", "")[:100] + "..." if len(sample_msg.get("text", "")) > 100 else sample_msg.get("text", "")
                print(f"   📝 Sample message: \"{text}\"")
                
                # Test sentiment analysis
                if text:
                    sentiment = self.sentiment_analyzer.polarity_scores(text)
                    print(f"   😊 Sentiment score: {sentiment['compound']:.2f} (positive/negative: -1 to 1)")
            
            return user_messages
            
        except SlackApiError as e:
            print(f"   ❌ Failed to get messages: {e.response['error']}")
            return []

    async def test_user_activity(self, user_id, user_name):
        """Test getting specific user activity"""
        print(f"\n5️⃣  Testing Activity for {user_name}...")
        try:
            # Get channels user is member of
            channels_response = await self.client.conversations_list(
                types="public_channel",
                exclude_archived=True
            )
            
            user_activity = {
                "messages_sent": 0,
                "channels_active": 0,
                "reactions_received": 0
            }
            
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)
            oldest = str(int(start_time.timestamp()))
            latest = str(int(end_time.timestamp()))
            
            for channel in channels_response["channels"][:3]:  # Test first 3 channels only
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
                            limit=100
                        )
                        
                        # Count user's messages
                        user_messages = [
                            msg for msg in history_response["messages"] 
                            if msg.get("user") == user_id and msg.get("type") == "message"
                        ]
                        
                        if user_messages:
                            user_activity["channels_active"] += 1
                            user_activity["messages_sent"] += len(user_messages)
                            
                            # Count reactions received
                            for msg in user_messages:
                                if "reactions" in msg:
                                    for reaction in msg["reactions"]:
                                        user_activity["reactions_received"] += reaction["count"]
                
                except SlackApiError:
                    continue  # Skip channels we can't access
            
            print(f"   ✅ User Activity Summary:")
            print(f"      📨 Messages sent: {user_activity['messages_sent']}")
            print(f"      📢 Active channels: {user_activity['channels_active']}")
            print(f"      👍 Reactions received: {user_activity['reactions_received']}")
            
            # Calculate simple engagement score
            engagement_score = min((
                user_activity['messages_sent'] * 2 + 
                user_activity['reactions_received'] + 
                user_activity['channels_active'] * 5
            ), 100)
            
            print(f"      🎯 Engagement score: {engagement_score}/100")
            
            return user_activity
            
        except Exception as e:
            print(f"   ❌ Failed to get user activity: {e}")
            return None

    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("🔥 Starting Slack Service Tests...")
        print("=" * 50)
        
        # Test 1: Connection
        if not await self.test_connection():
            print("\n❌ Cannot proceed - connection failed!")
            return False
        
        # Test 2: Get Users
        test_user = await self.test_get_users()
        if not test_user:
            print("\n❌ Cannot proceed - no users found!")
            return False
        
        # Test 3: Get Channels
        test_channel = await self.test_get_channels()
        if not test_channel:
            print("\n⚠️  No channels found, skipping message tests")
        else:
            # Test 4: Get Messages
            await self.test_channel_messages(test_channel["id"], test_channel["name"])
        
        # Test 5: User Activity
        await self.test_user_activity(test_user["id"], test_user["name"])
        
        print("\n" + "=" * 50)
        print("🎉 All Slack tests completed!")
        print("\n💡 If all tests passed, your Slack integration is ready!")
        return True

# Test runner
async def main():
    """Main test function"""
    try:
        tester = SimpleSlackTest()
        success = await tester.run_all_tests()
        
        if success:
            print("\n✅ SUCCESS: Slack service is working correctly!")
            print("\n📋 Next steps:")
            print("   1. Your Slack bot token is valid")
            print("   2. Bot has proper permissions")
            print("   3. You can proceed with full integration")
        else:
            print("\n❌ FAILED: Please check your Slack configuration")
            print("\n🔧 Troubleshooting:")
            print("   1. Verify SLACK_BOT_TOKEN in .env file")
            print("   2. Check bot permissions in Slack app settings")
            print("   3. Ensure bot is added to your workspace")
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("\n🔧 Check your .env file and ensure SLACK_BOT_TOKEN is set")

if __name__ == "__main__":
    # Quick environment check
    if not os.getenv("SLACK_BOT_TOKEN"):
        print("❌ SLACK_BOT_TOKEN not found!")
        print("📝 Create a .env file with:")
        print("SLACK_BOT_TOKEN=xoxb-your-token-here")
    else:
        asyncio.run(main())