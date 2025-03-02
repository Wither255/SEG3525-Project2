import os
import re
import gradio as gr
from groq import Groq

# API key 
# key = api_key_here
client = Groq(api_key=key)

# Store conversation history
conversation_history = []

def chat_with_gordon(user_input):
    
    # System message history as input
    if not any(msg["role"] == "system" for msg in conversation_history):
        conversation_history.insert(0, {"role": "system", "content": "Your name is Gordon TheWise. You give simple and short answers. You are an experienced and old geologist with a master's in geology. You provide interesting geology facts at a beginner level."})
    
    # Append user input to input
    conversation_history.append({"role": "user", "content": user_input})
    
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=conversation_history,
        temperature=0.6,
        max_completion_tokens=2048,
        top_p=0.95,
        stream=False,
    )
    
    response = completion.choices[0].message.content
    
    # Remove thinking 
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
    
    # Append response to conversation history
    conversation_history.append({"role": "assistant", "content": response})
    
    return response, get_history()

def get_history():
    
    # History box
    
    formatted_history = "<div style='font-family: Arial; font-size: 24px line-height: 1.5;'>"
    for msg in conversation_history:
        if msg["role"] == "user":
            formatted_history += f"<p style='color: LightCoral;'><b>User:</b> {msg['content']}</p>"
        elif msg["role"] == "assistant":
            formatted_history += f"<p style='color: #9FE2BF;'><b>Gordon:</b> {msg['content']}</p>"
    formatted_history += "</div>"
    return formatted_history

# Gradio interface
demo = gr.Blocks()

with demo:
    gr.Markdown("# Gordon TheWise - Geology Chatbot")
    gr.Markdown("Chat with Gordon TheWise, an experienced geologist who shares fascinating geology facts!")
    history_box = gr.HTML(value=get_history(), label="Conversation History")
    user_input = gr.Textbox(lines=2, placeholder="Ask Gordon a geology question, or ask for a random fact", label="You")
    response_box = gr.Textbox(interactive=False, label="Gordon")
    submit_btn = gr.Button("Submit")
    
    submit_btn.click(fn=chat_with_gordon, inputs=user_input, outputs=[response_box, history_box])

demo.launch()
