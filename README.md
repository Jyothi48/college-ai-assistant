# 🎓 College AI Assistant

An AI-Based College Academic Assistant that helps students get answers from college documents, generate study plans, modify study plans, and ask general academic questions.

## 📌 Project Overview

The College AI Assistant uses Artificial Intelligence, Retrieval-Augmented Generation (RAG), and an agentic workflow to provide useful academic assistance to students.

The system can understand the type of question asked and route it to the appropriate part of the application.

## ✨ Features

- 📚 **College Document Q&A**
  - Answers questions using provided college documents.
  - Retrieves relevant information from the documents.
  - Provides document source and page information when available.

- 📅 **Study Plan Generation**
  - Creates personalized study plans based on the student's request.

- 🔄 **Study Plan Modification**
  - Allows students to modify an existing study plan through follow-up requests.

- 🤖 **General Academic Questions**
  - Answers general academic questions that are not related to the uploaded college documents.

- 🧠 **Agentic Workflow**
  - Uses LangGraph to classify questions and route them to the appropriate task.

## 🏗️ System Architecture

```text
                    Student Question
                           │
                           ▼
                   ┌─────────────────┐
                   │   LangGraph     │
                   │ Question Router │
                   └────────┬────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        DOCUMENT         PLANNER        GENERAL
             │              │              │
             ▼              ▼              ▼
        ChromaDB       Study Plan       General
        Retrieval      Generation       LLM Answer
             │              │
             ▼              ▼
          Groq LLM      Updated Plan
             │
             ▼
        Final Answer
             │
             ▼
        Streamlit UI

Project Files
| File                                                     | Description                                         |
| -------------------------------------------------------- | --------------------------------------------------- |
| `app.py`                                                 | Streamlit user interface                            |
| `backend.py`                                             | RAG, LangGraph workflow, retrieval and LLM logic    |
| `requirements.txt`                                       | Required Python packages                            |
| `MSE I Timetable_ISE.pdf`                                | College academic document                           |
| `DEPT_Practical SEE Time Table _Dec 2025_III Sem.pdf`    | Practical examination timetable                     |
| `14ENGR09D2_B.Tech._IS_2023-04_Regulations_Syllabus.pdf` | B.Tech Information Science regulations and syllabus |

🚀 How to Run
1. Clone the repository
git clone YOUR_GITHUB_REPOSITORY_URL
cd college-ai-assistant
2. Install the required packages
pip install -r requirements.txt
3. Set the Groq API key

Set your Groq API key as an environment variable.

GROQ_API_KEY=your_api_key

Do not share or upload your API key publicly.

4. Run the application
streamlit run app.py

The application will open in your browser.

💡 Example Questions
What is the course code for Data Structures?

What are the subjects in 3rd semester?

Create a 5-day study plan for Data Structures.

Change Day 3 to 3 hours and add a revision session on Day 5.

What is the difference between Python and Java?
🎯 Project Objective

The objective of this project is to develop an AI-powered academic assistant that can provide students with college-specific information and personalized study planning through an easy-to-use conversational interface.
