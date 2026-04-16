# Bella Italia — AI Restaurant Agent

An AI powered restaurant agent built with FastAPI, LangGraph and Groq AI.
The agent uses tools to handle customer requests including menu inquiries,
table bookings, availability checks and dietary requirement questions.

## Features

- AI agent with 5 tools — menu, booking, availability, dietary, info
- Multi-session memory — each customer has separate conversation history
- Real restaurant data injection — no hallucination
- Reasoning rules — agent gathers info before booking
- Guardrails — only answers restaurant related questions
- Anti-hallucination rules — only uses provided data
- Built with LangGraph — modern LangChain 1.x agent framework

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend web framework |
| LangGraph | AI agent framework |
| LangChain | AI tooling and prompts |
| Groq API | AI language model provider |
| LLaMA 3.3 70B | AI model |
| Pydantic | Data validation |
| python-dotenv | Environment variable management |

## Project Structure
bella-italia-agent/
│
├── env/
├── main.py
├── .env
└── requirements.txt

## Setup

1. Clone the repository
git clone https://github.com/yourusername/bella-italia-agent

2. Create and activate virtual environment
python -m venv env
env\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Create `.env` file and add your Groq API key
API_KEY=your_groq_api_key_here

5. Run the server
uvicorn main:app --reload

## API Endpoint

### POST /chat

**Request:**
```json
{
    "session_id": "user_1",
    "message": "Do you have vegetarian pizza?"
}
```

**Response:**
```json
{
    "output": "Yes we have Vegetarian pizza available!"
}
```

## Available Tools

| Tool | Description |
|---|---|
| `check_menu` | Returns full menu or specific category |
| `check_dietary_options` | Checks dietary requirement availability |
| `get_restaurant_info` | Returns name, hours, location, phone |
| `check_availability` | Checks table availability for date and time |
| `book_table` | Books a table with reference number |

## Booking Flow
Customer sends message
↓
Agent understands request
↓
Agent gathers missing info if needed
↓
Agent checks availability
↓
Agent books the table
↓
Agent confirms with reference number

## Validation Rules

- Session ID cannot be empty
- Message cannot be empty
- Maximum 8 people per table

## Restaurant Information
Name:          Bella Italia
Location:      Astoria, New York
Opening Hours: 12 PM to 11 PM
Phone:         123-456-7890

## Environment Variables
API_KEY=your_groq_api_key_here

## Notes

- Never commit your .env file to GitHub
- Session memory resets when server restarts
- Agent only handles Bella Italia related questions