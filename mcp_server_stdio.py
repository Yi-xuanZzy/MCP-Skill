import sys
from datetime import datetime

from mcp.server.fastmcp import FastMCP

port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
mcp = FastMCP("date-tool", host="127.0.0.1", port=port)


@mcp.tool()
def get_current_date() -> str:
    """获取今天的日期（本地时区），格式 YYYY-MM-DD。"""
    return datetime.now().strftime("%Y-%m-%d")


@mcp.tool()
def get_current_time() -> str:
    """获取当前时间（本地时区），格式 HH:MM:SS。"""
    return datetime.now().strftime("%H:%M:%S")


if __name__ == "__main__":
    # 默认 stdio；传参可复用同一个文件启动网络模式：
    # python mcp_server_stdio.py sse
    # python mcp_server_stdio.py streamable-http
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    mcp.run(transport=transport)
