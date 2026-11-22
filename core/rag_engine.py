import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from core.vector_store import build_vector_store, load_vector_store, get_retriever


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
    )


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def _make_rag_chain(retriever):
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant. Answer the user's question
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say:
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}"),
    ])

    return (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | get_llm()
        | StrOutputParser()
    )


def build_rag_chain(transcript: str, meeting_id: str):
    """Create a RAG chain isolated to the supplied meeting ID."""
    vector_store = build_vector_store(transcript, meeting_id)
    return _make_rag_chain(get_retriever(vector_store, k=4))


def load_rag_chain(meeting_id: str):
    """Load the existing isolated RAG collection for one meeting."""
    vector_store = load_vector_store(meeting_id)
    return _make_rag_chain(get_retriever(vector_store, k=4))


def ask_question(rag_chain, question: str) -> str:
    return rag_chain.invoke(question)
