## Service Agent Query Resolver

A project to automate user query handling for an app, using OpenAI Agents.

## Getting Started

First, init virtual environment:

```bash
python3 -m venv venv
source .venv/bin/activate
```

Then, install dependencies:

```bash
pip install -r requirements.txt
```

Set up env variables:

```bash
export OPENAI_API_KEY=sk-...
```

(Optional)

```bash
export OPENAI_ORG_ID=org-...
```

Or add an **OPENAI_API_KEY** and optionally an **OPENAI_ORG_ID** to the .env file.

## Running the script

Run:

```bash
python main.py
```

## Opening gradio interface

The terminal will output a link (something like this: https://46ae36aa9613b43bba.gradio.live/) which will direct you to the test interface.

Login using the credentials.

## Testing

Write a query.
