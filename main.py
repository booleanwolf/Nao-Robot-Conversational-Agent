import sys
from nao_agent import Nao
from robot_planner import RobotPlanner  # Import the RobotPlanner class
import time
import chromadb
# from openai import OpenAI 
import openai
from datetime import datetime
import json
import re
import http.client

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

client_chroma = chromadb.Client()

COLLECTION_EPISODIC = client_chroma.create_collection("episodic_collection")
COLLECTION_SEMANTIC = client_chroma.create_collection("semantic_collection")
COLLECTION_PROCEDURAL = client_chroma.create_collection("procedural_collection")

class Database():
    def __init__(self):
        self.client = chromadb.Client()
        self.collections_episodic = COLLECTION_EPISODIC
        self.collections_semantic = COLLECTION_SEMANTIC
        self.collections_procedural = COLLECTION_PROCEDURAL
  
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

        print(f"{knowledge} saved in semantic memory")  

        return "Added to collection!"
    
    def save_episodic_memory(self, knowledge):
        embeddings = self.embed(knowledge)
        ids = [datetime.now().strftime("%Y-%m-%d_%H-%M-%S") for _ in knowledge]


        self.collections_episodic.add(
            documents=knowledge,
            embeddings=embeddings,
            ids= ids
        )

        print(f"{knowledge} saved in episodic memory")


        return "Added to collection!"

    def save_procedural_memory(self, knowledge):
        embeddings = self.embed(knowledge)
        ids = [datetime.now().strftime("%Y-%m-%d_%H-%M-%S") for _ in knowledge]

        
        
        self.collections_procedural.add(
            documents=knowledge,
            embeddings=embeddings,
            ids=ids
        )
        print(f"{knowledge} saved in procedural memory")

        return "Added to collection!"

    def search_semantic_memory(self, query):
        query_embedding = self.embed([query])
        results = self.collections_semantic.query(
            query_embeddings=query_embedding,
            n_results=1  # Return top 3 results
        )
        if results["documents"][0]:
            s = results["documents"][0]
            print(f"Found {s}")

            return results["documents"][0]

    
    def search_episodic_memory(self, query):
        query_embedding = self.embed([query])
        results = self.collections_episodic.query(
            query_embeddings=query_embedding,
            n_results=1 # Return top 3 results
        )
        if results["documents"][0]:
            s = results["documents"][0]
            print(f"Found {s}")

            return results["documents"][0]

    def search_procedural_memory(self, query):
        query_embedding = self.embed([query])
        results = self.collections_procedural.query(
            query_embeddings=query_embedding,
            n_results=1 # Return top 3 results
        )
        if results["documents"][0]:
            s = results["documents"][0]
            print(f"Found {s}")

            return results["documents"][0]

        return results 

    def search_web(self, query):
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({
        "q": query
        })
        headers = {
        'X-API-KEY': '428d5c35b8de994c8af5bcf72aa21f2a36ca4755',
        'Content-Type': 'application/json'
        }
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()

        return [data.decode("utf-8")]

database = Database()
    # def add_two(self, a, b, c):
    #     return a + b + c

class MemoryToolExecutor():
    def __init__(self):
        self.instance = database

    def execute_method(self, method_name, *args, **kwargs):
        # Get the method from the instance using getattr()
        method = getattr(self.instance, method_name, None)

        # Check if the method exists and is callable
        if method and callable(method):
            return method(*args, **kwargs)
        else:
            raise ValueError(f"Method '{method_name}' not found or is not callable on the instance.")
    
    def execute_memory_plan(self, tools_response):
        searched_info = ""
        
        tr_modified = re.sub(r'(\(.*?)(\".*?\")(.*?\))', lambda match: match.group(0).replace('"', '\\"'), tools_response)
        # print(tr_modified)

        data = json.loads(tr_modified)
        
        for tool in data["tools"]:
            # Parse the function name and arguments
            function_name = tool.split('(')[0]
            arguments = tool.split('(')[1].split(')')[0].strip("'")
            print(f"Executing {function_name} with {arguments}")
            
            # Call execute_method
            if "search" in function_name:
                info = self.execute_method(function_name, arguments)
                if info:
                    searched_info += ", ".join(map(str, info)) 
            else:
                self.execute_method(function_name, [arguments])
            
        return searched_info

class MemoryAgent():
    def __init__(self):
        self.model = "gpt-4o-mini"
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
    
    def execute_plan(self, tools_response):
        pass 


class Episode():
    def __init__(self):
        pass

if __name__ == "__main__":
    # Initialize the Nao robot
    nao = Nao(gui=True)
    time.sleep(1.0)  # Allow time for the robot to initialize

    # Initialize the RobotPlanner
    planner = RobotPlanner()
    executor = MemoryToolExecutor()
    mem = MemoryAgent()

    username = input("Username: ")
    # Continuous input loop
    while True:
        # Prompt the user for an instruction
        instruction = input("\nTalk with the robot (or type 'stop' to end): ")
        
        # Stop execution if the user types "stop"
        if instruction.lower() == "stop":
            print("Stopping the Nao robot.")
            break

        memory_tools_response = mem.generate_memory_plan(f"Username: {username}, Query: {instruction}")
        saved_info = executor.execute_memory_plan(memory_tools_response)

        memory = ""
        if saved_info:
            print(f" Saved info: {saved_info}")
            memory = saved_info
            # exit()
            # memory = " ".join(saved_info["documents"])  

        # Generate the action plan
        print(f"{username} is asking you, {instruction}. Previous memory of {username}: {memory}")

        formatted_instruction = f"{username} says, {instruction}"

        plan = planner.generate_plan(formatted_instruction, memory)

        # Execute the plan
        if plan:
            execute_plan(nao, plan)
        else:
            print("Failed to generate a plan")

    # Stop the nao
    nao.shutdown()



        
    
    # tr = r"""{
    # "tools": [
    #     "save_episodic_memory("Tamim prefers short responses.")",
    #     "save_semantic_memory("Tamim prefers responses in Bangla.")"
    # ]
    # }"""
   

#     tr_modified = re.sub(r'(\(.*?)(\".*?\")(.*?\))', lambda match: match.group(0).replace('"', '\\"'), tr)

#     print(tr_modified)

# #     a = r"""{
# #     "tools": [
# #         "save_episodic_memory(\"Tamim prefers short responses.\")",
# #         "save_semantic_memory(\"Tamim prefers responses in Bangla.\")"
# #     ]
# # }"""

#     # Convert the string to JSON
#     parsed_json = json.loads(tr_modified)

#     # Print the resulting JSON
#     print(parsed_json)
 
    
#     texts = ["Tamim's hate person is Halima"]

#     database.save_semantic_memory(texts)
    
    
#     texts = ["Tamim's favourite person is Halima"]

#     database.save_semantic_memory(texts)

#     results = database.collections_semantic.get()
#     print(database.search_semantic_memory("Favourite")["documents"])
# # Print the documents
#     print("Getting all the results")
#     for result in results['documents']:
#         print(result)

    pass 