import os
from fastapi import HTTPException
from qdrant_client.http import models
from openai import AsyncOpenAI
from qdrant_client import QdrantClient
from app.configs.logger import logger
from app.configs.settings import settings

groq_client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

class ChatsService:
    def __init__(self):
        self.qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        self.collection_name = settings.COLLECTION_NAME
        self.temp_dir = "temp_files"
        os.makedirs(self.temp_dir, exist_ok=True)


    async def post_chat_question(self, source_id: str, question: str) -> str:
        try:
            # 1. Generate Embedding for User Questions
            openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            embedding_response = await openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=question
            )
            query_vector = embedding_response.data[0].embedding

            # 2. Find Relevant Chunks in Qdrant based on user source_id
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="source_id",
                            match=models.MatchValue(value=str(source_id))
                        )
                    ]
                ),
                limit=3,
                with_payload=True
            )

            # If no documents are found for that user
            if not search_results:
                fallback_prompt = (
                    "You are a helpful Q&A assistant.\n"
                    "Current status: The user is asking about their documents, but the vector database is completely EMPTY (no documents uploaded yet).\n"
                    "Your tasks:\n"
                    "1. Detect the language used in the user's question below.\n"
                    "2. Refuse to answer the core question, and inform them that no documents are found. Instruct them to upload a PDF document first.\n"
                    "3. Respond strictly in the SAME LANGUAGE used by the user (e.g., reply in Indonesian if asked in Indonesian, English if in English, etc.)."
                )

                llm_response = await groq_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": fallback_prompt},
                        {"role": "user", "content": question}
                    ],
                    temperature=0.3
                )
                return llm_response.choices[0].message.content

            # 3. Extract the text of a document into a single contextual unit.
            context_chunks = []
            referenced_files = set()
            
            for hit in search_results:
                payload = hit.payload
                if payload and "text" in payload:
                    context_chunks.append(payload["text"])
                    if "file_name" in payload:
                        referenced_files.add(payload["file_name"])

            context_text = "\n\n".join(context_chunks)

            # 4. Establish a Strict Warning System (Prevent LLM Hallucinations)
            system_prompt = (
                "You are a helpful Q&A assistant.\n"
                "Answer the user's question based ONLY on the RAG-CONTEXT below.\n"
                "Strict Rules:\n"
                "1. Rely ONLY on clear facts directly mentioned in the context. Do not assume or extrapolate.\n"
                "2. If the answer cannot be found in the context, respond strictly with a polite notification stating that the information is not found in the documents.\n"
                "3. Respond in the SAME LANGUAGE used by the user in their question (e.g., if asked in Indonesian, reply in Indonesian; if in English, reply in English).\n\n"
                f"=== RAG-CONTEXT ===\n{context_text}\n==================="
            )

            # 5. Perform Inference on Groq Cloud API using Llama 3.1 8B (Super Fast & Cost-Effective)
            model_name = os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant")
            llm_response = await groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.1
            )

            ai_answer = llm_response.choices[0].message.content

            # 6. Add a footer with referenced document links
            sources_footer = f"\n\n📚 _Referensi dokumen: {', '.join(referenced_files)}_"
            return ai_answer + sources_footer

        except Exception as e:
            logger.error(f"Failed to respond to post chats/question request. Error occurred while processing document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")