import json
from typing import Dict, List

import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from versed.file_handler import FileHandler


class VectorStore:
    def __init__(
        self,
        app,
        data_dir,
        default_collection_name: str,
        google_credentials
    ):
        self.app = app
        self.data_dir = data_dir
        self.chroma_metadata_path = data_dir / "metadata.json"
        self.metadata = { "collections": [] }

        # Initialize Chroma client with persistence
        self.chroma_client = chromadb.PersistentClient(
            path=str(data_dir )
        )

        self.metadata = { "collections": [] }
        self.update_metadata()

        # Retrieve the list of existing collection names
        existing_collections = self.get_collection_names()
        if self.chroma_client.count_collections() == 0:
            if default_collection_name not in existing_collections:
                self.add_collection(collection_name=default_collection_name, description="Default project for Versed.")
        else:
            # Load existing metadata
            with self.chroma_metadata_path.open("r") as file:
                try:
                    self.metadata = json.loads(file.read())
                except json.decoder.JSONDecodeError:
                    # Metadata is corrupted, delete all collections and start fresh?
                    self.metadata = { "collections": [] }
                    self.update_metadata()

        self.openai_client = None
        self.google_credentials = google_credentials
        self.file_handler = FileHandler(self.google_credentials)

    def initialise_openai_client(self, api_key) -> OpenAI | None:
        self.openai_client = OpenAI(api_key=self.app.api_key)

    def close_client(self) -> None:
        pass

    def update_metadata(self) -> bool:
        """
        Updates the metadata file.

        Returns
            bool: A boolean indicating whether the operation succeeded.
        """
        with self.chroma_metadata_path.open("w") as file:
            file.write(json.dumps(self.metadata) + "\n")
        return True

    def get_collection_names(self) -> List:
        return self.chroma_client.list_collections()
    
    def get_collection_stats(self, collection_name) -> Dict:
        if collection_name in self.get_collection_names():
            return self.chroma_client.get_collection_stats(collection_name)
        else:
            return {}

    def add_collection(self, collection_name: str, description: str = "A searchable file collection.", callback=None) -> bool:
        """Adds a collection to the vector store and updates metadata."""
        if collection_name not in self.get_collection_names():
            self.chroma_client.create_collection(name=collection_name, metadata={"description": description})
            # Update vector store metadata
            collection_metadata = {
                "collection_name": collection_name,
                "files": []
            }
            self.metadata["collections"].append(collection_metadata)
            self.update_metadata()
            if callback:
                callback()
            return True
        return False

    def remove_collection(self, collection_name: str, callback) -> bool:
        """Removes a collection from the vector store and updates metadata."""
        if collection_name in self.get_collection_names():
            self.chroma_client.delete_collection(name=collection_name)
            # Update vector store metadata
            self.metadata["collections"] = [
                c for c in self.metadata["collections"]
                if c["collection_name"] != collection_name
            ]
            self.update_metadata()
            if callback:
                callback()
            return True
        return False

    def add_files_to_collection(self, collection_name: str, files: List[Dict]) -> bool:
        """Adds files to a collection and updates the collection's metadata."""
        collection = self.chroma_client.get_collection(name=collection_name)
        for file in files:
            content = self.get_file_content(file)
            chunks = self.split_text(content, file["name"])
            embedding_docs = self.embed_chunks(chunks)
            # Add embeddings to the collection
            collection.add(
                documents=[doc["text"] for doc in embedding_docs],
                embeddings=[doc["embedding"] for doc in embedding_docs],
                metadatas=[{"file_name": doc["file_name"]} for doc in embedding_docs],
                ids=[f"{file['name']}_{i}" for i in range(len(chunks))]
            )
            # Update metadata
            for coll in self.metadata["collections"]:
                if coll["collection_name"] == collection_name:
                    if not file["name"] in coll["files"]:
                        coll["files"].append(file["name"])
                    break
        self.update_metadata()
        return True
    
    def remove_files_from_collection(self, collection_name: str, files: List[Dict]) -> bool:
        """
        Removes files from a collection, and updates the collections metadata accordingly.

        Returns
            bool: A boolean indicating whether the operation succeeded.
        """
        pass

    def search_collections(self, collections: List[str], user_query: str) -> List[Dict]:
        """Searches collections for similar vectors and returns their text content."""
        query_embedding = self.embed_texts([user_query])[0]
        similar_docs = []
        for collection_name in collections:
            collection = self.chroma_client.get_collection(name=collection_name)
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=3,
                include=["documents", "metadatas"]
            )
            if results["documents"]:
                hits = [
                    {"text": doc, "file_name": meta["file_name"]}
                    for doc, meta in zip(results["documents"][0], results["metadatas"][0])
                ]
                similar_docs.append({
                    "collection": collection_name,
                    "hits": hits
                })
        return similar_docs

    def get_file_content(self, file) -> str:
        return self.file_handler.get_file_content(file)

    async def chunk_file(self, file_contents: str) -> List[str]:
        """
        """
        long_context = f"""
        <document>
        {file_contents}
        </document>
        """

        chunking_instructions = ""

        response = await self.openai_client.chat.completions.create(
            messages=[
                {"role": "system", "content": long_context},
                {"role": "user", "content": chunking_instructions},
            ],
            model="gpt-4o-mini",
        )
        return response.choices[0].message.content
    
    def split_text(self, text, file_name, chunk_size=1000, overlap=0) -> List[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            is_separator_regex=False,
            separators=[
                ".\n\n",
                "\n\n",
                ".\n",
                "\n",
                ".",
                ",",
                " ",
                "\u200b",  # Zero-width space
                "\uff0c",  # Fullwidth comma
                "\u3001",  # Ideographic comma
                "\uff0e",  # Fullwidth full stop
                "\u3002",  # Ideographic full stop
                "",
            ],
        )

        chunks = text_splitter.split_text(text)
        return [
            {"text": x, "file_name": file_name} for x in chunks
        ]
    
    def embed_texts(self, texts: List[str]) -> List:
        response = self.openai_client.embeddings.create(
            input=texts,
            model="text-embedding-3-small",
            dimensions=1024
        )

        embeddings = [x.embedding for x in response.data]

        return embeddings

    def embed_chunks(self, chunks: List[Dict]):
        """
        Embeds a list of chunks and returns a dictionary associating each
        text with its embedding.

        Returns:
            Dict: {
                "text": str: The chunk text,
                "embedding": List[float]: The chunk embedding.
            }
        """
        chunk_texts = [x["text"] for x in chunks]

        chunk_embeddings = self.embed_texts(chunk_texts)

        chunk_documents = []
        for i, chunk_embedding in enumerate(chunk_embeddings):
            chunk_document = { 
                "text": chunks[i]["text"],
                "embedding": chunk_embedding,
                "file_name": chunks[i]["file_name"]
            }
            chunk_documents.append(chunk_document)

        return chunk_documents
