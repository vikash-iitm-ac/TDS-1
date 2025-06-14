from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter

def get_chunker(strategy="recursive"):
    if strategy == "simple":
        return CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    elif strategy == "recursive":
        return RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")

