from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
from loguru import logger
from tempfile import NamedTemporaryFile
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import LanceDB
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI

router = APIRouter(prefix="/api/v1/vectorstore")

BUCKET_NAME = os.environ.get('AWS_BUCKET')
VECTORSTORE_S3_URI = f"s3://{BUCKET_NAME}/onboarding/vectorstore"

# Initialize embeddings model
embeddings = OpenAIEmbeddings()

# Initialize language model
llm = ChatOpenAI()

# Initialize LanceDB vector store
db = LanceDB(
    uri=VECTORSTORE_S3_URI,
    table='documents',
    embedding_function=embeddings.embed_query
)

@router.post("/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload PDF files and create/update the vector store using LangChain and LanceDB.
    """
    try:
        for file in files:
            # Save the uploaded file temporarily
            with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file.file.read())
                temp_file_path = temp_file.name

            # Load document content
            loader = PyPDFLoader(temp_file_path)
            documents = loader.load()

            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            docs = text_splitter.split_documents(documents)

            # Add documents to vector store
            db.add_documents(documents=docs)

            # Clean up temporary file
            os.remove(temp_file_path)

        return {"message": "Documents uploaded and processed successfully"}

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask-question")
async def ask_question(question: str):
    """
    Endpoint to receive a question, retrieve the most similar chunks
    from the vector store, and generate a response using LangChain and LanceDB.
    """
    try:
        # Retrieve similar documents from vector store
        similar_docs = db.similarity_search(query=question, k=5)

        # Concatenate the content of the similar documents
        context = "\n\n".join([doc.page_content for doc in similar_docs])

        # Create a prompt with the similar documents
        prompt = f"""
        Use the following context to answer the question.

        Context:
        {context}

        Question:
        {question}
        """

        # Generate the answer
        answer = llm.predict(prompt)

        return {"answer": answer.strip()}

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))