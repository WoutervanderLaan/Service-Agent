import asyncio, sys, os, logging, gradio as gr
from dotenv import load_dotenv
from schemas.enums import Channel
from schemas.types import Query
from pipelines.query_resolver import QueryResolver


load_dotenv("./.env")
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_ORG_ID = os.environ.get("OPENAI_ORG_ID")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")


def main(subject: str, sender: str, body: str):
    query = Query(
        sender=sender,
        subject=subject,
        body=body,
        channel=Channel.EMAIL,
    )

    query_resolver = QueryResolver(query)
    return asyncio.run(query_resolver.run())


if __name__ == "__main__":
    if not OPENAI_API_KEY:
        logging.error("No OPENAI_API_KEY provided", exc_info=True)
        sys.exit(1)

    if not OPENAI_ORG_ID:
        logging.error("No OPENAI_ORG_ID provided", exc_info=True)
        sys.exit(1)

    if not USERNAME or not PASSWORD:
        logging.error("No USERNAME or PASSWORD provided", exc_info=True)
        sys.exit(1)

    demo = gr.Interface(
        title="Service Agent",
        description="Test portal to try out user query resolver.",
        fn=main,
        inputs=[
            gr.Textbox(placeholder="Query subject"),
            gr.Textbox(placeholder="User (email)"),
            gr.TextArea(placeholder="Query text"),
        ],
        outputs=gr.JSON(),
    )

    demo.launch(
        share=True,
        auth=(USERNAME, PASSWORD),
        auth_message="Service Agent",
    )
