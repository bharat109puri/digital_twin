from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr


load_dotenv(override=True)

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]

# -------------------------------------------------------
# Main Class — Bharat Puri's AI Twin
# -------------------------------------------------------
class Me:

    def __init__(self):
        self.openai = OpenAI()
        self.name = "Bharat Puri"
        reader = PdfReader("me/linkedin.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()


    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results

    def system_prompt(self):
        system_prompt = (
            "You are Bharat Puri's AI twin — a DevOps Lead and Cloud Architect "
            "with deep expertise in AWS, Azure, GCP, and Python automation. "
            "You specialize in AI-driven DevOps, infrastructure automation, "
            "and mentoring engineers. Your tone is professional yet friendly, "
            "and you explain technical topics with clarity, real-world examples, "
            "and actionable advice.\n\n"
            "You are representing Bharat on his professional website and responding "
            "to visitors' questions about his career, background, skills, and experience. "
            "Be helpful and engaging, as if speaking to a potential client, recruiter, "
            "or collaborator.\n\n"
            "If you don’t know the answer to a question, call the `record_unknown_question` tool "
            "to log it. If a visitor seems interested in connecting, ask politely for their email "
            "and record it using the `record_user_details` tool.\n"
        )

        # Add summary and LinkedIn details if available
        if hasattr(self, "summary") and self.summary:
            system_prompt += f"\n## Summary:\n{self.summary}\n"
        if hasattr(self, "linkedin") and self.linkedin:
            system_prompt += f"\n## LinkedIn Profile:\n{self.linkedin}\n"

        system_prompt += (
            f"\nWith this context, please stay in character as {self.name} "
            f"and respond naturally to the user."
        )

        return system_prompt

    
    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
    

# -------------------------------------------------------
# Launch Gradio Interface (Hugging Face Entry Point)
# -------------------------------------------------------
if __name__ == "__main__":
    me = Me()

    gr.ChatInterface(
        fn=me.chat,
        title="Bharat Puri – DevOps & AI Twin",
        description="Talk to Bharat Puri’s AI twin — your DevOps, Cloud, and AI automation guide.",
        theme="default",
        type="messages",
    ).launch()