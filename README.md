# Personal AI Assistant


A conversational AI assistant that connects to your Google Calendar to help you manage your schedule, answers your questions via web search, and holds natural conversations.

---

## Features

- **Conversational AI Core:** Powered by LangGraph and Groq's Llama 3 for stateful, low-latency conversations.
- **Advanced Google Calendar Integration:**

  + **Read Events with NLU:** Understands natural language queries for dates and ranges like "tomorrow", "next Friday", or "in the next 3 days".

  + **Create Events:** Schedule new appointments and meetings directly through conversation (e.g., "Add a meeting tomorrow at 2 PM for an hour").
- **General Knowledge Q&A:** Uses Tavily Search to answer questions about real-time events, facts, and general knowledge.
- **Hybrid Functionality:** Can differentiate between a general chat and a specific task, using tools only when necessary.
- **Interactive Notebook Environment:** All development and interaction happens within a single, easy-to-use `assistant.ipynb` file.

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

`Note:` The first time you run a calendar command, you will be prompted to authorize the application in your browser. This will generate a token.json file. This is a one-time process.

---

## How to Run

1- Open the `assistant.ipynb` file in Jupyter Notebook, JupyterLab, or Visual Studio Code.

2- Run the cells in order from top to bottom.

3- The final cell will start an interactive chat loop. You can start talking to your assistant directly in the notebook's output.

--- 

## Example Usage

```
Your assistant is ready. You can now start chatting.
   Type 'quit' or 'exit' to end the conversation.
-------------------------
You: What's on my schedule for tomorrow?
Assistant: You have a 'Doctor' appointment scheduled for tomorrow at 3:30 AM.

You: Can you show me my events for the next 3 days?
Assistant: Here is your schedule for the next 3 days:
- August 18, 2025: Doctor at 3:30 AM
- August 19, 2025: Dinner at 8:00 PM
- August 20, 2025: Dentist at 9:30 AM

You: Add a 'Breakfast' to my calendar for next Friday at 11 AM, and make it 90 minutes long.
Assistant: Your 'Breakfast' has been successfully scheduled for Friday, August 22, 2025, from 11:00 AM to 12:30 PM.

You: What is the capital of Japan?
Assistant: The capital of Japan is Tokyo.
```