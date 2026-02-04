import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate


# ---------- CONFIG ----------
DOC_PATHS = [os.path.join(os.getcwd(), 'data', f) for f in os.listdir('data')]
VECTOR_DIR = "faiss_index"

CHAT_MODEL = "llama3.2:3b"
EMBED_MODEL = "nomic-embed-text"


app = Flask(__name__)
CORS(app)

retrieval_chain = None  # global cache

# ---------- HELPERS ----------
def build_vectorstore():
    all_docs = []
    for path in DOC_PATHS:
        if os.path.exists(path):
            loader = Docx2txtLoader(path)
            all_docs.extend(loader.load())
        else:
            print(f"WARNING: File not found: {path}")

    if not all_docs:
        raise ValueError("No documents loaded. Check DOC_PATHS.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(all_docs)

    # ✅ USE EMBEDDING MODEL
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    vectorstore = FAISS.from_documents(splits, embeddings)
    vectorstore.save_local(VECTOR_DIR)
    return vectorstore

def get_or_create_chain():
    global retrieval_chain
    if retrieval_chain is not None:
        return retrieval_chain

    # ✅ USE EMBEDDING MODEL
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    if os.path.exists(VECTOR_DIR):
        vectorstore = FAISS.load_local(
            VECTOR_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        vectorstore = build_vectorstore()

    # ✅ USE CHAT MODEL
    llm = ChatOllama(
        model=CHAT_MODEL,
        temperature=0,
        num_ctx=4096
    )


    system_prompt = """
            You are a helpful assistant.

            Answer ONLY using the provided context.
            The answer must be EXACTLY based on the context.

            RULES:
            - Use very simple language suitable for farmers.
            - Do NOT add extra information.
            - If information is missing, say:
            "Based on available information..."
            and give conservative guidance.
            - Never hallucinate.
            - Don't tell out of the context. if something is not mentioned in the context, say "i am not for this information".

            CONTEXT:
            {context}
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}")
        ]
    )

    from langchain_core.runnables import RunnableLambda, RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    retrieval_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "input": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return retrieval_chain

# ---------- ROUTES ----------
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Chatbot backend running"})


@app.route("/rebuild_index", methods=["POST"])
def rebuild_index():
    """Rebuild FAISS index from the two DOCX files."""
    build_vectorstore()
    # reset global chain so it reloads next time
    global retrieval_chain
    retrieval_chain = None
    return jsonify({"message": "Index rebuilt from DOCX files"})


@app.route("/chat", methods=["POST"])
def chat():
    """Body: {\"query\": \"your question\"}"""
    data = request.get_json(force=True)
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Field 'query' is required"}), 400

    chain = get_or_create_chain()
    answer = chain.invoke(query)

    return jsonify({"answer": answer})


if __name__ == "__main__":
    # First run may take some time to build index
    app.run(host="0.0.0.0", port=5000, debug=True)
