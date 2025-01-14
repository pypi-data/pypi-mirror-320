from ..manifest import ParameterTypeEnum, ToolManifest, ToolParameter


class LinkReader(ToolManifest):
    def __init__(self) -> None:
        super().__init__(
            action_name="LinkReader",
            tool_name="LinkReader",
            description="当你需要获取网页、pdf、抖音视频内容时，使用此工具。"
            + "可以获取url链接下的标题和内容。\n\n"
            + 'examples: {"url_list":["abc.com", "xyz.com"]}',
            parameters=[
                ToolParameter(
                    name="url_list",
                    description="需要解析网页链接,最多3个,以列表返回",
                    param_type=ParameterTypeEnum.ARRAY,
                    items=[
                        ToolParameter(
                            param_type=ParameterTypeEnum.STRING,
                            required=True,
                        )
                    ],
                    required=True,
                )
            ],
        )
