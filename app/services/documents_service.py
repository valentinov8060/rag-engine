import os
import shutil
import uuid
from fastapi import HTTPException, UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.configs.logger import logger
from app.configs.settings import settings

class DocumentsService:
    def __init__(self):
        self.qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        self.collection_name = settings.COLLECTION_NAME
        self.temp_dir = "temp_files"
        os.makedirs(self.temp_dir, exist_ok=True)

    def _extract_text(self, file_path: str, ext: str) -> str:
        text = ""
        if ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
        elif ext in [".docx", ".doc"]:
            from docx import Document
            doc = Document(file_path)
            for p in doc.paragraphs:
                text += p.text + "\n"
        return text

    # Private method for ingest_document method
    def _chunk_text(self, text: str) -> list:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return splitter.split_text(text)

    async def _save_to_vector_db(self, chunks: list, filename: str, source_id: str) -> int:
        # Check if the collection exists, if not, create it
        collections = self.qdrant_client.get_collections()
        if self.collection_name not in [c.name for c in collections.collections]:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
            )

        embeddings_model = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        vectors = embeddings_model.embed_documents(chunks)

        points = []
        for i, chunk in enumerate(chunks):
            # Generate a unique string ID for each chunk and convert it to a valid UUID
            unique_string_id = f"{source_id}-chunk-{i}"
            qdrant_valid_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string_id))

            points.append(
                models.PointStruct(
                    id=qdrant_valid_uuid,
                    vector=vectors[i],
                    payload={"text": chunk, "file_name": filename, "source_id": source_id}
                )
            )

        self.qdrant_client.upsert(collection_name=self.collection_name, points=points)
        return len(points)

    async def ingest_document(self, file: UploadFile, source_id: str) -> int:
        file_extension = os.path.splitext(file.filename)[1].lower()
        temp_file_path = os.path.join(self.temp_dir, f"{source_id}{file_extension}")

        try:
            # 1. Save binary stream from File Upload to local storage (Save RAM)
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # 2. Extract text from the file based on its type
            raw_text = self._extract_text(temp_file_path, file_extension)
            if not raw_text.strip():
                raise ValueError("The document does not contain readable text.")

            # 3. Text Chunking
            chunks = self._chunk_text(raw_text)

            # 4. Generate Embeddings & Push to Qdrant Cloud
            total_points = await self._save_to_vector_db(chunks, file.filename, source_id)
            return total_points

        except Exception as e:
            logger.error(f"Failed to respond to documents/ingest request. Error occurred while processing document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

        finally:
            # Guarantee cleanup of temporary files from the server's hard disk
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
