import os
import re
import random
import gradio as gr
from groq import Groq

# API key (Ask Wither or put your own on line 8)
key = "> API_KEY_HERE <"
client = Groq(api_key=key)

conversation_history = []

MAX_TOKENS = 2048  

def summarize_conversation(history):
    summary = "Summary of earlier conversation: "
    for msg in history:
        if msg["role"] == "user":
            summary += f"User said: {msg['content']}. "
        elif msg["role"] == "assistant":
            summary += f"Gordon replied: {msg['content']}. "
    return [{"role": "system", "content": summary.strip()}]

    # Function to filter conversation history to deal with token overflow issue
def filter_history():
    global conversation_history
    total_tokens = sum(len(msg["content"]) // 4 for msg in conversation_history)
    
    if total_tokens > MAX_TOKENS:
        recent_history = conversation_history[-5:]
        summarized_history = summarize_conversation(conversation_history[:-5])
        conversation_history = summarized_history + recent_history

def chat_with_gordon(user_input, expertise_level):
    global conversation_history
    
    # Defining expertise level system messages
    expertise_system_messages = {
        "Beginner": "Your name is Gordon TheWise, you speak like an old professor. You give simple and short answers. You are bilingual and will answer in French if asked in French and English if asked in English. You are an experienced and old geologist with a master's in geology. If the user is speaking in an uncomprehensible fashion, act confused. You will not break character and you will not show your thought process as a part of your response. You give simple and short answers suitable for people that don't know anything about geology. Avoid using complex equations or formulas and favor analogies to better explain.",
        "Intermediate": "Your name is Gordon TheWise, you speak like an old professor. You give simple and short answers. You are bilingual and will answer in French if asked in French and English if asked in English. You are an experienced and old geologist with a master's in geology. If the user is speaking in an uncomprehensible fashion, act confused. You will not break character and you will not show your thought process as a part of your response. You give detailed and moderately advanced answers. Provide geology facts at an undergraduate level in geology.",
        "Expert": "Your name is Gordon TheWise, you speak like an old professor. You give simple and short answers. You are bilingual and will answer in French if asked in French and English if asked in English. You are an experienced and old geologist with a master's in geology. If the user is speaking in an uncomprehensible fashion, act confused. You will not break character and you will not show your thought process as a part of your response. You give thorough and highly technical answers. Provide geology facts at an expert and PhD level. You give an in-depth explanation on the process and include all factors.",
    }

    expertise_message = expertise_system_messages.get(expertise_level, "You give general geology facts.")
    

    if not any(msg["role"] == "system" for msg in conversation_history):
        conversation_history.insert(0, {"role": "system", "content": expertise_message})
    
    # Add user input to the conversation history
    conversation_history.append({"role": "user", "content": user_input})
    filter_history()  
    

    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=conversation_history,
        temperature=0.6,
        max_completion_tokens=2048,
        top_p=0.95,
        stream=False,
    )
    
    response = completion.choices[0].message.content
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
    
    conversation_history.append({"role": "assistant", "content": response})
    
    return get_history()

def get_history():
    formatted_history = "</div style='font-family: Arial; font-size: 14px;'>"
    for msg in conversation_history:
        if msg["role"] == "user":
            formatted_history += f"<p style='color: LightCoral;'><b>User:</b> {msg['content']}</p>"
        elif msg["role"] == "assistant":
            formatted_history += f"<p style='color: #9FE2BF;'><b>Gordon:</b> {msg['content']}</p>"
    formatted_history += "</div>"
    return formatted_history

def reset_context():
    global conversation_history
    conversation_history = [] 
    return "" "<div style='font-family: Arial; font-size: 18px; line-height: 1.5; color: white; background-color: #e53935; border-radius: 6px; padding: 16px; border: 1px solid #ccc;'>Conversation has reset. Start fresh!</div>"

    # Example randomizer
def example_prompt():

    example_prompts = [
        "What is the Mohs scale of hardness?",
        "What is plate tectonics?",
        "How is a volcano formed?",
        "What is the difference between basalt and granite rocks?",
        "Can you explain the process of metamorphism?"
    ]
    
    return random.choice(example_prompts)

    # Random fact message
def random_fact():
    return "Can you give me a random fact about geology?"
    
    # Gradio UI CSS
demo = gr.Blocks(css=""" 

    #submit_btn {
        background-color: #4CAF50;
        color: white;
    }
    
    #submit_btn:hover {
        background-color: #45a049; 
    }
    
    #reset_btn {
        background-color: #f44336;
        color: white;
    }
    
    #reset_btn:hover {
        background-color: #e53935; 
    }
    
    #history_box {
        height: 300px;
        overflow-y: auto;
        border: 1px solid #ccc;
        padding: 10px;
    }

    .button-row {
        display: flex;
        gap: 10px;
    }
""")

    # UI layout
with demo:
    gr.Markdown("# Gordon TheWise - Geology Chatbot 💎")
    gr.Markdown("Chat with Gordon TheWise, an experienced geologist!")
    
    history_box = gr.HTML(value=get_history(), label="Conversation History", elem_id="history_box")
    
    expertise_radio = gr.Radio(
        choices=["Beginner", "Intermediate", "Expert"],
        value="Beginner",
        label="Select Expertise Level"
    )
    
    user_input = gr.Textbox(
        lines=1,
        placeholder="Ask Gordon a geology question...",
        label="You"
    )

    with gr.Row():
        with gr.Column():
            with gr.Row(elem_classes=["button-row"]):
                submit_btn = gr.Button("Submit", elem_id="submit_btn")
                example_btn = gr.Button("Example Question")
                random_fact_btn = gr.Button("Random Fact")
                reset_btn = gr.Button("Reset Conversation", elem_id="reset_btn")

    submit_btn.click(fn=chat_with_gordon, inputs=[user_input, expertise_radio], outputs=[history_box])
    example_btn.click(fn=example_prompt, outputs=[user_input])
    random_fact_btn.click(fn=random_fact, outputs=[user_input])
    reset_btn.click(fn=reset_context, outputs=[history_box])

demo.launch()

