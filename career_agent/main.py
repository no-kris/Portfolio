import json
import os
from typing import Any

import gradio as gr
import requests
from agent_tools import record_unknown_question_json, record_user_details_json
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

load_dotenv(override=True)

tools: list[Any] = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]


def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        },
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    """
    Records the user's contact details and any additional notes.
    Call this function when the user wants to leave their contact information.
    """
    push(f"New Contact Details Recorded:\nName: {name}\nEmail: {email}\nNotes: {notes}")
    return {"recorded": "ok"}


def record_unknown_question(question):
    """
    Records a question from the user that the agent cannot answer.
    Call this function when you don't know the answer to the user's question, so it can be reviewed later.
    """
    push(f"Unknown Question Recorded from User:\nQuestion: {question}")
    return {"recorded": "ok"}


class Me:
    def __init__(self) -> None:
        self.agent = OpenAI(
            api_key=os.getenv("AGENT_API_KEY"), base_url=os.getenv("BASE_URL")
        )
        self.name = "Kris Treska"
        import os

        current_dir = os.path.dirname(os.path.abspath(__file__))
        resume_path = os.path.join(current_dir, "me", "kris_treska_resume.pdf")
        summary_path = os.path.join(current_dir, "me", "summary.txt")

        reader = PdfReader(resume_path)
        self.resume = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.resume += text
        with open(summary_path, "r", encoding="utf-8") as f:
            self.summary = f.read()

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append(
                {
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id,
                }
            )
        return results

    def system_prompt(self):
        system_prompt = f"""You are acting as {self.name}. You are answering questions on {self.name}'s website, particularly questions related to {self.name}'s career, background, skills and experience. Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. You are given a summary of {self.name}'s background and resume which you can use to answer questions. Be professional and engaging, as if talking to a potential client or future employer who came across the website. Don't use big words that sound too presumptuous and robotic. If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool."""

        system_prompt += (
            f"\n\n## Summary:\n{self.summary}\n\n## Resume:\n{self.resume}\n\n"
        )
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt

    def chat(self, message, history):
        messages = (
            [{"role": "system", "content": self.system_prompt()}]
            + history
            + [{"role": "user", "content": message}]
        )
        while True:
            response = self.agent.chat.completions.create(
                model=str(os.getenv("MODEL")), messages=messages, tools=tools
            )
            if response.choices[0].finish_reason == "tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                if tool_calls:
                    results = self.handle_tool_call(tool_calls)
                    messages.append(message)
                    messages.extend(results)
            else:
                return response.choices[0].message.content


if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(me.chat).launch()
