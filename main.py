import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

# ---------- CONFIG ----------
DOC_PATHS = [
    r"C:\Users\himan\Desktop\test_backend\Questions for Chatbot - 1.docx",
    r"C:\Users\himan\Desktop\test_backend\Questions for Chatbot - 2.docx"
]
VECTOR_DIR = "faiss_index"     # folder, not .pkl
MODEL_NAME = "llama3.2:3b" 

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

    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    vectorstore = FAISS.from_documents(splits, embeddings)
    vectorstore.save_local(VECTOR_DIR)
    return vectorstore

def get_or_create_chain():
    global retrieval_chain
    if retrieval_chain is not None:
        return retrieval_chain

    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    if os.path.exists(VECTOR_DIR):
        vectorstore = FAISS.load_local(
            VECTOR_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        vectorstore = build_vectorstore()

    llm = ChatOllama(model=MODEL_NAME)

    system_prompt = (
        """
                You are a Dairy Farmer Advisory Assistant.

                OBJECTIVE:
                Give the SHORTEST, MOST RELEVANT, and PRACTICAL answer possible
                using ONLY the provided data/context.

                STRICT RULES:
                1. Do NOT add greetings, fillers, apologies, or opinions.
                2. Do NOT repeat the question.
                3. Do NOT go out of context.
                4. Do NOT hallucinate facts, medicines, dosages, or prices.
                5. If input is unclear, infer the MOST LIKELY intent.
                6. If critical data is missing, give SAFE GENERAL advice only.
                7. When health is involved, choose the LOWEST-RISK guidance.
                8. Ask ONE clarification question ONLY if required to avoid harm.

                OUTPUT FORMAT (MANDATORY):
                - Direct answer. make sure you are not saying 'Direct answer'
                - Warning ONLY if necessary

                LANGUAGE:
                - Simple, farmer-friendly
                - No technical jargon
                - No AI references

                FAIL-SAFE:
                If data is insufficient, say:
                "Based on available information..."
                and give conservative guidance.

                GOAL:
                Help the farmer act correctly TODAY with minimum words and zero risk.

        """  

        "{context}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}")
        ]
    )

    # Create a simple chain using langchain_core
    from langchain_core.runnables import RunnableLambda, RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    # Format the retrieved documents into the prompt
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Create the chain
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
