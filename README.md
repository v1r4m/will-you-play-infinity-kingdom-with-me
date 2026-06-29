# will-you-play-infinity-kingdom-with-me
엄마 저는 커서 로맨스스캠이 될거에요! 

## 설치
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 값 채우기
```

`.env` 채우기:
- `DISCORD_USER_TOKEN` — 유저 토큰
- `ANTHROPIC_API_KEY` — https://console.anthropic.com
- `TARGET_USER_ID` — 대상 User ID (개발자 모드 → 우클릭 → ID 복사)
- `SEND_OPENER` — `true`면 봇이 먼저 오프닝 멘트 전송
- `ANTHROPIC_MODEL` — 기본 `claude-sonnet-4-6` (저렴하게: `claude-haiku-4-5-20251001`)

## 실행
```bash
python bot.py
```

## 동작
1. 로그인 후 `SEND_OPENER=true`면 대상에게 오프닝 DM 전송
   ("hey! i think i accidentally added you...")
2. 대상이 답장하면 Claude가 페르소나대로 짧고 자연스럽게 응답
3. 타이핑 인디케이터 + 길이 비례 딜레이로 사람처럼 보이게 전송

## 커스터마이징
- 말투/성격/오프닝 → `persona.py`
- 대화 기억 길이 → `bot.py`의 `MAX_HISTORY`
- 타이핑 속도 → `human_like_send()`

## example
![alt text](discord-capture-1782709817554.png)

## exploit
![alt text](discord-capture-1782709833028.png)