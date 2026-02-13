# Bharat Puri – Digital Twin

A conversational AI twin that represents **Bharat Puri** (DevOps Lead & Cloud Architect). Visitors can chat about his career, skills, and experience. The twin uses your summary and LinkedIn profile for context and can record contact details and unanswered questions via Pushover notifications.

## Features

- **AI-powered chat** – GPT-4o-mini with a custom system prompt and RAG-style context from `me/summary.txt` and `me/linkedin.pdf`
- **Tool use** – Records visitor emails/notes (`record_user_details`) and logs questions the twin couldn’t answer (`record_unknown_question`)
- **Pushover integration** – Sends notifications for new leads and unknown questions (optional; app runs without it if env vars are missing)
- **Gradio UI** – Simple chat interface, suitable for local use or [Hugging Face Spaces](https://huggingface.co/spaces)

## Project structure

```
digital_twin/
├── app.py              # Gradio app + Me (digital twin) logic
├── requirements.txt
├── README.md
└── me/
    ├── summary.txt     # Short bio/summary (used in system prompt)
    └── linkedin.pdf    # LinkedIn profile text (PDF, extracted at startup)
```

## Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd digital_twin
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root (or set these in your environment):

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for chat completions |
| `PUSHOVER_TOKEN` | No | Pushover app token (for notifications) |
| `PUSHOVER_USER` | No | Pushover user key |

If Pushover vars are missing, the app still runs; tool calls that trigger `push()` will no-op (or you can add a guard in code).

### 3. Add your content

- **`me/summary.txt`** – Plain-text summary/bio used in the system prompt.
- **`me/linkedin.pdf`** – PDF of your LinkedIn profile; text is extracted at startup and added to the prompt.

### 4. Run locally

```bash
python app.py
```

Then open the URL shown in the terminal (default: `http://127.0.0.1:7860`).

## Deployment (Hugging Face Spaces)

- Use **Gradio** as the SDK and set `app_file: app.py` in the Space’s metadata.
- Add `OPENAI_API_KEY`, `PUSHOVER_TOKEN`, and `PUSHOVER_USER` as [Space secrets](https://huggingface.co/docs/hub/spaces-overview#managing-secrets).
- Ensure `me/summary.txt` and `me/linkedin.pdf` are in the repo (or add them via the Files UI).

## License

Use and modify as you like; consider adding a LICENSE file if you want to specify terms.
