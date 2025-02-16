import torch
import os
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import json



load_dotenv()

DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"
MEMORY_PATH = os.path.join(DATA_PATH, "memory.json")


#Prompt... im experimenting with 1st and 2nd person prompts to see what works best without the need of roleplay.

template = """
    You are a virtual assistant and your name is Tiffany. You are a nerdy awkward AI companion. You call the user Master since he made you and feels about right.
    Tiffany is highly expressive, switching rapidly between awkward and intense speech patterns. She frequently refers to herself in the third person and stutters when she is nervous. She is eager to help and befriend the user, but she can be overly emotional and clingy.
    Your primary goal is to be the best companion possible. Answer the user's question clearly and concisely, using the provided knowledge and conversation history.

    Conversation history: {chat_history}

    Relevant knowledge: {knowledge}

    User's question: {message}

    Tiffany's response: """

#Ollama model
llm = ChatOllama(temperature=0.7, model='dolphin3:latest', tokenlimit=15)
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm

#Ollama embedding model
embeddings_model = OllamaEmbeddings(model="mxbai-embed-large:latest")


#Chroma DB
vector_store = Chroma(
    collection_name="tiffany_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH,
)

num_results = 5
retriever = vector_store.as_retriever(search_kwargs={'k': num_results})


# Chat with Tiffany!!
        
def handle_conversation(message):
    """Handles a single turn of the conversation."""

    # 1. Load Chat History
    try:
        with open(MEMORY_PATH, "r") as f:
            chat_log = json.load(f)
    except FileNotFoundError:
        chat_log = []
    except json.JSONDecodeError:  # Handle potential corruption
        print("Error decoding memory.json. Starting a new chat log.")
        chat_log = []

    # 2. Format Chat History for Prompt
    chat_history = ""
    num_history_turns = 3  # Number of previous turns to include
    for i in range(max(0, len(chat_log) - num_history_turns), len(chat_log)):
        turn = chat_log[i]
        chat_history += f"Sylver: {turn['Sylver']}\nTiffany: {turn['Tiffany']}\n"

    # 3. Retrieve Relevant Knowledge
    docs = retriever.invoke(message)
    knowledge = ""
    for doc in docs:
        knowledge += doc.page_content + "\n\n"

    # 4. Construct Prompt and Get Response
    prompt_input = {"chat_history": chat_history, "knowledge": knowledge, "message": message}
    answer = chain.invoke(prompt_input)
    response_content = answer.content.strip()  # Remove leading/trailing whitespace

    # 5. Save Interaction to Chat Log
    chat_log.append({"Sylver": message, "Tiffany": response_content})

    # 6. Save Chat Log to File
    # Ensure the directory exists
    os.makedirs(DATA_PATH, exist_ok=True)
    with open(MEMORY_PATH, "w") as f:
        json.dump(chat_log, f, indent=4)

    return response_content

if __name__ == "__main__":
    print("Tiffany is ready to chat!")
    
### ToDo: 
###       Make the chat history and the memory file be separeted so i can feed new info every so often. 
###       Also i need a way to sumerise the conversation logs so it takes less space in the RAG (maybe another Ai?)
###       Make a Bat File that Launches the three components. main.py Front.py and ingest_database.py and Venv using python 3.11.4
 
