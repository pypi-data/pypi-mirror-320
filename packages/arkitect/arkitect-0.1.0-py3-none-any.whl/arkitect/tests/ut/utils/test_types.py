from arkitect.core.component.llm.model import (
    ArkChatRequest,
    ArkMessage,
    ChatCompletionMessageImageUrlPart,
    ChatCompletionMessageImageUrlPartImageUrl,
)
from arkitect.utils import dump_json_truncate


def test_dump_json():
    obj = ArkChatRequest(
        messages=[
            ArkMessage(
                role="user",
                content=[
                    ChatCompletionMessageImageUrlPart(
                        type="image_url",
                        image_url=ChatCompletionMessageImageUrlPartImageUrl(
                            url="fake-b64-url",
                        ),
                    )
                ],
            )
        ],
        model="fake-model",
    )
    obj_copied = dump_json_truncate(obj, 1)
    assert obj_copied["messages"][0]["content"][0]["image_url"]["url"] == "f"
    obj_copied = dump_json_truncate(obj, 100)
    assert obj_copied["messages"][0]["content"][0]["image_url"]["url"] == "fake-b64-url"
