# MCP Client Demo

一个最小可跑的 [MCP（Model Context Protocol）](https://modelcontextprotocol.io/) 示例：用 Python 写一个本地 MCP 服务端，再通过 LangChain Agent 调用它的工具。

## 文件说明

| 文件 | 作用 |
|---|---|
| `mcp_server_stdio.py` | MCP 服务端，提供 `get_current_date`、`get_current_time` 两个工具，支持 stdio / SSE / Streamable HTTP 三种传输 |
| `MCP_client.py` | MCP 客户端，通过 `MultiServerMCPClient` 连接服务端，把工具交给 Agent 调用 |

## 环境要求

- Python 3.10+
- 一个 [DashScope](https://dashscope.aliyuncs.com/) API Key（示例使用通义千问 `qwen-plus`，可改成其他兼容 OpenAI 协议的模型）

## 安装

```bash
pip install -r requirements.txt
```

配置模型 API Key（不要写进代码）：

```bash
# Linux / macOS
export DASHSCOPE_API_KEY="你的 key"

# Windows PowerShell
$env:DASHSCOPE_API_KEY="你的 key"
```

## 启动服务端

按传输方式选择，三种可以只选一种：

```bash
# stdio：无需手动启动，客户端会自动拉起子进程
python mcp_server_stdio.py

# SSE（旧版协议），监听 http://127.0.0.1:8000/sse
python mcp_server_stdio.py sse 8000

# Streamable HTTP（新版协议），监听 http://127.0.0.1:8001/mcp
python mcp_server_stdio.py streamable-http 8001
```

## 运行客户端

```bash
python MCP_client.py
```

客户端默认连接 stdio 和 Streamable HTTP 两个服务。如果只用 stdio，把 `MCP_client.py` 里 `date-tool-streamable` 那一行注释掉即可；使用 SSE 则取消 `date-tool-sse` 的注释。

预期输出：Agent 自动调用 `get_current_date` 工具，并打印工具调用参数、返回值和最终回答。

## 三种传输方式的区别

| 传输 | 说明 |
|---|---|
| `stdio` | 客户端启动子进程，通过标准输入输出通信，适合本地工具 |
| `sse` | 旧版 HTTP 传输（2024-11 规范），长连接事件流 + POST 回传，已弃用但兼容 |
| `streamable_http` | 新版 HTTP 传输（2025-03 规范），单端点，需要流式时再升级为 SSE，推荐使用 |

## License

[MIT](LICENSE)
