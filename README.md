# Telegram Mini App

This project contains a Telegram bot built with **aiogram** and a small web application served via **FastAPI**.

## Requirements

* **Python 3.11+**
* `aiogram` 3.x
* `fastapi` 0.110 or newer
* `uvicorn` for running the FastAPI server
* `aiohttp` (used by the bot)

All of these dependencies are listed in `requirements.txt`.

## Installation

1. Install Python 3.11 or newer.
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Set the Telegram bot token in the `TG_API_TOKEN` environment variable:

```bash
export TG_API_TOKEN="<your token>"
```

## Running

Start the FastAPI server from the project root so that static files are served correctly:

```bash
uvicorn main:app
```

The server will serve `game.html` and the contents of the `frontend/` directory
thanks to the `StaticFiles` mount in `main.py`. Ensure these files are located
next to `main.py` when running `uvicorn` so that FastAPI can find them.

In another terminal start the Telegram bot:

```bash
python game.py
```

After both are running you can interact with the bot and open the web application.
