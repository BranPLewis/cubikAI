import utilities, sys
from smolagents import ToolCallingAgent
from tools.web_tools import YoutubeTranscriptSearchTool
from tools.cube_solver import RubiksCubeSolver
from tools.cube_layout import RubiksCubeStringVerifier
from tools.cube_db_retrieval_tool import LocalTranscriptSearchTool

def build_agent()->ToolCallingAgent:
    model = utilities.google_build_reasoning_model()

    tools = [
        YoutubeTranscriptSearchTool(), 
        LocalTranscriptSearchTool(),
        RubiksCubeSolver(),
        RubiksCubeStringVerifier(),
    ]

    agent = ToolCallingAgent(
        tools = tools,
        model = model,
        verbosity_level = 3,
        stream_outputs = False,
        planning_interval = 2,
        instructions = """You are an agent programmed
        simply to help users learn about and solve Rubik's Cubes."""
    )
    return agent

def main():
    if len(sys.argv)<2:
        print("Usage: python run_agent.py \"<your question about Rubik's Cubes.>\"")
        return
    query = sys.argv[1]
    agent = build_agent()
    print("Query:", query)
    result = agent.run(query)
    print("\n-----------Response-----------\n", result)

if __name__ == "__main__":
    main()
