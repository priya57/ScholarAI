#!/usr/bin/env python3
"""
ScholarAI CLI - Command line interface for managing the RAG system
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.config import settings
from src.core.document_processor import DocumentProcessor
from src.core.vector_store import VectorStoreManager
from src.core.rag_engine import RAGEngine

def init_components():
    """Initialize system components"""
    document_processor = DocumentProcessor(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    
    vector_store_manager = VectorStoreManager(
        persist_directory=settings.chroma_persist_directory,
        collection_name=settings.collection_name,
        openai_api_key=settings.openai_api_key
    )
    
    rag_engine = RAGEngine(
        vector_store_manager=vector_store_manager,
        openai_api_key=settings.openai_api_key,
        model_name=settings.llm_model
    )
    
    return document_processor, vector_store_manager, rag_engine

def ingest_documents(directory_path: str):
    """Ingest documents from a directory"""
    if not os.path.exists(directory_path):
        print(f"Error: Directory {directory_path} does not exist")
        return
    
    print("Initializing components...")
    document_processor, vector_store_manager, _ = init_components()
    
    print(f"Processing documents from: {directory_path}")
    documents = document_processor.process_directory(directory_path)
    
    if documents:
        print(f"Adding {len(documents)} document chunks to vector store...")
        vector_store_manager.add_documents(documents)
        print("✅ Document ingestion completed successfully!")
    else:
        print("❌ No documents found or processed")

def query_system(question: str):
    """Query the RAG system"""
    print("Initializing components...")
    _, _, rag_engine = init_components()
    
    print(f"Question: {question}")
    print("Searching for relevant information...")
    
    result = rag_engine.query(question)
    
    print("\n" + "="*50)
    print("ANSWER:")
    print("="*50)
    print(result["answer"])
    
    if result["sources"]:
        print("\n" + "="*50)
        print("SOURCES:")
        print("="*50)
        for i, source in enumerate(result["sources"], 1):
            print(f"{i}. {source['file_name']}")
            print(f"   Preview: {source['content_preview']}")
            print()

def reset_system():
    """Reset the vector store"""
    print("Initializing components...")
    _, vector_store_manager, _ = init_components()
    
    confirm = input("Are you sure you want to reset the vector store? (y/N): ")
    if confirm.lower() == 'y':
        vector_store_manager.reset_collection()
        print("✅ Vector store reset successfully!")
    else:
        print("Reset cancelled")

def show_stats():
    """Show system statistics"""
    print("Initializing components...")
    _, vector_store_manager, _ = init_components()
    
    count = vector_store_manager.get_collection_count()
    print(f"📊 System Statistics:")
    print(f"   Total document chunks: {count}")
    print(f"   Collection name: {settings.collection_name}")
    print(f"   Chunk size: {settings.chunk_size}")
    print(f"   Model: {settings.llm_model}")

def main():
    parser = argparse.ArgumentParser(description="ScholarAI RAG System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents from directory")
    ingest_parser.add_argument("directory", help="Directory containing documents to ingest")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query the RAG system")
    query_parser.add_argument("question", help="Question to ask the system")
    
    # Reset command
    subparsers.add_parser("reset", help="Reset the vector store")
    
    # Stats command
    subparsers.add_parser("stats", help="Show system statistics")
    
    args = parser.parse_args()
    
    if args.command == "ingest":
        ingest_documents(args.directory)
    elif args.command == "query":
        query_system(args.question)
    elif args.command == "reset":
        reset_system()
    elif args.command == "stats":
        show_stats()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()