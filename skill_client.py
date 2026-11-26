import asyncio
import os
import re
import sys
from pathlib import Path

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

# 1. 扫描本地技能目录：每个技能一个文件夹，内含 SKILL.md
SKILLS_DIR = Path(__file__).parent / "skills"


def parse_skill(path):
    """解析 SKILL.md：--- 包裹的头部取 name/description，剩余部分作为正文"""
    text = path.read_text(encoding="utf-8")
    _, header, body = text.split("---", 2)
    name = re.search(r"^name:\s*(.+)$", header, re.MULTILINE).group(1).strip()
    description = re.search(r"^description:\s*(.+)$", header, re.MULTILINE).group(1).strip()
    return {"name": name, "description": description, "content": body.strip()}


def load_skills():
    """把 skills 目录下的技能读进内存，便于后续按名字查找"""
    skills = {}
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        skill = parse_skill(path)
        skills[skill["name"]] = skill
    return skills


SKILLS = load_skills()


# 2. 把技能清单写进系统提示，让 agent 知道有哪些技能可用
def build_system_prompt():
    lines = ["你是一个可以使用本地技能的助手。可用技能如下："]
    for skill in SKILLS.values():
        lines.append(f"- {skill['name']}：{skill['description']}")
    lines.append("需要某个技能时，先调用 load_skill 读取完整说明，再严格按说明执行。")
    return "\n".join(lines)


# 3. 技能加载工具：agent 按需读取某个技能的完整内容
@tool
def load_skill(name: str) -> str:
    """按名称加载技能的完整说明（SKILL.md 正文）。"""
    skill = SKILLS.get(name)
    if not skill:
        return f"未找到技能 {name}，可选技能：{', '.join(SKILLS)}"
    return skill["content"]


async def main():
    # 4. 把工具和系统提示交给 agent，用自然语言触发技能调用
    model = init_chat_model(
        "qwen-plus",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_provider="openai",
    )
    agent = create_agent(model, [load_skill], system_prompt=build_system_prompt())
    result = await agent.ainvoke({"messages": [("user", "用 translate 技能把“今天天气不错”翻译成英文")]})

    # 5. 验证是否真的加载并使用了技能
    for index, message in enumerate(result["messages"]):
        print(f"\n--- [{index}] {type(message).__name__} ---")
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                print("工具调用:", call["name"], call["args"], "id:", call["id"])
        if message.type == "tool":
            print("工具返回:", message.name, message.tool_call_id, "->", message.content)

    print("\n最终回答:", result["messages"][-1].content)

asyncio.run(main())
