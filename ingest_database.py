from langchain_community.document_loaders import PyPDFDirectoryLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4
import os

# import the .env file
from dotenv import load_dotenv
load_dotenv()

# configuration
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

# initiate the embeddings model
embeddings_model = OllamaEmbeddings(model="mxbai-embed-large:latest")

# initiate the vector store
vector_store = Chroma(
    collection_name="tiffany_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH,
)

def load_documents(data_path):
    """Loads documents from PDF and JSON files in the given directory."""
    pdf_loader = PyPDFDirectoryLoader(data_path)
    json_loader = JSONLoader(
        file_path=data_path,
        jq_schema='.[]',  # Adjust this based on your JSON structure
        text_content=False)
    
    pdf_documents = pdf_loader.load()
    # Check if the directory itself is a JSON file
    if data_path.lower().endswith('.json'):
        json_documents = json_loader.load()
    else:
        json_documents = []
        for filename in os.listdir(data_path):
            if filename.lower().endswith('.json'):
                file_path = os.path.join(data_path, filename)
                loader = JSONLoader(
                    file_path=file_path,
                    jq_schema= '.[]', 
                    text_content=False
                )
                json_documents.extend(loader.load())
    
    return pdf_documents + json_documents

# loading the documents
raw_documents = load_documents(DATA_PATH)

# splitting the document
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

# creating the chunks
chunks = text_splitter.split_documents(raw_documents)

# creating unique ID's
uuids = [str(uuid4()) for _ in range(len(chunks))]

# adding chunks to vector store
vector_store.add_documents(documents=chunks, ids=uuids)


### ToDo:
###         Again, Separate the memory.json from the ingested memory. the ingested needs to be sumerise and formated in a PDF or a better structured Json file 
###         Add a auto run fucntion or auto runnit with a .bat
###         
###         Thanks to Thomas Janssen for this Amazing code! https://www.youtube.com/@thomasjanssen-tech <--- His YT Channel. 