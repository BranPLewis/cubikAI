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

# 2. Build the Chat Interface
demo = gr.ChatInterface(
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

if __name__ == "__main__":
    # launch(share=True) would create a public link, 
    # but for local use just launch() is fine.
    demo.launch()
