# Game Patch Notes AI

A Streamlit app for finding Steam games, reading their latest announcements, and using an OpenAI-compatible model to summarize or answer questions about patch notes.

## Features

- Search any Steam game by name and resolve its AppID
- Fetch recent announcements via Steam's public `ISteamNews` API
- Generate summaries focused on gameplay impact, balance changes, and fixes
- Ask questions about the latest announcement in a chat interface
- Use OpenAI or another OpenAI-compatible API endpoint
- Save favorite games locally

## Quick Start

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd game-patch-notes-ai
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux (run this instead of the Windows command)
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Steam search and announcements do not require an API key. To use AI features, enter an API key in the app's sidebar, or copy `.env.example` to `.env` and set `OPENAI_API_KEY`. For a compatible provider, set `OPENAI_BASE_URL` and `OPENAI_MODEL` in `.env` or change the corresponding sidebar fields. Keep real credentials in `.env`; it is excluded from Git.

To create `.env`, run `Copy-Item .env.example .env` in Windows PowerShell or `cp .env.example .env` on macOS/Linux.

## Supported Sources

| Source       | What it provides                  | Auth required |
|--------------|-----------------------------------|---------------|
| Steam News   | Raw patch notes for most PC games | No            |
| AI provider  | Summaries and chat about notes    | Yes           |

## Project Structure

```
.
├── app.py                  # Streamlit entry point
├── data/                   # Local favorites (created at runtime; not committed)
├── src/
│   ├── ai.py
│   ├── game_store.py
│   ├── nerf_client.py
│   └── steam_client.py
├── .env.example
├── LICENSE
├── README.md
└── requirements.txt
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
