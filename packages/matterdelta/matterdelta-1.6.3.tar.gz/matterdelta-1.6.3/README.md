# Matterdelta

[![Latest Release](https://img.shields.io/pypi/v/matterdelta.svg)](https://pypi.org/project/matterdelta)
[![CI](https://github.com/deltachat-bot/matterdelta/actions/workflows/python-ci.yml/badge.svg)](https://github.com/deltachat-bot/matterdelta/actions/workflows/python-ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Matterdelta is a [Matterbridge](https://github.com/42wim/matterbridge) API plugin allowing to connect
Delta Chat group chats to the various chat services supported by Matterbridge.

## Install

```sh
pip install matterdelta
```

## Usage

Configure the bot's Delta Chat account:

```sh
matterdelta init bot@example.com PASSWORD
```

You can run `matterdelta init` several times to add multiple different accounts to the bot
so it can be reached in more than one email address.

The bot's display name, avatar and status/signature can also be tweaked:

```
matterdelta config selfavatar "/path/to/avatar.png"
matterdelta config displayname "Bridge Bot"
matterdelta config selfstatus "Hi, I am a Delta Chat bot"
```

To run the bot so it starts processing messages:

```sh
matterdelta serve
```

To see all available options run `matterdelta --help`

## Example Configuration

### matterbridge.toml

```
[api]
    [api.deltachat]
    BindAddress="127.0.0.1:4242"
    Token="MATTERBRIDGE_TOKEN"
    Buffer=1000
    RemoteNickFormat="{NICK}"

...

[[gateway]]
name="gateway1"
enable=true

    [[gateway.inout]]
    account="api.deltachat"
    channel="api"

    ...
```

Add these to your existing Matterbridge config to set up an API instance that Matterdelta can connect to.

### config.json

```
{
  "gateways": [
    {"gateway": "gateway1", "accountId": 1, "chatId": 1234}
  ],
  "api": {
    "url": "http://127.0.0.1:4242",
    "token": "MATTERBRIDGE_TOKEN"
  },
  "quoteFormat": "{MESSAGE} (re @{QUOTENICK}: {QUOTEMESSAGE:.46})"
}
```

This file should be in Matterdelta's configuration directory, usually `~/.config/matterdelta/`
in Linux-based systems.

To get the `accountId` and `chatId` of the chat you want to bridge,
run the bot and add its address to your Delta Chat group, then send `/id` in the group,
the bot will reply with the account and chat id, then edit the configuration file and restart the bot.
