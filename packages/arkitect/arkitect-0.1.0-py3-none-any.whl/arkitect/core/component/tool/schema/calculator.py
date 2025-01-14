from ..manifest import ParameterTypeEnum, ToolManifest, ToolParameter


class Calculator(ToolManifest):
    def __init__(self) -> None:
        super().__init__(
            action_name="Calculator",
            tool_name="Calculator",
            description="Evaluate a given mathematical expression",
            parameters=[
                ToolParameter(
                    name="input",
                    description="The mathematical expression in Wolfram"
                    + "Language InputForm",
                    param_type=ParameterTypeEnum.STRING,
                    required=True,
                )
            ],
        )
