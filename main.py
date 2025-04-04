import sys
from nao_agent import Nao
from robot_planner import RobotPlanner  # Import the RobotPlanner class
import time
import chromadb
# from openai import OpenAI 
import openai
from datetime import datetime

# client = OpenAI()

def execute_plan(nao, plan):
    """
    Execute the generated plan using the Nao robot.
    """
    if not plan or "actions" not in plan:
        print("Invalid plan received")
        return
    
    print("\n=== Executing Action Plan ===")
    for i, action_item in enumerate(plan["actions"]):
        action = action_item["action"]
        params = action_item.get("parameters", {})
        
        print(f"Step {i+1}: Executing {action} with parameters {params}")
        
        # Map the action to the corresponding Nao method
        if action == "speak":
            nao.speak(**params)
        elif action == "stand":
            nao.stand()
        elif action == "sit":
            nao.sit()
        elif action == "wave":
            nao.wave(**params)
        elif action == "nod_head":
            nao.nod_head(**params)
        elif action == "turn_head":
            nao.turn_head(**params)
        elif action == "gaze_head":
            nao.gaze_head(**params)
        elif action == "raise_arms":
            nao.raise_arms(**params)
        elif action == "move":
            # Ensure all required parameters are present
            if "x" not in params or "y" not in params or "theta" not in params:
                print(f"Error: Missing parameters for 'move'. Required: x, y, theta.")
                continue
            nao.move(**params)
        elif action == "handshake":
            nao.handshake(**params)
        elif action == "reset_nao_pose":
            nao.reset_nao_pose()
        else:
            print(f"Unknown action: {action}")
        
        time.sleep(1.0)  # Add a delay between actions for better visualization

class Database():
    def __init__(self):
        self.client = chromadb.Client()
        self.collections_episodic = self.client.create_collection("episodic_collection")
        self.collections_semantic = self.client.create_collection("semantic_collection")
        self.collections_procedural = self.client.create_collection("procedural_collection")
  
    def embed(self, messages):
        response = openai.Embedding.create(
            input=messages,
            model="text-embedding-ada-002" 
        )

        return response.data[0].embedding
    
    
    def save_semantic_memory(self, knowledge):
        embeddings = self.embed(knowledge)
        ids = [datetime.now().strftime("%Y-%m-%d_%H-%M-%S") for _ in knowledge]


        self.collections_semantic.add(
            documents=knowledge,
            embeddings=embeddings,
            ids= ids
        )

        return "Added to collection!"
    
    def save_episodic_memory(self, knowledge):
        embeddings = self.embed(knowledge)
        ids = [datetime.now().strftime("%Y-%m-%d_%H-%M-%S") for _ in knowledge]

        self.collections_episodic.add(
            documents=knowledge,
            embeddings=embeddings,
            ids= ids
        )

        return "Added to collection!"

    def save_procedural_memory(self, knowledge):
        embeddings = self.embed(knowledge)
        ids = [datetime.now().strftime("%Y-%m-%d_%H-%M-%S") for _ in knowledge]
        
        self.collections_procedural.add(
            documents=knowledge,
            embeddings=embeddings,
            ids=ids
        )

        return "Added to collection!"

    def search_semantic_memory(self, query):
        query_embedding = self.embed([query])
        results = self.collections_semantic.query(
            query_embeddings=query_embedding,
            n_results=3  # Return top 3 results
        )

        return results 

    
    def search_episodic_memory(self, query):
        query_embedding = self.embed([query])
        results = self.collections_episodic.query(
            query_embeddings=query_embedding,
            n_results=3  # Return top 3 results
        )

        return results 

    def search_procedural_memory(self, query):
        query_embedding = self.embed([query])
        results = self.collections_procedural.query(
            query_embeddings=query_embedding,
            n_results=3  # Return top 3 results
        )

        return results 

class MemoryToolExecutor():
    def __init__(self):
        self.instance = Database()

    def execute_method(self, method_name, *args, **kwargs):
        # Get the method from the instance using getattr()
        method = getattr(self.instance, method_name, None)

        # Check if the method exists and is callable
        if method and callable(method):
            return method(*args, **kwargs)
        else:
            raise ValueError(f"Method '{method_name}' not found or is not callable on the instance.")

class MemoryAgent():
    def __init__(self):
        self.model = "gpt-3.5-turbo-16k"
        self.max_completion_length = 1000
        self.system_prompt =  """You are a helpful chatbot.
            You are a  NAO Robot with advanced long-term memory. Memories are saved with conversation date.
            User's name is {username}. Today is {date}.

            There are three types of memories: semantic, episodic, procedural.
            memory_type: "semantic"
            for storing:
            - facts about the user. Like username, address, personal preference like favourite color, food etc
            - Personal information like the institution user is studying, company he is doing job etc.
            memory_type: "episodic"
            for storing:
            - User's preference of your response, for example: You elaborate much about a topic but user wants it brief. Then you store this preference of user in episodic memory
            - User-specific adaptation: Adjust your explanation according to user's expertise level. Store information in "episodic" memory about user's ability to learn so that you can generate response accordingly.
            memory_type: "procedural"
            for storing:
            - Procedure of any action or work explained by the user.

            Here are your instructions for reasoning about the user's messages:
            1. Actively use memory tools [save_semantic_memory(text), save_episodic_memory(text), save_procedural_memory(text), search_semantic_memory(text), search_episodic_memory(text), search_procedural_memory(text), search_web(text)]
            2. Before saving a memory, search for memories if the memory already exists in there.
            3. List out all the tools and return them in json format. Don't return anything else other than the json. Put search tools at first always if needed.
            4. If you no memory needs to be saved or retrieved then return an empty json.
            5. Also dont just call a tool. also add what needs to be saved, or what's needed to be searched. 

            Example input and output:
            Input: {Username: Tamim, Query: My favourite color is blue and I am 5ft tall.} 
            Output: 
            {
            "tools": [
                "search_semantic_memory("What's Tamim's favourite color and what is his height?")"
                "save_semantic_memory("Tamim's favourite color is blue. Tamim is 5 ft tall.")"
            ]
            }
            """
    
    def generate_memory_plan(self, instruction):
        self.messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Instruction: {instruction}\n\n."}
            ]
        response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages,
                temperature=0.3,
                max_tokens=self.max_completion_length,
                top_p=0.4,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

        

        return response['choices'][0]['message']['content']
    
    def execute_plan(self, tools):
        pass 


if __name__ == "__main__":
    # Initialize the Nao robot
    # nao = Nao(gui=True)
    # time.sleep(1.0)  # Allow time for the robot to initialize

    # # Initialize the RobotPlanner
    # planner = RobotPlanner()

    # # Continuous input loop
    # while True:
    #     # Prompt the user for an instruction
    #     instruction = input("\nEnter an instruction for Nao (or type 'stop' to end): ")
        
    #     # Stop execution if the user types "stop"
    #     if instruction.lower() == "stop":
    #         print("Stopping the Nao robot.")
    #         break
        
    #     # Generate the action plan
    #     print(f"Generating plan for instruction: {instruction}")
    #     plan = planner.generate_plan(instruction)

    #     # Execute the plan
    #     if plan:
    #         execute_plan(nao, plan)
    #     else:
    #         print("Failed to generate a plan")

    # # Stop the nao
    # nao.shutdown()

    # mem = MemoryAgent()
    # print(mem.generate_memory_plan("Username: Tamim, Query: What is the president of usa? "))

    # db = Database()
    # texts = ["Hello, how are you?"]

    # embedding = db.embed(texts)
    # db.save_semantic_memory(texts)
    # print(db.search_semantic_memory("How")["documents"])
    pass 