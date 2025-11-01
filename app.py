"""
ScholarMate - AI-Powered Academic Assistant
Main Streamlit Application Entry Point
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.coordinator import CoordinatorAgent
from mcp.database_tool import DatabaseTool
import json
import os

# Page configuration
st.set_page_config(
    page_title="ScholarMate - AI Academic Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'coordinator' not in st.session_state:
        st.session_state.coordinator = CoordinatorAgent()
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseTool()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"


def sidebar_navigation():
    """Render sidebar navigation."""
    st.sidebar.markdown("## 📚 ScholarMate")
    st.sidebar.markdown("---")
    
    pages = {
        "🏠 Dashboard": "Dashboard",
        "📅 Calendar": "Calendar",
        "📝 Lecture Summarizer": "Summarizer",
        "📊 Study Planner": "Planner",
        "🔍 Evaluation Logs": "Evaluation"
    }
    
    for label, page_name in pages.items():
        if st.sidebar.button(label, use_container_width=True):
            st.session_state.current_page = page_name
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Settings")
    st.sidebar.markdown("Model: Fine-tuned Mistral-7B")
    st.sidebar.markdown(f"Database: Active")


def dashboard_page():
    """Main dashboard view."""
    st.markdown('<div class="main-header">📚 ScholarMate Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("📝 Total Flashcards", st.session_state.db.count_flashcards())
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("📅 Upcoming Events", st.session_state.db.count_upcoming_events())
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("📊 Study Sessions", st.session_state.db.count_study_sessions())
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        quick_input = st.text_input("Ask me anything:", placeholder="e.g., Schedule a study session tomorrow at 3pm")
        if st.button("Submit", type="primary"):
            if quick_input:
                with st.spinner("Processing..."):
                    response = st.session_state.coordinator.handle_request(quick_input)
                    st.markdown(f'<div class="success-box">{response["message"]}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📋 Recent Activity")
        recent_logs = st.session_state.db.get_recent_logs(5)
        for log in recent_logs:
            st.markdown(f"- {log['timestamp']}: {log['action']}")


def calendar_page():
    """Calendar management interface."""
    st.markdown('<div class="main-header">📅 Calendar</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 View Events", "➕ Add Event"])
    
    with tab1:
        st.subheader("Upcoming Events")
        events = st.session_state.db.get_upcoming_events()
        
        if events:
            for event in events:
                with st.expander(f"{event['title']} - {event['date']}"):
                    st.write(f"**Time:** {event.get('time', 'All day')}")
                    st.write(f"**Description:** {event.get('description', 'No description')}")
                    if st.button(f"Delete Event", key=f"del_{event['id']}"):
                        st.session_state.db.delete_event(event['id'])
                        st.rerun()
        else:
            st.info("No upcoming events. Add one below!")
    
    with tab2:
        st.subheader("Create New Event")
        
        event_input = st.text_area(
            "Describe your event in natural language:",
            placeholder="Schedule a machine learning lecture on Friday at 2pm for 2 hours"
        )
        
        if st.button("Create Event", type="primary"):
            if event_input:
                with st.spinner("Creating event..."):
                    response = st.session_state.coordinator.handle_request(event_input, intent_override="calendar")
                    if response.get("success"):
                        st.markdown(f'<div class="success-box">✅ {response["message"]}</div>', unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.markdown(f'<div class="error-box">❌ {response.get("message", "Error creating event")}</div>', unsafe_allow_html=True)


def summarizer_page():
    """Lecture summarizer and flashcard generator."""
    st.markdown('<div class="main-header">📝 Lecture Summarizer</div>', unsafe_allow_html=True)
    
    st.markdown("Upload lecture notes or paste text to generate summaries and flashcards.")
    
    tab1, tab2 = st.tabs(["📄 Text Input", "📎 File Upload"])
    
    with tab1:
        lecture_text = st.text_area(
            "Paste your lecture notes here:",
            height=300,
            placeholder="Enter lecture content..."
        )
        
        if st.button("Generate Summary & Flashcards", type="primary"):
            if lecture_text:
                with st.spinner("Analyzing lecture content..."):
                    response = st.session_state.coordinator.handle_request(
                        lecture_text,
                        intent_override="summarize"
                    )
                    
                    if response.get("success"):
                        st.markdown("### 📋 Summary")
                        st.markdown(f'<div class="card">{response["summary"]}</div>', unsafe_allow_html=True)
                        
                        st.markdown("### 🎴 Flashcards")
                        flashcards = response.get("flashcards", [])
                        for i, card in enumerate(flashcards, 1):
                            with st.expander(f"Flashcard {i}: {card['question']}"):
                                st.markdown(f"**Answer:** {card['answer']}")
                    else:
                        st.error(response.get("message", "Error generating summary"))
    
    with tab2:
        uploaded_file = st.file_uploader("Upload a file", type=['txt', 'pdf', 'docx'])
        
        if uploaded_file:
            st.info(f"File uploaded: {uploaded_file.name}")
            
            if st.button("Process File", type="primary"):
                with st.spinner("Processing file..."):
                    # Save file temporarily
                    file_path = f"data/uploads/{uploaded_file.name}"
                    os.makedirs("data/uploads", exist_ok=True)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    response = st.session_state.coordinator.handle_request(
                        f"Summarize file: {file_path}",
                        intent_override="summarize"
                    )
                    
                    if response.get("success"):
                        st.success("File processed successfully!")
                        st.markdown("### 📋 Summary")
                        st.write(response["summary"])


def planner_page():
    """Study planner interface."""
    st.markdown('<div class="main-header">📊 Study Planner</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Generate Study Plan")
        
        plan_input = st.text_area(
            "Describe your study goals:",
            placeholder="I need to study calculus and physics for exams next week. I have 3 hours daily."
        )
        
        if st.button("Generate Plan", type="primary"):
            if plan_input:
                with st.spinner("Creating personalized study plan..."):
                    response = st.session_state.coordinator.handle_request(
                        plan_input,
                        intent_override="plan"
                    )
                    
                    if response.get("success"):
                        st.markdown("### 📅 Your Study Plan")
                        plan = response.get("plan", {})
                        
                        for day, tasks in plan.items():
                            with st.expander(f"📆 {day}"):
                                for task in tasks:
                                    st.markdown(f"- **{task['time']}**: {task['activity']} ({task['duration']})")
    
    with col2:
        st.subheader("Current Plan")
        current_plan = st.session_state.db.get_current_study_plan()
        if current_plan:
            st.json(current_plan)
        else:
            st.info("No active study plan. Generate one!")


def evaluation_page():
    """Evaluation logs and metrics."""
    st.markdown('<div class="main-header">🔍 Evaluation Logs</div>', unsafe_allow_html=True)
    
    st.subheader("Model Performance Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Quality Metrics")
        metrics = st.session_state.db.get_evaluation_metrics()
        if metrics:
            st.metric("Average ROUGE Score", f"{metrics.get('rouge', 0):.3f}")
            st.metric("Average BLEU Score", f"{metrics.get('bleu', 0):.3f}")
            st.metric("User Satisfaction", f"{metrics.get('satisfaction', 0):.1f}/5.0")
    
    with col2:
        st.markdown("### 📝 Recent Evaluations")
        logs = st.session_state.db.get_evaluation_logs(10)
        for log in logs:
            st.markdown(f"- **{log['timestamp']}**: {log['metric']} = {log['score']}")
    
    st.markdown("---")
    st.subheader("Detailed Logs")
    
    if st.button("Refresh Logs"):
        st.rerun()
    
    all_logs = st.session_state.db.get_all_logs()
    st.dataframe(all_logs, use_container_width=True)


def main():
    """Main application entry point."""
    initialize_session_state()
    sidebar_navigation()
    
    # Route to appropriate page
    page = st.session_state.current_page
    
    if page == "Dashboard":
        dashboard_page()
    elif page == "Calendar":
        calendar_page()
    elif page == "Summarizer":
        summarizer_page()
    elif page == "Planner":
        planner_page()
    elif page == "Evaluation":
        evaluation_page()


if __name__ == "__main__":
    main()