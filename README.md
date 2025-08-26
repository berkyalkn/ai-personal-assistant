# Personal AI Assistant


A conversational AI assistant that connects to your Google services to help you manage your calendar, read and summarize your emails, answer questions via web search, and hold natural conversations with persistent memory.

---

## Features

- **Conversational AI Core:** Powered by LangGraph and Groq's Llama 3 for stateful, low-latency conversations.

- **Persistent Conversation Memory:** Utilizes LangGraph's checkpointer system with SQLite to remember conversations, allowing you to stop and resume your session at any time.

- **Advanced Google Calendar Integration:**
  + **Read Events:** Understands natural language queries for dates and ranges like "tomorrow" or "next Friday".

  + **Create Events:** Schedules new appointments, automatically checking for conflicts before adding them.

  + **Update Events:** Modifies existing events with simple commands like "Move my meeting to 3 PM".

  + **Delete Events:** Cancels appointments with a confirmation step to prevent accidents.

- **Gmail Integration:**

  + **Read & Summarize:** Reads emails from your inbox and provides concise summaries.

  + **Intelligent Filtering:** Understands requests to filter emails by sender, status (unread/read), and time range (e.g., "last 2 days").

- **General Knowledge Q&A:** Uses Tavily Search to answer questions about real-time events, facts, and general knowledge.

- **Intelligent Tool Use:** Differentiates between chat and tasks, using tools only when necessary and asking clarifying questions for missing details.

- **Interactive Notebook Environment:** All development and interaction happens within a single, easy-to-use `assistant.ipynb` file.

---

## Technologies Used

- **Core Framework:** LangChain & LangGraph for building the stateful agent.
- **LLM:** Llama 3, accessed via the Groq API for high-speed, low-latency responses.
- **External Services:**
  - Google Calendar API
  - Google Gmail API
  - Tavily Search API
- **Key Python Libraries:**
  - `google-api-python-client` & `google-auth-oauthlib` for Google API authentication.
  - `Pydantic` for robust data validation and modeling.
  - `python-dotenv` for secure management of API keys.
- **Database:** SQLite, used by LangGraph's checkpointer for persistent conversation memory.


---


##  Setup & Installation

Follow these steps to get your local environment set up and ready to run the assistant.

**1. Clone the Repository:**

```bash
git clone https://github.com/berkyalkn/ai-personal-assistant.git
cd ai-personal-assistant
```

**2. Create a Virtual Environment and Install Dependencies:**

```bash
# Create a virtual environment
python -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate
# Or (Windows)
.\venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

**3. Create and Configure the `.env` File:**

- In the root of the project, create a new file named .env.

-  Copy the contents of the .env.example file below into your new .env file and fill in your own credentials.


**.env.example:**

```
# Groq API Key for the LLM
GROQ_API_KEY="gsk_YourGroqApiKey"

# Tavily API Key for web search
TAVILY_API_KEY="tvly-YourTavilyApiKey"

```


**4. Configure Google Calendar Access:**

- Go to the [Google Cloud Console](https://console.cloud.google.com/)

- Create a new project.

- Go to "APIs & Services" > "Library" and enable the "Google Calendar API".

- Go to "OAuth consent screen", select "External", and fill in the required app details. Add your own Google account as a "Test user".

- Go to "Credentials", click "+ CREATE CREDENTIALS", and select "OAuth client ID".

- Choose "Desktop app" as the application type.

- After creation, click the "DOWNLOAD JSON" button.

- Rename the downloaded file to `credentials.json` and place it in the root of your project directory.

**Note:** The first time you run a calendar command, you will be prompted to authorize the application in your browser. This will generate a `token.json` file. This is a one-time process.

---

## How to Run

1- Open the `assistant.ipynb` file in Jupyter Notebook, JupyterLab, or Visual Studio Code.

2- Run the cells in order from top to bottom.

3- The final cell will start an interactive chat loop. You can start talking to your assistant directly in the notebook's output.

4- To continue a previous conversation, ensure the thread_id in the code is the same. To start a new one, change the thread_id.

--- 

## Example Usage

```
Your assistant is ready. You can now start chatting.
   Type 'quit' or 'exit' to end the conversation.
-------------------------
You: What's on my schedule for tomorrow?
Assistant: You have a 'Dentist Appointment' scheduled for tomorrow at 11:00 AM.

You: Can you add a 'Family Lunch' at 1 PM tomorrow at 'Yedi Mehmet' for 90 minutes?
Assistant: Done. I've added 'Family Lunch' to your calendar for tomorrow at 1:00 PM.

You: Actually, can you move the Family Lunch to 1:30 PM instead?
Assistant: No problem. The 'Family Lunch' has been rescheduled to start at 1:30 PM.

You: Great. By the way, are there any unread emails from 'Google'?
Assistant: Let me check. Yes, you have one unread email from 'Google' with the subject 'Security alert'. The summary is that a new device has signed into your account.

You: When did I receive that?
Assistant: You received that email today, August 27, 2025.

You: Okay, thanks. Please cancel the Dentist Appointment.
Assistant: I found the 'Dentist Appointment' for tomorrow. Are you sure you want to cancel it?

You: Yes, please.
Assistant: The 'Dentist Appointment' has been successfully removed from your calendar.
