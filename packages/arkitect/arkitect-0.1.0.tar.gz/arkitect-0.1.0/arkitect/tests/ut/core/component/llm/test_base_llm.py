import os

from arkitect.core.component.llm import BaseChatLanguageModel
from arkitect.core.component.llm.model import ArkMessage

os.environ["ARK_API_KEY"] = "-"


def test_generate_prompts_with_additional_prompts() -> None:
    # Arrange
    messages = [
        ArkMessage(role="user", content="Hello"),
        ArkMessage(role="assistant", content="Hi there!"),
    ]
    additional_prompts = ["Welcome to the chat!", "How can I help you today?"]

    mock_chat_model = BaseChatLanguageModel(endpoint_id="123", messages=messages)
    # Act
    result = mock_chat_model.generate_prompts(
        messages, additional_system_prompts=additional_prompts
    )

    # Assert
    assert len(result) == len(messages) + len(additional_prompts)
    assert all(msg.role == "system" for msg in result[: len(additional_prompts)])
    assert all(msg.role != "system" for msg in result[len(additional_prompts) :])


def test_generate_prompts_without_template():
    # Arrange
    messages = [
        ArkMessage(role="user", content="Hello"),
        ArkMessage(role="assistant", content="Hi there!"),
    ]
    mock_chat_model = BaseChatLanguageModel(endpoint_id="123", messages=messages)
    mock_chat_model.template = None

    # Act
    result = mock_chat_model.generate_prompts(messages)

    # Assert
    assert len(result) == len(messages)


def test_generate_prompts_with_formatting() -> None:
    # Arrange
    messages = [
        ArkMessage(role="system", content="You are a helpful assistant."),
        ArkMessage(role="user", content="Hello"),
        ArkMessage(role="assistant", content="Hi there!"),
    ]
    mock_chat_model = BaseChatLanguageModel(endpoint_id="123", messages=messages)
    additional_prompts = ["Welcome to the chat!", "How can I help you today?"]

    # Act
    result = mock_chat_model.generate_prompts(
        messages, additional_system_prompts=additional_prompts
    )

    # Assert
    assert result
    assert len(result) == len(messages) + len(additional_prompts)
    assert all(msg.role == "system" for msg in result[: len(additional_prompts) + 1])
    assert all(msg.role != "system" for msg in result[len(additional_prompts) + 1 :])
