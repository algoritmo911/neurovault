import pytest
import json
from unittest.mock import patch, AsyncMock

# The module to test
from services.novelty_agent import main as novelty_agent_main

@pytest.fixture
def mock_nats_client():
    """Fixture to provide a mock NATS client."""
    nc = AsyncMock()
    nc.publish = AsyncMock()
    return nc

@pytest.fixture
def mock_llm():
    """Fixture to mock the LLM call."""
    with patch("services.novelty_agent.main.generate_hypothesis") as mock_generate:
        mock_generate.return_value = "This is a test hypothesis."
        yield mock_generate

@pytest.mark.asyncio
async def test_message_handler_success(mock_nats_client, mock_llm):
    """
    Tests the successful processing of a message, including LLM call and hypothesis publishing.
    """
    # Arrange
    source_event_id = "event-123"
    text_content = "Some novel text content."
    event_data = {
        "id": source_event_id,
        "metadata": {
            "text": text_content
        }
    }

    # Create a mock message object
    mock_msg = AsyncMock()
    mock_msg.subject = "event.type.novel"
    mock_msg.data = json.dumps(event_data).encode('utf-8')

    # Create the handler instance with the mock NATS client
    handler = novelty_agent_main.create_message_handler(mock_nats_client)

    # Act
    await handler(mock_msg)

    # Assert
    # 1. Check that the LLM was called with the correct text
    mock_llm.assert_awaited_once_with(text_content)

    # 2. Check that the new hypothesis was published
    mock_nats_client.publish.assert_awaited_once()

    # 3. Check the content of the published message
    call_args = mock_nats_client.publish.call_args[0]
    published_subject = call_args[0]
    published_payload = json.loads(call_args[1].decode('utf-8'))

    assert published_subject == novelty_agent_main.HYPOTHESIS_SUBJECT
    assert published_payload["source_event_id"] == source_event_id
    assert "test hypothesis" in published_payload["hypothesis_text"]
