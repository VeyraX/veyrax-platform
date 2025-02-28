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
    """Fixture to get first user from channel members"""
    payload = {"channel_id": test_channel["id"]}
    response = base_setup.post("/slack/list_channel_members", payload=payload)
    members = response.json()["data"]["members"]
    if not members:
        pytest.skip("No channel members available for testing")
    return members[0]

@pytest.fixture(scope="module")
def test_message(base_setup, test_channel):
    """Fixture to create and return a test message"""
    payload = {
        "channel_id": test_channel["id"],
        "message": {"text": "Integration test message"}
    }
    response = base_setup.post("/slack/post_message", payload=payload)
    return response.json()["data"]

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
    # List messages in channel
    payload = {"channel_id": test_channel["id"]}
    response = base_setup.post("/slack/list_channel_messages", payload=payload)
    messages = response.json()["data"]["messages"]
    
    # Verify posted message exists in list
    assert any(m["id"] == test_message["id"] for m in messages)
    assert any(m["text"] == "Integration test message" for m in messages)

def test_thread_operations(base_setup, test_channel, test_message):
    """Test thread reply and thread message listing"""
    # Post thread reply
    reply_payload = {
        "channel_id": test_channel["id"],
        "thread_ts": test_message["timestamp"],
        "message": {"text": "Thread reply"}
    }
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

def test_direct_messaging(base_setup, test_user):
    """Test DM sending and DM history"""
    # Send direct message
    dm_payload = {
        "message": {
            "user_id": test_user["id"],
            "text": "Test direct message"
        }
    }
    dm_response = base_setup.post("/slack/send_dm", payload=dm_payload)
    dm_data = dm_response.json()["data"]
    
    # List DMs with user
    history_payload = {"user_id": test_user["id"]}
    history_response = base_setup.post("/slack/list_direct_messages_with_user", payload=history_payload)
    history_messages = history_response.json()["data"]["messages"]
    
    # Verify DM operations
    assert dm_data["text"] == "Test direct message"
    assert any(m["id"] == dm_data["id"] for m in history_messages)

# --- Basic Health Checks ---
def test_list_direct_messages(base_setup):
    """Test direct message listing health check"""
    response = base_setup.post("/slack/list_direct_messages")
    data = response.json()["data"]
    assert isinstance(data["messages"], list)

def test_component_serialization(base_setup, test_message):
    """Verify response serialization includes component metadata"""
    response = base_setup.post("/slack/list_channels")
    assert "component" in response.json()
    assert response.json()["component"] is not None 