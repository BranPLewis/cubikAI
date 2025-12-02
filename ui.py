import gradio as gr
from run_agent import build_agent
import sys

# 1. Initialize the agent
# We build it once so we don't reload the model on every message
print("Building Agent... please wait.")
agent = build_agent()
print("Agent is ready!")

def process_query(message, history):
    """
    Callback function for Gradio.
    Arguments:
        message (str): The current user input.
        history (list): List of previous messages (context).
    """
    try:
        # We pass the message to the agent.
        # Note: If you want the agent to remember context, you might need to 
        # concatenate history, but for now we treat each query as a new task.
        response = agent.run(message)
        return str(response)
    except Exception as e:
        return f"Error: {str(e)}"

CSS = """
/* 1. Force the main Gradio container to use the full viewport height */
.gradio-container {
    height: 100vh !important;
    max-height: 100vh !important;
}

/* 2. Target the specific element that contains the ChatInterface contents */
/* This class usually wraps the entire content area (title, chatbot, textbox) */
.gradio-app {
    height: 100% !important;
}

/* 3. Force the ChatInterface itself to expand vertically */
/* This targets the inner container where the chatbot and input are located */
#chat-interface-container {
    height: 100% !important;
    display: flex;
    flex-direction: column;
}

/* 4. Crucial: Make the Chatbot component (the message history) fill the REST of the space */
/* In a flex column, flex-grow: 1 makes this element consume all available space */
#chatbot-history-container {
    flex-grow: 1 !important;
    overflow: auto; /* Ensures you can still scroll messages */
    min-height: 0; /* Important for flex children */
}

/* Optional: Hide the small Gradio footer at the bottom */
footer {
    visibility: hidden;
}
"""

# 2. Build the Chat Interface
with gr.Blocks(
        fill_height=True,
        fill_width=True,
        #css=CSS,
        title="Rubik's Cube AI Agent"
        ) as demo:

    gr.ChatInterface( 
        fn=process_query,
        title="Rubik's Cube AI Agent",
        description="Ask me how to solve the cube, or give me a cube state string to solve!",
        examples=[
        "How do I solve the white cross?",
        "What is the algorithm for T-Perm?",
        "Help me understand the corners."
        ],
    # Customizing the theme to look a bit more 'techy'
    #theme=gr.themes.Soft()
    )
demo.height=1000

if __name__ == "__main__":
    # launch(share=True) would create a public link, 
    # but for local use just launch() is fine.
    demo.launch(share=True)
