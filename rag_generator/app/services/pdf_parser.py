import httpx
import pdfplumber
import io
from typing import List
from langchain.schema import Document
from vector_store import vectorstore
from utils.chunker import get_chunker

async def parse_pdfs(urls: List[str], chunking_strategy="recursive"):
    chunker = get_chunker(chunking_strategy)

    for url in urls:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url)
                res.raise_for_status()
                with pdfplumber.open(io.BytesIO(res.content)) as pdf:
                    text = "\n".join([page.extract_text() or "" for page in pdf.pages])

                    docs = chunker.create_documents([text], metadatas=[{"source": url}])
                    print(docs)
                    vectorstore.add_documents(docs)
        except Exception as e:
            print(f"[PDF ERROR] {url}: {e}")

    vectorstore.persist()
    return {"status": "PDF ingestion completed", "count": len(urls)}

