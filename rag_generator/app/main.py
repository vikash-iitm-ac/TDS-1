from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from services.pdf_parser import parse_pdfs
from services.web_scraper import parse_website
from os import environ
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

class IngestRequest(BaseModel):
    source_type: Literal["pdf", "web"]
    urls: List[str]
    chunking_strategy: Literal["recursive", "simple"] = "recursive"

@app.post("/ingest")
async def ingest(req: IngestRequest):
    if req.source_type == "pdf":
        return await parse_pdfs(req.urls, req.chunking_strategy)
    elif req.source_type == "web":
        results = []
        for url in req.urls:
            result = await parse_website(url, req.chunking_strategy)
            results.append(result)
        return results
    else:
        raise HTTPException(status_code=400, detail="Invalid source_type")

# @app.get("/query")
# async def query_docs(q: str):
#     from app.vector_store import vectorstore
#     print(f"Querying for: {q}")
#     all_docs = vectorstore.similarity_search("", k=10)
#     print(all_docs)
#     if not q:
#         raise HTTPException(status_code=400, detail="Query cannot be empty")
#     results = vectorstore.similarity_search_with_score(q, k=3)
    
#     # pass this result to llm as context and also the user query and ask llm to answer user question based on provided context
#     # filtered = []
#     # print(results)
#     # for doc, distance in results:
#     #     similarity = 1 - distance  # For cosine distance
#     #     if similarity >= 0.9:
#     #         filtered.append({"text": doc.page_content, "source": doc.metadata.get("source")})
#     # print(filtered)
#     return results

from langchain.llms import OpenAI

@app.get("/query")
async def query_docs(q: str):
    from vector_store import vectorstore
    print(f"Querying for: {q}")
    if not q:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    results = vectorstore.similarity_search_with_score(q, k=3)
    # Filter by similarity >= 0.7

    filtered = []
    # for doc, distance in results:
    #     similarity = 1 - distance
    #     if similarity >= 0.7:
    #         filtered.append(doc.page_content)
    # if not filtered:
    #     return {"answer": "No relevant context found."}

    # Combine context
    context = "\n\n".join([doc.page_content for doc, _ in results])
    print(context)
    # context = ''
    # for result in results:
    #     context = "\n\n".join(result[0])
    #     print(context)
    prompt = f"Context:\n{context}\n\nQuestion: {q}\nAnswer: give response in json with key 'answer': 'your answer'"

    # Call LLM (OpenAI example)
    llm = OpenAI(openai_api_key=environ.get("OPENAI_API_KEY"))
    if not llm:
        raise HTTPException(status_code=500, detail="LLM not configured")
    
    answer = llm(prompt)

    return {"answer": answer}