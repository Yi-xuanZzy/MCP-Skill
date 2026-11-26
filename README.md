# MCP Skill · 本地日期工具 MCP Server

一个可直接运行、可发布到 MCP 广场的开源示例项目：用 Python（FastMCP）实现本地 MCP 服务端，并通过 LangChain Agent 调用其工具。

## 项目简介

做这个项目的初衷是给 MCP 初学者一个「最小可跑」的完整链路：

- 服务端：`mcp_server_stdio.py` 用 FastMCP 提供 `get_current_date`、`get_current_time` 两个工具，一份代码支持 **stdio / SSE / Streamable HTTP** 三种传输
- 客户端：`MCP_client.py` 用 `MultiServerMCPClient` 连接服务端，把 MCP 工具自动转成 LangChain Tool 交给 Agent，用自然语言触发调用
- 无需数据库、无需外部 API，克隆下来装完依赖即可运行，适合作为 MCP 项目模板

## 文件说明

| 文件 | 作用 |
|---|---|
| `mcp_server_stdio.py` | MCP 服务端，提供日期、时间两个工具，支持三种传输 |
| `MCP_client.py` | MCP 客户端，连接服务端并驱动 LangChain Agent |
| `requirements.txt` | Python 依赖清单 |

## 部署指南

### 环境要求

- Python 3.10+
- 运行客户端需要 [DashScope](https://dashscope.aliyuncs.com/) API Key（示例使用 `qwen-plus`，可换成其他兼容 OpenAI 协议的模型）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 API Key

```bash
# Linux / macOS
export DASHSCOPE_API_KEY="你的 key"

# Windows PowerShell
$env:DASHSCOPE_API_KEY="你的 key"
```

### 启动服务端

三种传输按需选择，只跑一种即可：

```bash
# stdio：无需手动启动，客户端会自动拉起子进程
python mcp_server_stdio.py

# SSE（旧版协议），监听 http://127.0.0.1:8000/sse
python mcp_server_stdio.py sse 8000

# Streamable HTTP（新版协议），监听 http://127.0.0.1:8001/mcp
python mcp_server_stdio.py streamable-http 8001
```

### 客户端配置（Cherry Studio / Claude Desktop 等）

stdio 方式：

```json
{
  "mcpServers": {
    "date-tool": {
      "command": "python",
      "args": ["/绝对路径/mcp_server_stdio.py"]
    }
  }
}
```

远程方式：

```json
{
  "mcpServers": {
    "date-tool": {
      "url": "http://127.0.0.1:8001/mcp"
    }
  }
}
```

### 运行示例客户端

```bash
python MCP_client.py
```

默认连接 stdio 与 Streamable HTTP 两个服务；只用 stdio 时注释掉 `MCP_client.py` 中 `date-tool-streamable` 那一行即可，SSE 则取消 `date-tool-sse` 的注释。

## 使用示例

向 Agent 提问「今天几号？」后，实际输出：

```text
--- [0] HumanMessage ---

--- [1] AIMessage ---
工具调用: get_current_date {} id: call_19251a6c7c0b40ad8468cd

--- [2] ToolMessage ---
工具返回: get_current_date call_19251a6c7c0b40ad8468cd -> [{'type': 'text', 'text': '2026-11-26', ...}]

--- [3] AIMessage ---

最终回答: 今天是2026年11月26日。
```

工具清单：

| 工具名 | 说明 | 返回示例 |
|---|---|---|
| `get_current_date` | 获取本地时区当天日期 | `2026-11-26` |
| `get_current_time` | 获取本地时区当前时间 | `15:24:51` |

## 三种传输方式对比

| 传输 | 说明 |
|---|---|
| `stdio` | 客户端启动子进程，通过标准输入输出通信，适合本地工具 |
| `sse` | 旧版 HTTP 传输（2024-11 规范），长连接事件流 + POST 回传，已弃用但兼容 |
| `streamable_http` | 新版 HTTP 传输（2025-03 规范），单端点，需要流式时再升级为 SSE，推荐使用 |

## 开源协议

[MIT](LICENSE)
