# 요구사항

- `>= python3.10`
- `>= pip23.0.1`
- `discord`
- `telegram`
- `venv`


# venv 세팅

```bash
python3 -m venv discordbot
```


# 패키지 설치

```bash
source discordbot/bin/activate
discordbot/bin/pip3 install discord
discordbot/bin/pip3 install python-telegram-bot --upgrade
deactivate
```


# 실행
```bash
./start.sh
```