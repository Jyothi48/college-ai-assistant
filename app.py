
import streamlit as st
from backend import college_ai_assistant

st.set_page_config(
    page_title="College AI Assistant",
    page_icon="🎓",
    layout="centered"
)

# ---------- Custom Styling ----------
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #666;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .feature-box {
        padding: 12px;
        border-radius: 10px;
        background-color: #f5f7fb;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ---------- Header ----------
st.markdown(
    '<div class="main-title">🎓 College AI Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your AI assistant for college academics, documents and study planning</div>',
    unsafe_allow_html=True
)


# ---------- Sidebar ----------
with st.sidebar:
    st.header("📌 Features")

    st.markdown("""
    <div class="feature-box">📚 College Document Q&A</div>
    <div class="feature-box">📅 Study Plan Generation</div>
    <div class="feature-box">🔄 Study Plan Modification</div>
    <div class="feature-box">🤖 General Academic Questions</div>
    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("💡 Try asking")

    st.write("• What is the course code for Data Structures?")
    st.write("• What are the subjects in 3rd semester?")
    st.write("• Create a 5-day study plan for Data Structures.")
    st.write("• Change Day 3 to 3 hours.")

    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.study_plan = ""
        st.rerun()


# ---------- Session State ----------
if "study_plan" not in st.session_state:
    st.session_state.study_plan = ""

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------- Display Previous Messages ----------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message["role"] == "assistant" and "intent" in message:
            st.caption(f"Route: {message['intent']}")

        st.markdown(message["content"])


# ---------- Chat Input ----------
question = st.chat_input("Ask your question...")


if question:

    # Display user question
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)


    # Generate answer
    with st.chat_message("assistant"):

        with st.spinner("🤖 Thinking..."):

            result = college_ai_assistant(
                question,
                st.session_state.study_plan
            )

            answer = result["answer"]
            intent = result["intent"]

            if result["study_plan"]:
                st.session_state.study_plan = result["study_plan"]

        st.caption(f"Route: {intent}")
        st.markdown(answer)


    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "intent": intent
    })
