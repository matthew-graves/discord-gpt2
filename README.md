# discord-gpt2
GPT2 Discord TTS Bot

Usage: Configure main.py -> set vc_id, tc_id, bot_token

This is a discord implementation of openAI's GPT-2 NLP algorithm. 

Bot will reply to every message (including itself) in the discord channel that you specify

Bot uses gtts to output TTS to voice channel configured in main.py

Lots of improvements to be had, if using tensorflow with CPU, remove "os.environ" cuda flags from conditional_sample.py

No idea how async works so lots of unsafe conditions going on here. Feel free to contribute

