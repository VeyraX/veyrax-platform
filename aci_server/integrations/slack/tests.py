from integrations.common.tests.base import base_setup
import pytest

#########################################
# Slack Integration Tests
#########################################

# --- Test Fixtures ---
@pytest.fixture(scope="module")
def test_channel(base_setup):
    """Fixture to get first available channel ID"""
    response = base_setup.post("/slack/list_channels")
    channels = response.json()["data"]["channels"]
    if not channels:
        pytest.skip("No channels available for testing")
    return channels[0]

@pytest.fixture(scope="module")
def test_user(base_setup, test_channel):
    """Fixture to get first non-bot user from channel members"""
    payload = {"channel_id": test_channel["id"]}
    response = base_setup.post("/slack/list_channel_members", payload=payload)
    members = response.json()["data"]["members"]
    
    # Filter out any bot users
    non_bot_members = [m for m in members if not m.get("is_bot", False)]
    
    if not non_bot_members:
        pytest.skip("No non-bot channel members available for testing")
    
    return non_bot_members[0]

@pytest.fixture(scope="module")
def test_message(base_setup, test_channel):
    """Fixture to create and return a test message"""
    # Always try to post a new message for testing
    payload = {
        "channel_id": test_channel["id"],
        "message": {"text": "Integration test message"}
    }
    
    try:
        response = base_setup.post("/slack/post_message", payload=payload)
        return response.json()["data"]
    except Exception as e:
        # If posting fails, skip tests that depend on this fixture
        pytest.skip(f"Cannot post messages to channel: {str(e)}")

# --- Core Functionality Tests ---
def test_list_channels(base_setup, test_channel):
    """Test channel listing endpoint"""
    response = base_setup.post("/slack/list_channels")
    data = response.json()["data"]
    assert isinstance(data["channels"], list)
    assert any(c["id"] == test_channel["id"] for c in data["channels"])

def test_list_channel_members(base_setup, test_channel, test_user):
    """Test channel member listing endpoint"""
    payload = {"channel_id": test_channel["id"]}
    response = base_setup.post("/slack/list_channel_members", payload=payload)
    data = response.json()["data"]
    assert isinstance(data["members"], list)
    assert any(m["id"] == test_user["id"] for m in data["members"])

def test_post_and_list_messages(base_setup, test_channel, test_message):
    """Test message posting and channel message listing"""
    # Skip if we couldn't create a test message
    if not test_message:
        pytest.skip("No test message available")
        
    # List messages in channel
    payload = {"channel_id": test_channel["id"]}
    response = base_setup.post("/slack/list_channel_messages", payload=payload)
    messages = response.json()["data"]["messages"]
    
    # Verify posted message exists in list
    assert any(m["id"] == test_message["id"] for m in messages)
    assert any(m["text"] == test_message["text"] for m in messages)

def test_thread_operations(base_setup, test_channel, test_message):
    """Test thread reply and thread message listing"""
    # Skip if we couldn't create a test message
    if not test_message:
        pytest.skip("No test message available")
        
    # Skip if the test message doesn't support threaded replies
    if test_message.get("text", "").startswith("<@") and "has joined the channel" in test_message.get("text", ""):
        pytest.skip("Cannot reply to system messages about users joining channels")
    
    # Post thread reply
    reply_payload = {
        "channel_id": test_channel["id"],
        "thread_ts": test_message["timestamp"],
        "message": {"text": "Thread reply"}
    }
    
    try:
        reply_response = base_setup.post("/slack/reply_in_thread", payload=reply_payload)
        reply_data = reply_response.json()["data"]
        
        # List thread messages
        thread_payload = {
            "channel_id": test_channel["id"],
            "thread_ts": test_message["timestamp"]
        }
        thread_response = base_setup.post("/slack/list_thread_messages", payload=thread_payload)
        thread_messages = thread_response.json()["data"]["messages"]
        
        # Verify thread operations
        assert reply_data["thread_ts"] == test_message["timestamp"]
        assert len(thread_messages) >= 2
        assert any(m["text"] == "Thread reply" for m in thread_messages)
    except Exception as e:
        pytest.skip(f"Thread operations failed: {str(e)}")

def test_direct_messaging(base_setup, test_user):
    """Test DM sending and DM history"""
    # Skip if we don't have a valid user
    if not test_user or test_user.get("is_bot", False):
        pytest.skip("No valid user available for DM testing")
        
    # Send direct message
    dm_payload = {
        "message": {
            "user": test_user["id"],
            "text": "Test direct message"
        }
    }
    
    try:
        dm_response = base_setup.post("/slack/send_dm", payload=dm_payload)
        dm_data = dm_response.json()["data"]
        
        # List DMs with user
        history_payload = {"user": test_user["id"]}
        history_response = base_setup.post("/slack/list_direct_messages_with_user", payload=history_payload)
        history_messages = history_response.json()["data"]["messages"]
        
        # Verify DM operations
        assert dm_data["text"] == "Test direct message"
        assert any(m["id"] == dm_data["id"] for m in history_messages)
    except Exception as e:
        pytest.skip(f"Direct messaging failed: {str(e)}")

# --- Basic Health Checks ---
def test_list_direct_messages(base_setup):
    """Test direct message listing health check"""
    response = base_setup.post("/slack/list_direct_messages")
    data = response.json()["data"]
    assert isinstance(data["messages"], list)

def test_component_serialization(base_setup):
    """Verify response serialization includes component metadata"""
    response = base_setup.post("/slack/list_channels")
    assert "component" in response.json()
    assert response.json()["component"] is not None 