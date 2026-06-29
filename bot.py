"""AI 친구 만들기 디스코드 셀프봇.

대상에게 먼저 가벼운 오프닝을 보내고, DM으로 오는 답장에 Claude가 자연스럽게
대화하며 친해진다. (스캠/앱 설치 유도 없음 — persona.py 참고)

주의: 유저 토큰 셀프봇은 Discord ToS 위반이라 계정 정지 위험이 있음.
테스트 전용 계정에서만 사용할 것.
"""

import asyncio
import os

import anthropic
import discord
from dotenv import load_dotenv

import persona

load_dotenv()

DISCORD_USER_TOKEN = os.environ["DISCORD_USER_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TARGET_USER_ID = int(os.environ["TARGET_USER_ID"])
SEND_OPENER = os.getenv("SEND_OPENER", "true").lower() == "true"
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# 대화 맥락을 짧게 유지 (최근 N개 메시지)
MAX_HISTORY = 20

claude = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
client = discord.Client()

# user_id -> [{"role": "user"/"assistant", "content": "..."}]
history: dict[int, list[dict]] = {}


async def generate_reply(user_id: int, user_message: str) -> str:
    """Claude로 다음 답장을 생성한다."""
    convo = history.setdefault(user_id, [])
    convo.append({"role": "user", "content": user_message})
    convo[:] = convo[-MAX_HISTORY:]  # 최근 것만 유지

    resp = await claude.messages.create(
        model=MODEL,
        max_tokens=300,
        system=persona.SYSTEM_PROMPT,
        messages=convo,
    )
    reply = "".join(block.text for block in resp.content if block.type == "text").strip()
    convo.append({"role": "assistant", "content": reply})
    return reply


async def human_like_send(channel, text: str):
    """사람처럼 보이도록 타이핑 인디케이터 + 약간의 딜레이 후 전송."""
    delay = min(len(text) * 0.08, 12.0)  # 길이에 비례한 '타이핑' 시간 (최대 6초)
    async with channel.typing():
        await asyncio.sleep(delay)
    await channel.send(text)


@client.event
async def on_ready():
    print(f"로그인됨: {client.user} (id={client.user.id})")
    if SEND_OPENER:
        try:
            user = await client.fetch_user(TARGET_USER_ID)
            dm = user.dm_channel or await user.create_dm()
            await human_like_send(dm, persona.OPENER)
            history.setdefault(TARGET_USER_ID, []).append(
                {"role": "assistant", "content": persona.OPENER}
            )
            print(f"오프닝 전송 완료 → {user}")
        except Exception as e:
            print(f"오프닝 전송 실패: {e}")


@client.event
async def on_message(message):
    # 자기 자신이 보낸 메시지는 무시
    if message.author.id == client.user.id:
        return
    # DM이 아니거나 대상이 아니면 무시
    if not isinstance(message.channel, discord.DMChannel):
        return
    if message.author.id != TARGET_USER_ID:
        return
    if not message.content.strip():
        return

    try:
        reply = await generate_reply(message.author.id, message.content)
        await human_like_send(message.channel, reply)
    except Exception as e:
        print(f"답장 생성/전송 실패: {e}")


if __name__ == "__main__":
    client.run(DISCORD_USER_TOKEN)
