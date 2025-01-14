# SDK介绍

## SDK定义
ai-app-lab  是方舟高代码智能体 SDK，面向具有专业开发能力的企业开发者，提供智能体开发需要用到的工具集和流程集。 包括丰富的插件库与大模型应用落地所需的工具链以及应用代码示例，可进行高定制化与高自由度的智能体应用开发，并支持火山引擎 veFaaS 部署服务，帮助其与云上资源和产品更好的打通，赋能大模型在各行业场景的落地应用。

## 框架优势
- **高度定制化：** 提供高代码智能体编排方式，灵活服务客户高度定制化和自定义需求，赋能大模型的落地应用。
- **丰富优质的业务工具：** 方舟基于各方项目交付的最佳实践沉淀以及企业开发者经验，面向企业客户提供高质量、有保障的业务工具，包括丰富的业务插件库与工具链，支持与先进的大模型进行组合串联，最终实现一个解决端到端解决问题的智能体应用。
- **开放的生态环境：** 方舟平台致力于构建一个底层充分开放的大模型生态，通过 SDK（软件开发工具包）企业开发者可轻松进行二次开发和定制，以满足行业业务场景的特定需求。
- **一站式开发与托管服务：** 简化智能体部署和管理的流程，增强系统的稳定性。
- **安全可靠：** 方舟提供高保障的安全措施，保证对话的安全性和保密性，无需担心数据泄漏或窃取风险。
  
## 应用场景
面向复杂的企业开发场景，搭建高定制化与自定义的智能体应用，赋能大模型在各行业场景的落地应用，实现企业智能化升级。
- **智能驾舱：** 为汽车行业用户提供车载智能交互, 包括角色扮演、聊天、联网查询（天气、视频、新闻等）、车机能力唤起等多功能的融合编排使用。
- **金融服务：** 为金融行业用户提供智能投顾、风险评估等服务，提升金融服务的效率和客户满意度。
- **电商库存管理：** 为电商行业提供高效的库存管理方案。包括商品库存管理与查询、分析与预测需求，保证供应链运营的流畅性和效率。
- **办公助理：** 支持企业客户在办公场景下文档写作、会议管理、数据分析等需求。
- **行业大模型应用：** 企业可根据业务和目标进行定制和拓展。包括但不限于泛互联网、工业、政务、交通、汽车、金融等各行业场景的大模型落地应用。

## 架构设计
![image](./docs/assets/image1.jpeg)

# 支持特性
| 功能点     | 功能简介                                                           |
| ---------- | ------------------------------------------------------------------ |
| Prompt     | 渲染及模型调用简化调用模型时，prompt渲染及模型调用结果处理的流程。 |
| 插件调用   | 支持插件本地注册、插件管理及对接FC模型自动化调用。                 |
| Trace 监控 | 支持对接otel协议的trace管理及上报。                                |

# 应用列表

| 应用名称                                                    | 应用简介                                                     |
| ----------------------------------------------------------- | ------------------------------------------------------------ |
| [互动双语视频生成器](demohouse/live_voice_call/README.md)   | 只需输入一个主题，就能为你生成引人入胜且富有含义的双语视频。 |
| [视频实时理解](./demohouse/video_analyser/README.md)        | 多模态洞察，基于豆包-视觉理解模型实时视觉与语音理解。        |
| [语音通话-活力少女青青](./demohouse/chat2cartoon/README.md) | 嗨，我是你的朋友乔青青，快来和我语音通话吧！                 |

# 快速入门

## SDK安装
```shell
git clone https://github.com/volcengine/ai-app-lab.git
cd ai-app-lab

make install
make build
```

## 运行环境

- Python 3.9 或以上版本
- 火山 TOS AK&SK access
- 方舟模型接入点[Endpoint](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint)
  
