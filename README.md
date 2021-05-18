# tengi - Telegram bot ENGIne

Key features:
- Button clicks with no domain name needed (polling)
- Bot commands in bash-like style
- Ability to send periodic updates to other components (not only to Telegram callbacks) 
- Ability to access Telegram both as a bot and as a user
- Many useful chatbot components

# Bots built with `tengi`
- [liker](https://github.com/luckybots/liker) - allows you to add reactions (likes, etc.) to channel posts. Try in Telegram [@liker10_bot](https://t.me/liker10_bot)
- [anonym](https://github.com/luckybots/anonym) - anonymizes messages in chats. Try it in Telegram [@anonym10_bot](https://t.me/anonym10_bot)

# For contributors
In order to add `tengi` source code to your project run the following in your project environment
```
cd [TENGI_REPO_FOLDER]
pip uninstall tengi
python setup_develop.py develop
```
