import httpx
from bs4 import BeautifulSoup
from typing import Set
from urllib.parse import urljoin
from utils.chunker import get_chunker
from vector_store import vectorstore
from langchain.schema import Document

async def scrape_links_recursively(url: str, visited: Set[str], depth=0, max_depth=2):
    if url in visited or depth > max_depth:
        return []

    visited.add(url)
    documents = []

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            text = soup.get_text(separator="\n", strip=True)
            print(f"[SCRAPING] {url} - Depth: {depth} - Text Length: {len(text)}")
            documents.append((text, url))

            for tag in soup.find_all("a", href=True):
                href = tag["href"]
                child_url = urljoin(url, href)
                documents.extend(await scrape_links_recursively(child_url, visited, depth+1, max_depth))

    except Exception as e:
        print(f"[SCRAPE ERROR] {url}: {e}")
    return documents


# async def scrape_single_page(url: str):
#     documents = []
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(url, timeout=10)
#             soup = BeautifulSoup(response.text, "html.parser")
#             text = soup.get_text(separator="\n", strip=True)
#             print(f"[SCRAPING] {url} - Text Length: {len(text)}")
#             documents.append((text, url))
#     except Exception as e:
#         print(f"[SCRAPE ERROR] {url}: {e}")
#     return documents


from playwright.async_api import async_playwright

async def scrape_single_page(url: str):
    documents = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=20000)
            await page.wait_for_load_state('networkidle')
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            print(f"[SCRAPING] {url} - Text Length: {len(text)}")
            documents.append((text, url))
            await browser.close()
    except Exception as e:
        print(f"[SCRAPE ERROR] {url}: {e}")
    return documents

async def parse_website(url: str, chunking_strategy="recursive"):
    pages = await scrape_single_page(url)
    print(pages)

    chunker = get_chunker(chunking_strategy)
    for text, page_url in pages:
        docs = chunker.create_documents([text], metadatas=[{"source": page_url}])
        vectorstore.add_documents(docs)

    vectorstore.persist()
    return {"status": "Website scraping completed", "pages": len(pages)}



