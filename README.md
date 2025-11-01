Name: Abhay Chandra
University: IIT Bombay
Department: BS Engineering Sciences with specialization in AI ML
# ScholarMate - AI-Powered Academic Assistant

ScholarMate is a comprehensive, MCP-integrated AI system that automates academic life through intelligent scheduling, lecture summarization, flashcard generation, and adaptive study planning.

## 🚀 Features

- **Natural Language Scheduling**: Create calendar events using plain English
- **Lecture Summarizer**: Generate concise summaries from lecture notes
- **Flashcard Generator**: Automatically create study flashcards
- **Adaptive Study Planner**: Generate personalized study schedules
- **Google Calendar Integration**: Sync events with Google Calendar
- **Performance Evaluation**: Track and evaluate AI-generated content quality
- **Fine-tuned Models**: Uses LoRA-tuned models for educational content

## 📋 Requirements

### Core Dependencies
```bash
pip install streamlit
pip install anthropic  # or openai
pip install sqlite3
```

### Optional Dependencies

**For Fine-tuned Model Support:**
```bash
pip install torch
pip install transformers
pip install peft
```

**For Google Calendar Integration:**
```bash
pip install google-api-python-client
pip install google-auth-httplib2
pip install google-auth-oauthlib
```

**For PDF Processing:**
```bash
pip install PyPDF2
# or
pip install pdfplumber
```

**For Advanced Document Processing:**
```bash
pip install python-docx
```

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd scholarmate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up Google Calendar (Optional):**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials
   - Download `credentials.json` and place in project root

4. **Set up environment variables:**
```bash
export GOOGLE_CREDENTIALS_PATH="credentials.json"
export GOOGLE_TOKEN_PATH="token.json"
```

## 🚀 Quick Start

### Run the Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Basic Usage Examples

**1. Schedule a Study Session:**
```
"Schedule a calculus study session tomorrow at 3pm for 2 hours"
```

**2. Summarize Lecture Notes:**
```
Paste your lecture notes in the Lecture Summarizer tab and click "Generate Summary & Flashcards"
```

**3. Create a Study Plan:**
```
"I need to study physics and chemistry for exams next week. I have 3 hours daily."
```

## 📂 Project Structure
```
scholarmate/
│
├── app.py                        # Main Streamlit application
├── agents/
│   ├── coordinator.py            # Central request router
│   ├── calendar_agent.py         # Calendar operations
│   ├── summarizer_agent.py       # Summarization & flashcards
│   ├── planner_agent.py          # Study planning
│   └── evaluator_agent.py        # Quality evaluation
│
├── models/
│   ├── lora_model/               # Fine-tuned model directory
│   └── inference.py              # Model inference engine
│
├── mcp/
│   ├── google_calendar_client.py # Google Calendar MCP client
│   ├── pdf_parser_tool.py        # PDF text extraction
│   └── database_tool.py           # SQLite database manager
│
├── data/
│   ├── scholarmate.db            # SQLite database (auto-created)
│   ├── uploads/                  # Uploaded files
│   └── flashcards/               # Generated flashcards
│
├── utils/
│   ├── prompts.py                # Prompt templates
│   ├── evaluation.py             # Evaluation metrics
│   └── scheduler_utils.py        # Scheduling utilities
│
└── README.md                     # This file
```

## 🧠 Architecture Overview

### Agent System

ScholarMate uses a multi-agent architecture:

1. **Coordinator Agent**: Routes requests to appropriate specialized agents
2. **Calendar Agent**: Handles scheduling and calendar integration
3. **Summarizer Agent**: Generates summaries and flashcards
4. **Planner Agent**: Creates adaptive study schedules
5. **Evaluator Agent**: Assesses content quality

### Data Flow
```
User Input → Coordinator → Specialized Agent → Model/API → Response → UI
                ↓
          Database Storage
                ↓
          Evaluation & Logging
```

## 🎯 Usage Guide

### Dashboard
- View statistics (flashcards, events, sessions)
- Quick actions for common tasks
- Recent activity log

### Calendar
- View upcoming events
- Create new events with natural language
- Sync with Google Calendar

### Lecture Summarizer
- Paste lecture notes or upload files
- Generate concise summaries
- Create study flashcards automatically
- Supports TXT, PDF, DOCX formats

### Study Planner
- Describe study goals in natural language
- Get personalized day-by-day plans
- Automatic calendar synchronization
- Adaptive scheduling based on deadlines

### Evaluation Logs
- View performance metrics
- Track model quality (ROUGE, BLEU scores)
- Monitor system usage
- Compare base vs fine-tuned models

## 🔧 Configuration

### Database Configuration

The database is automatically created at `data/scholarmate.db`. To use a different location:
```python
from mcp.database_tool import DatabaseTool

db = DatabaseTool(db_path="custom/path/database.db")
```

### Model Configuration

To use a custom fine-tuned model:
```python
from models.inference import ModelInference

model = ModelInference(model_path="path/to/your/model")
```

## 📊 Evaluation Metrics

ScholarMate tracks several quality metrics:

- **ROUGE Scores**: Measure summary quality
- **BLEU Scores**: Evaluate generation accuracy
- **Clarity**: Question and answer clarity
- **Completeness**: Content completeness
- **Diversity**: Variety of question types

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional calendar providers (Outlook, Apple Calendar)
- More sophisticated NLP for intent detection
- Advanced spaced repetition algorithms
- Mobile app version
- Collaborative study features

## 📝 License

This project is licensed under the MIT License.

## 🐛 Troubleshooting

### Common Issues

**1. Google Calendar not connecting:**
- Ensure `credentials.json` is in project root
- Check that Google Calendar API is enabled
- Delete `token.json` and re-authenticate

**2. Model not loading:**
- Install required packages: `pip install torch transformers peft`
- Check model path exists
- System will use fallback methods if model unavailable

**3. Database errors:**
- Ensure `data/` directory exists
- Check write permissions
- Delete database file to reset

**4. PDF extraction failing:**
- Install PDF library: `pip install PyPDF2` or `pip install pdfplumber`
- Check PDF is not encrypted or password-protected

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check documentation
- Review example usage in code comments

## 🎓 Academic Use

ScholarMate is designed for educational purposes. Features:
- Lecture note processing
- Automated flashcard creation
- Study schedule optimization
- Calendar management for academic deadlines

## ⚡ Performance Tips

- Keep lecture notes under 5000 words for best results
- Use specific topics in study planning
- Review generated flashcards for accuracy
- Regularly clear old data to maintain performance

## 🔮 Future Enhancements

- Voice input for hands-free operation
- Integration with learning management systems (Canvas, Moodle)
- Collaborative study group features
- Advanced analytics and progress tracking
- Mobile notifications for study reminders
- Integration with note-taking apps (Notion, Evernote)

---