| 环境变量        | 备注                                                                                                                                                       |
| :-------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ARK_API_KEY     | 火山方舟 API Key，用于方舟模型接入点推理时做鉴权。[参考文档](https://www.volcengine.com/docs/82379/1298459#api-key-%E7%AD%BE%E5%90%8D%E9%89%B4%E6%9D%83)。 |
| VOLC_ACCESS_KEY | 火山引擎账号 Access Key，用于访问火山相关服务。                                                                                                            |
| VOLC_SECRET_KEY | 火山引擎账号 Secret Key，火山相关服务。                                                                                                                    |


## 基础聊天

### 创建```main.py```，并添加如下代码
```python
import os
from typing import AsyncIterable, Union

from arkitect.core.component.llm import BaseChatLanguageModel

from arkitect.core.component.llm.model import (
    ArkChatCompletionChunk,
    ArkChatParameters,
    ArkChatRequest,
    ArkChatResponse,
    Response,
)
from arkitect.launcher.local.serve import launch_serve
from arkitect.telemetry.trace import task

# 请替换为您的 endpoint_id
endpoint_id = "<YOUR ENDPOINT ID>"

@task()
async def default_model_calling(
    request: ArkChatRequest,
) -> AsyncIterable[Union[ArkChatCompletionChunk, ArkChatResponse]]:
    parameters = ArkChatParameters(**request.__dict__)
    llm = BaseChatLanguageModel(
        endpoint_id=endpoint_id,
        messages=request.messages,
        parameters=parameters,
    )
    if request.stream:
        async for resp in llm.astream():
            yield resp
    else:
        yield await llm.arun()

@task()
async def main(request: ArkChatRequest) -> AsyncIterable[Response]:
    async for resp in default_model_calling(request):
        yield resp

if __name__ == "__main__":
    port = os.getenv("_FAAS_RUNTIME_PORT")
    launch_serve(
        package_path="main",
        port=int(port) if port else 8080,
        health_check_path="/v1/ping",
        endpoint_path="/api/v3/bots/chat/completions",
        clients={},
    )

```

### 启动应用服务
```shell
export ARK_API_KEY=<YOUR APIKEY>
python3 main.py
```

### 发起请求
```shell
curl --location 'http://localhost:8080/api/v3/bots/chat/completions' \
--header 'Content-Type: application/json' \
--data '{
    "model": "my-bot",
    "messages": [
        {
            "role": "user",
            "content": "介绍你自己啊"
        }
    ],
    "stream": true
}'
```

## 插件调用

### 创建```main.py```，并添加如下代码
```python
import os
from typing import AsyncIterable, Union

from arkitect.core.component.llm import BaseChatLanguageModel

from arkitect.core.component.llm.model import (
    ArkChatCompletionChunk,
    ArkChatParameters,
    ArkChatRequest,
    ArkChatResponse,
    ChatCompletionTool,
    FunctionDefinition,
    Response,
)
from arkitect.core.component.tool.manifest import ToolManifest
from arkitect.core.component.tool.pool import ToolPool
from arkitect.launcher.local.serve import launch_serve
from arkitect.telemetry.trace import task

# 请替换为您的 endpoint_id
endpoint_id = "<YOUR ENDPOINT ID>"

def tool_to_chat_completion_tool(item: ToolManifest) -> ChatCompletionTool:
    tool_manifest = item.manifest()
    return ChatCompletionTool(
        type="function",
        function=FunctionDefinition(
            name="calculator",
            description=tool_manifest['description'],
            parameters=tool_manifest['parameters'],
        )
    )

@task()
async def default_model_calling(
    request: ArkChatRequest,
) -> AsyncIterable[Union[ArkChatCompletionChunk, ArkChatResponse]]:
    parameters = ArkChatParameters(**request.__dict__)
    calculator_tool = ToolPool.get("Calculator", "Calculator")
    
    parameters.tools = [
        tool_to_chat_completion_tool(calculator_tool),
    ]

    print(calculator_tool.manifest())

    llm = BaseChatLanguageModel(
        endpoint_id=endpoint_id,
        messages=request.messages,
        parameters=parameters,
    )
    if request.stream:
        async for resp in llm.astream(functions={"calculator": calculator_tool}):
            yield resp
    else:
        yield await llm.arun(functions={"calculator": calculator_tool})

@task()
async def main(request: ArkChatRequest) -> AsyncIterable[Response]:
    async for resp in default_model_calling(request):
        yield resp

if __name__ == "__main__":
    port = os.getenv("_FAAS_RUNTIME_PORT")
    launch_serve(
        package_path="main",
        port=int(port) if port else 8080,
        health_check_path="/v1/ping",
        endpoint_path="/api/v3/bots/chat/completions",
        clients={},
    )
```
### 启动应用服务
```shell
export ARK_API_KEY=<YOUR APIKEY>
python3 main.py
```

### 发起请求
```shell
curl --location 'http://localhost:8080/api/v3/bots/chat/completions' \
--header 'Content-Type: application/json' \
--data '{
    "model": "my-bot",
    "messages": [
        {
            "role": "user",
            "content": "老王要养马,他有这样一池水:如果养马30匹,8天可可以把水喝光;如果养马25匹,12天把水喝光。老王要养马23匹,那么几天后他要为马找水喝?"
        }
    ],
    "stream": true
}'
```

# 常见问题
## ai-app-lab 和 volcenginesdkarkruntime 的区别?
- ai-app-lab 是方舟高代码智能体 SDK，面向具有专业开发能力的企业开发者，提供智能体开发需要用到的工具集和流程集。 
- volcenginesdkarkruntime 是对方舟的 API 进行封装，方便用户通过 API 创建、管理和调用大模型相关服务。