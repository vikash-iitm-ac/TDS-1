from langchain.embeddings import OpenAIEmbeddings
import os
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()

persist_directory = os.getenv("CHROMA_DIRECTORY", "./chroma_data")

chroma_settings = Settings(
    persist_directory=persist_directory,
    anonymized_telemetry=False
)

embedding_function = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),   
)

vectorstore = Chroma(
    collection_name=os.getenv("CHROMA_COLLECTION", "rag_data"),
    embedding_function=embedding_function,
    client_settings=chroma_settings
)