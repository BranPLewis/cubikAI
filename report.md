# **Project Report:** 

# **AI Agent for Rubik's Cube Analysis and Solving**
# **Part 2**

Assisted by: Gemini (AI assistant)  
Date: November 18, 2025  
Name: Brandon Lewis

### **1\. Project Objective**

The goal of this project was to develop an AI agent capable of interacting with the domain of Rubik's Cubes in two distinct ways:

1. **Knowledge Retrieval:** To research and understand general topics about cube solving by sourcing information from the web.  
2. **Computational Solving:** To algorithmically solve a specific, unsolved Rubik's Cube state provided by a user.

### **2\. Component 1: Knowledge Retrieval via YouTube Transcripts**

To enable the agent to research "how-to" topics, we built a two-tool system that leverages web search and YouTube's transcript data. This allows the agent to answer qualitative questions like, "What is the beginner's method for solving a cube?"

#### **Tool A: YoutubeVideoSearchTool**

* **Purpose:** To find relevant videos on a specific topic.  
* **Mechanism:** This tool uses the DuckDuckGoSearchTool to perform a targeted search, restricted only to youtube.com.  
* **Output:** It returns a list of YouTube video IDs (e.g., \['c\_h-Ez08s7g', 'v-a-s-I-v-i-d'\]) related to the user's query (e.g., "how to solve a rubik's cube").

#### **Tool B: GetYoutubeTranscriptTool**

* **Purpose:** To extract the full text content from a specific video.  
* **Mechanism:** This tool uses the youtube-transcript-api library. It takes a single video ID (provided by YoutubeVideoSearchTool) as input.  
* **Output:** It returns a single, clean string of the video's full transcript.

**Workflow Example:**

1. **User:** "How do I solve the first layer?"  
2. **Agent (Thought):** "I need to find a video. I will use Youtube\_video\_search with the query how to solve rubik's cube first layer."  
3. **Agent (Action):** Youtube\_video\_search returns \['video\_id\_123'\].  
4. **Agent (Thought):** "Now I will get the transcript for video\_id\_123 using Get\_youtube\_transcript."  
5. **Agent (Action):** Get\_youtube\_video\_transcript returns a long text string: "Hello everyone, in this video we're going to build the white cross..."  
6. **Agent (Response):** The agent then summarizes this text to answer the user's question.

#### **Data Persistence: Transcript Database**

To support learning and prevent redundant API calls, transcripts are automatically stored in a local TinyDB database (`cube_db.json`). When a transcript is fetched, it is persisted with metadata including:
- **Video ID, Title, Channel:** For reference and organization  
- **Transcript Text:** Full timestamped transcript content  
- **URL:** Direct link to the source video  
- **Timestamp:** When the transcript was added  

This enables future queries to reference previously collected materials without re-fetching, supporting efficient knowledge accumulation for the agent.

### **3\. Component 2: Computational Solving via Kociemba Algorithm**

#### **Tool C: RubiksCubeSolverTool**

* **Purpose:** To provide a guaranteed, step-by-step solution for any valid, scrambled cube state.  
* **Mechanism:** This tool is a wrapper for the kociemba Python library, a highly optimized "two-phase" algorithm that finds a near-optimal solution.  
* **Input:** A 54-character "state string" that defines the color of every sticker on the cube, in a specific order (Up-Right-Front-Down-Left-Back).  
* **Output:** A single string of moves (e.g., U' R2 F' B2...) required to solve the cube.

**Workflow Example:**

1. **User:** "Please solve this cube: DRLUUBFBRBLRRRFRFDFBLDRDUBBULFLUDLULFRBDRFDBBUUBLDFFF"  
2. **Agent (Thought):** "This is a 54-character string. This is a job for the Rubiks\_cube\_solver tool."  
3. **Agent (Action)::** Calls RubiksCubeSolverTool with the state string.  
4. **Agent (Response):** "The solution is: U' R2 F' B2 L D' R..."

### **4\. PEAS Framework Analysis**

This agent can be described using the **PEAS (Performance, Environment, Actuators, Sensors)** framework, which defines its operational parameters.

* **Performance Measure:**  
  * **Solver:** The correctness, efficiency (shortest number of moves), and speed of the generated solution. A successful outcome is a valid move set that solves the given cube state.  
  * **Researcher:** The relevance, accuracy, and clarity of the information retrieved and summarized from YouTube transcripts in response to a user's question.  
* **Environment:**  
  * **For the Solver:** The environment is the 54-character cube\_state\_string provided by the user. It is fully observable, deterministic (a move has one outcome), discrete, and static (the cube state does not change while the agent is "thinking").  
  * **For the Researcher:** The environment is the public internet, accessed via the DuckDuckGo search tool and the youtube-transcript-api. This environment is partially observable, stochastic (search results can change), and dynamic (content is always being added/removed).  
* **Actuators (Agent's "Hands"):**  
  * **RubiksCubeSolverTool:** The agent's primary actuator for solving. It executes the kociemba.solve() function to "act" upon the cube state string and generate a solution.  
  * **Text Response:** The agent's final output to the user. This "acts" by presenting the solution moves or the summarized research.  
* **Sensors (Agent's "Eyes"):**  
  * **User Input:** The agent's primary sensor is its ability to receive a prompt (a state string or a question) from the user.  
  * **YoutubeVideoSearchTool:** This tool (using DuckDuckGoSearchTool) "senses" the web to find relevant video URLs.  
  * **GetYoutubeTranscriptTool:** This tool (using youtube-transcript-api) "senses" the content of a specific video by reading its transcript.  
  * **Transcript Database:** Acts as a secondary sensor by providing access to previously acquired knowledge, allowing the agent to retrieve stored transcripts without querying external sources.