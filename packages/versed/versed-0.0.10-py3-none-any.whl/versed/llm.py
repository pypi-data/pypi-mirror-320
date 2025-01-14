from openai import OpenAI
from typing import List

class LLMHandler:

    def __init__(self, api_key, vector_store):
        self.client = OpenAI(api_key=api_key)
        self.vector_store = vector_store

    async def generate_completion(self, user_message: str, collections: List) -> str:
        if collections:
            return await self._doc_chat_completion(
                user_message=user_message,
                collections=collections
            )
        else:
            return await self._chat_completion(user_message=user_message)
        
    async def _chat_completion(self, user_message: str) -> str:
        """
        Generate bot response.
        """
        system_message = """\
        Answer the user's query using the message history (if any is provided).
        If you do not know the answer, say "I do not know."
        Do not lie.
        """

        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            model="gpt-4o",
        )
        
        assistant_message = response.choices[0].message.content
        return assistant_message

    async def _doc_chat_completion(self, user_message: str, collections: List) -> str:
        """
        Generate bot response.
        """
        system_message = """\
        Use the provided context, and not your prior knowledge, to answer the user's query.
        When answering, specify the name of the file that you are referencing.
        If you cannot find an answer in the context, say "I cannot find relevant material to answer your query."
        """

        similar_docs = self.vector_store.search_collections(collections, user_message)
        context = self._build_context_string(similar_docs)

        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "system",
                    "content": context
                },
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            model="gpt-4o",
        )
        
        assistant_message = response.choices[0].message.content
        return assistant_message
    
    def _build_context_string(self, similar_docs):
        context_string = """\
        Here is the context in <context> XML tags.
        """

        for collection_hits in similar_docs:
            for hit in collection_hits["hits"]:
                hit_text = hit["text"]
                file_name = hit["file_name"]
                context = f"<context file_name=\"{file_name}\">\n{hit_text}\n</context>\n"
                context_string += context

        return context_string
