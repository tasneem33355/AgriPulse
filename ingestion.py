"""
AgriPulse RAG Knowledge Ingestion Pipeline.
Loads, chunks, embeds, and indexes engineering documentation into ChromaDB:
- Industrial standards & technical pump manuals (data_docs/*.pdf)
- Domain FMEA specifications (docs/fmea/*.md)
- Machine architecture & hardware reference (docs/*.md)
- Application schemas & diagnostic rules (app/schemas.py, app/diagnostics.py)
"""

import os
import glob
from langchain_community.document_loaders import PyPDFDirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DOCS_DIR = "./data_docs"
FMEA_DIR = "./docs/fmea"
CORE_DOCS = [
    "./docs/AI_Technical_Architecture.md",
    "./docs/Hardware_Team_Reference.md"
]
CODE_FILES = [
    "./app/schemas.py",
    "./app/diagnostics.py"
]
DB_DIR = "./chroma_db"

def run_ingestion():
    documents = []

    # 1. LOAD TECHNICAL PDF MANUALS
    if os.path.exists(DOCS_DIR):
        print(f"Loading PDF manuals from '{DOCS_DIR}'...")
        pdf_loader = PyPDFDirectoryLoader(DOCS_DIR)
        pdf_docs = pdf_loader.load()
        for doc in pdf_docs:
            doc.metadata["document_type"] = "technical_manual"
        documents.extend(pdf_docs)
        print(f"  Loaded {len(pdf_docs)} PDF page(s).")
    else:
        print(f"Directory '{DOCS_DIR}' not found. Skipping PDF manuals.")

    # 2. LOAD FMEA SPECIFICATIONS (Markdown)
    if os.path.exists(FMEA_DIR):
        print(f"Loading FMEA specifications from '{FMEA_DIR}'...")
        fmea_files = glob.glob(os.path.join(FMEA_DIR, "*.md"))
        for fpath in fmea_files:
            loader = TextLoader(fpath, encoding="utf-8")
            fdocs = loader.load()
            for doc in fdocs:
                doc.metadata["source"] = fpath
                doc.metadata["document_type"] = "fmea_specification"
            documents.extend(fdocs)
            print(f"  Loaded FMEA: {os.path.basename(fpath)}")

    # 3. LOAD SYSTEM ARCHITECTURE & BOM
    print("Loading system architecture & engineering specifications...")
    for fpath in CORE_DOCS:
        if os.path.exists(fpath):
            loader = TextLoader(fpath, encoding="utf-8")
            cdocs = loader.load()
            for doc in cdocs:
                doc.metadata["source"] = fpath
                doc.metadata["document_type"] = "engineering_architecture"
            documents.extend(cdocs)
            print(f"  Loaded Architecture: {os.path.basename(fpath)}")

    # 4. LOAD RELEVANT SYSTEM CODE SCHEMAS
    print("Loading application diagnostic & schema definitions...")
    for fpath in CODE_FILES:
        if os.path.exists(fpath):
            loader = TextLoader(fpath, encoding="utf-8")
            codedocs = loader.load()
            for doc in codedocs:
                doc.metadata["source"] = fpath
                doc.metadata["document_type"] = "system_code_definition"
            documents.extend(codedocs)
            print(f"  Loaded Code: {os.path.basename(fpath)}")

    if not documents:
        print("No documents found to ingest!")
        return

    print(f"\nTotal loaded documents/sections: {len(documents)}")

    # 5. CHUNK DOCUMENTS
    print("Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=750,
        chunk_overlap=120,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"Generated {len(chunks)} text chunks.")

    # 6. EMBEDDING & VECTOR STORAGE
    print("Initializing embedding model (sentence-transformers/all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print(f"Persisting vectors into '{DB_DIR}'...")
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    print(f"Ingestion successfully completed! Vector DB saved to '{DB_DIR}'.")

if __name__ == "__main__":
    run_ingestion()
