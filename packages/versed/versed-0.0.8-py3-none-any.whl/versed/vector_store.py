import json
from typing import Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from pymilvus import MilvusClient, FieldSchema, DataType, CollectionSchema
from versed.file_handler import FileHandler

class VectorStore:

    def __init__(
        self,
        app,
        data_dir,
        default_collection_name,
        google_credentials
    ):
        self.app = app

        milvus_db_path = data_dir / "milvus.db"
        self.milvus_metadata_path = data_dir / "metadata.json"
        self.milvus_uri = f"{milvus_db_path}"

        self.fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=100),
        ]

        self.milvus_client = MilvusClient(uri=self.milvus_uri)
        self.metadata = { "collections": [] }

        if not self.milvus_client.list_collections():
            if not self.milvus_client.has_collection(collection_name=default_collection_name):
                self.add_collection(collection_name=default_collection_name, description="Default project for Versed.")
        else:
            # Load metadata
            with self.milvus_metadata_path.open("r") as file:
                try:
                    self.metadata = json.loads(file.read())
                except json.decoder.JSONDecodeError:
                    # Metadata is corrupted, delete all collections and start fresh?
                    self.metadata = { "collections": [] }

        self.openai_client = None
        self.google_credentials = google_credentials

        self.file_handler = FileHandler(self.google_credentials)

    def initialise_openai_client(self, api_key) -> OpenAI | None:
        self.openai_client = OpenAI(api_key=self.app.api_key)

    def close_client(self) -> None:
        self.milvus_client.close()

    def update_metadata(self) -> bool:
        """
        Updates the metadata file.

        Returns
            bool: A boolean indicating whether the operation succeeded.
        """
        with self.milvus_metadata_path.open("w") as file:
            file.write(json.dumps(self.metadata) + "\n")
        return True

    def get_collection_names(self) -> List:
        return [x["collection_name"] for x in self.metadata["collections"]]
    
    def get_collection_stats(self, collection_name) -> Dict:
        if collection_name in self.get_collection_names():
            return self.milvus_client.get_collection_stats(collection_name)
        else:
            return {}

    def add_collection(self, collection_name: str, description: str="A searchable file collection.", callback=None) -> bool:
        """
        Adds a collection to the vector store, and its metadata to the metadata file.

        Returns
            bool: A boolean indicating whether the operation succeeded.
        """
        if not collection_name in self.milvus_client.list_collections():
            schema = CollectionSchema(self.fields, description=description, auto_id=True)

            # Add indexes
            index_params = self.milvus_client.prepare_index_params()
            index_params.add_index(
                field_name="embedding", 
                index_type="AUTOINDEX",
                metric_type="COSINE"
            )

            self.milvus_client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params
            )

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
        else:
            return False

    def remove_collection(self, collection_name: str, callback=None) -> bool:
        """
        Removes a collection from the vector store, and its metadata from the metadata file.

        Returns
            bool: A boolean indicating whether the operation succeeded.
        """
        if collection_name in self.milvus_client.list_collections():
            response = self.milvus_client.drop_collection(collection_name=collection_name)

            # Update vector store metadata
            self.metadata["collections"] = [
                c for c in self.metadata["collections"] 
                if c["collection_name"] != collection_name
            ]
            self.update_metadata()

            if callback:
                callback()
            return True
        else:
            return False

    def add_files_to_collection(self, collection, files) -> bool:
        """
        Adds files to a collection, and updates the collections metadata accordingly.

        Returns
            bool: A boolean indicating whether the operation succeeded.
        """
        def add_to_collection(collection, data):
            # Insert into Milvus collection
            response = self.milvus_client.insert(collection_name=collection, data=data)
            response_dict = dict(response)

            # Check all entities added ?
            # if response_dict["insert_count"] != len(data):
            #     pass
            # self.app.push_screen(DebugScreen(json_response))

            # try:
            #     response = self.milvus_client.insert(collection_name=collection, data=data)
            # except Exception as e:
            #     self.app.push_screen(DebugScreen(e))
            
            return
        
        for file in files:
            content = self.get_file_content(file)
            chunks = self.split_text(content, file["name"])
            vectors = self.embed_chunks(chunks)
            # Handle metadata here
                # Add file name to files key of collection entry in self.metadata
            add_to_collection(collection, vectors)

    def remove_files_from_collection(self, collection: str, files: List[Dict]) -> bool:
        """
        Removes files from a collection, and updates the collections metadata accordingly.

        Returns
            bool: A boolean indicating whether the operation succeeded.
        """
        pass

    def search_collections(self, collections: List[str], user_query: str) -> List[Dict]:
        """
        Search a collection for similar vectors and return their text content.
        """
        query_embedding = self.embed_texts([user_query])

        search_params = {
            "params": {}
        }

        similar_docs = []

        for collection in collections:
            # Search with limit
            response = self.milvus_client.search(
                collection_name=collection,
                data=query_embedding,
                anns_field="embedding",
                limit=3,
                output_fields=["text", "file_name"]
            )

            if response[0]: # Non-empty response
                similar_docs.append({
                    "collection": collection,
                    "hits": response[0]
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
