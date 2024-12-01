# Kwampus

A Discord bot for organizing Secret Santa gift exchanges within a server. Members can opt in or out, and the server owner can schedule an event and randomly assign gift-giving pairings via DM.

## Setup

**Prerequisites**: Python 3.11+, a Discord bot token with the `message content`, `members`, and `guild scheduled events` intents enabled.

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root:
   ```
   TOKEN=your_discord_bot_token_here
   ```

3. Run the bot:
   ```bash
   python main.py
   ```

> **Note**: Never commit your `.env` file or share your bot token publicly.

## Commands

| Command | Description | Who can use |
|---------|-------------|-------------|
| `!join` | Opt into Secret Santa (assigns the "Secret Santa" role) | Anyone |
| `!leave` | Opt out of Secret Santa (removes the "Secret Santa" role) | Anyone |
| `!list` | Show all current Secret Santa participants | Anyone |
| `!setdate <mm/dd/yyyy/hh/mm> <location>` | Schedule a Secret Santa event at the given date and location | Server owner only |
| `!generate` | Randomly assign pairings and notify each participant via DM | Server owner only |
| `!ping` | Check if the bot is responsive | Anyone |

### Example usage

```
!setdate 12/24/2025/18/00 123 Main St, Springfield
!generate
```

`!generate` shuffles all enrolled participants and sends each one a private DM revealing who they are gifting to. If any participant has DMs disabled, the generation is aborted and the server is notified.
