import os
import streamlit as st
from typing import TypedDict

# Get Groq API key from Streamlit Secrets
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END


# -----------------------------
# 1. Load college documents
# -----------------------------

pdf_files = [
    "MSE I Timetable_ISE.pdf",
    "DEPT_Practical SEE Time Table _Dec 2025_III Sem.pdf",
    "14ENGR09D2_B.Tech._IS_2023-04_Regulations_Syllabus.pdf"
]

all_documents = []

for pdf_file in pdf_files:
    if not os.path.exists(pdf_file):
        continue

    reader = PdfReader(pdf_file)

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text()

        if text and text.strip():
            all_documents.append({
                "text": text,
                "page": page_number + 1,
                "source": pdf_file
            })


# -----------------------------
# 2. Split documents
# -----------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)

page_chunks = []

for doc in all_documents:
    chunks = text_splitter.split_text(doc["text"])

    for chunk in chunks:
        page_chunks.append({
            "text": chunk,
            "page": doc["page"],
            "source": doc["source"]
        })


# -----------------------------
# 3. Embeddings + ChromaDB
# -----------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

texts = [item["text"] for item in page_chunks]

metadatas = [
    {
        "page": item["page"],
        "source": item["source"]
    }
    for item in page_chunks
]

vectorstore = Chroma.from_texts(
    texts=texts,
    embedding=embeddings,
    metadatas=metadatas,
    collection_name="college_documents"
)


# -----------------------------
# 4. Groq LLM
# -----------------------------

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


# -----------------------------
# 5. Document search
# -----------------------------

def keyword_search_documents(keyword):

    results = []

    keyword = keyword.lower()

    for doc in all_documents:

        if keyword in doc["text"].lower():

            results.append({
                "text": doc["text"],
                "page": doc["page"],
                "source": doc["source"]
            })

    return results


def search_college_documents(question):

    question_lower = question.lower()

    semester_keywords = {
        "third semester": "iii semester",
        "3rd semester": "iii semester",
        "iii semester": "iii semester",
        "fourth semester": "iv semester",
        "4th semester": "iv semester",
        "iv semester": "iv semester",
        "fifth semester": "v semester",
        "5th semester": "v semester",
        "v semester": "v semester",
        "sixth semester": "vi semester",
        "6th semester": "vi semester",
        "vi semester": "vi semester",
        "seventh semester": "vii semester",
        "7th semester": "vii semester",
        "vii semester": "vii semester",
        "eighth semester": "viii semester",
        "8th semester": "viii semester",
        "viii semester": "viii semester"
    }

    for phrase, keyword in semester_keywords.items():

        if phrase in question_lower:

            results = keyword_search_documents(keyword)

            if results:
                return results[:5]

    if "mse" in question_lower or "mid semester" in question_lower:

        results = keyword_search_documents("MSE")

        if results:
            return results[:5]

    results = vectorstore.similarity_search(
        question,
        k=5
    )

    return [
        {
            "text": result.page_content,
            "page": result.metadata.get("page"),
            "source": result.metadata.get("source")
        }
        for result in results
    ]


# -----------------------------
# 6. Document answering
# -----------------------------

def ask_college_assistant(question):

    results = search_college_documents(question)

    context = "\n\n".join([
        f"""
Source: {result['source']}
Page: {result['page']}

{result['text']}
"""
        for result in results[:3]
    ])

    prompt = f"""
You are an AI Academic Assistant for NMAM Institute of Technology.

Answer the student's question using ONLY the information
provided in the document context.

Rules:
1. Do not make up information.
2. If the answer is not available in the context, say:
"I could not find this information in the provided college documents."
3. Give a simple and clear answer.
4. Mention the document source and page number when possible.

DOCUMENT CONTEXT:
{context}

STUDENT QUESTION:
{question}

ANSWER:
"""

    response = llm.invoke(prompt)

    return response.content


# -----------------------------
# 7. LangGraph state
# -----------------------------

class CollegeAssistantState(TypedDict):
    question: str
    intent: str
    answer: str
    study_plan: str


# -----------------------------
# 8. Question classifier
# -----------------------------

def classify_question(state):

    question = state["question"]

    prompt = f"""
Classify the student's question into exactly ONE category:

DOCUMENT
PLANNER
GENERAL

DOCUMENT = questions about college documents, syllabus,
regulations, courses, exams, timetables, attendance, credits, etc.

PLANNER = requests to create or modify a study timetable,
study plan, revision plan, or preparation schedule.

GENERAL = other questions that do not belong to the above categories.

Student question:
{question}

Return ONLY one word:
DOCUMENT
PLANNER
or
GENERAL
"""

    response = llm.invoke(prompt)

    intent = response.content.strip().upper()

    if intent not in ["DOCUMENT", "PLANNER", "GENERAL"]:
        intent = "GENERAL"

    return {"intent": intent}


# -----------------------------
# 9. Route question
# -----------------------------

def route_question(state):

    intent = state["intent"]

    if intent == "DOCUMENT":
        return "document"

    elif intent == "PLANNER":
        return "planner"

    else:
        return "general"


# -----------------------------
# 10. Nodes
# -----------------------------

def document_node(state):

    answer = ask_college_assistant(
        state["question"]
    )

    return {
        "answer": answer
    }


def planner_node(state):

    question = state["question"]

    previous_plan = state.get(
        "study_plan",
        ""
    )

    if previous_plan:

        prompt = f"""
You are a college study planner.

The student already has the following study plan:

{previous_plan}

The student now wants to modify it.

Student request:
{question}

Modify the existing plan according to the request.

Rules:
1. Keep the parts that the student did not ask to change.
2. Make only the requested changes.
3. Show the complete updated study plan.
4. Keep it simple and practical.
"""

    else:

        prompt = f"""
You are a college study planner.

Create a practical and simple study plan based on the student's request.

Student request:
{question}

Give the plan in a clear format with:
- Day/date if provided
- Subject or topic
- Study duration
- Short break/revision suggestions

Do not invent specific exam dates unless the student provides them.
"""

    response = llm.invoke(prompt)

    new_plan = response.content

    return {
        "answer": new_plan,
        "study_plan": new_plan
    }


def general_node(state):

    question = state["question"]

    prompt = f"""
You are a helpful college academic assistant.

Answer the student's general question clearly and simply.

Student question:
{question}
"""

    response = llm.invoke(prompt)

    return {
        "answer": response.content
    }


# -----------------------------
# 11. Build LangGraph
# -----------------------------

graph_builder = StateGraph(
    CollegeAssistantState
)

graph_builder.add_node(
    "classify",
    classify_question
)

graph_builder.add_node(
    "document",
    document_node
)

graph_builder.add_node(
    "planner",
    planner_node
)

graph_builder.add_node(
    "general",
    general_node
)

graph_builder.add_edge(
    START,
    "classify"
)

graph_builder.add_conditional_edges(
    "classify",
    route_question,
    {
        "document": "document",
        "planner": "planner",
        "general": "general"
    }
)

graph_builder.add_edge(
    "document",
    END
)

graph_builder.add_edge(
    "planner",
    END
)

graph_builder.add_edge(
    "general",
    END
)

college_assistant_graph = graph_builder.compile()


# -----------------------------
# 12. Final assistant function
# -----------------------------

def college_ai_assistant(
    question,
    study_plan=""
):

    result = college_assistant_graph.invoke({

        "question": question,

        "intent": "",

        "answer": "",

        "study_plan": study_plan
    })

    return {
        "intent": result["intent"],

        "answer": result["answer"],

        "study_plan": result.get(
            "study_plan",
            study_plan
        )
    }
