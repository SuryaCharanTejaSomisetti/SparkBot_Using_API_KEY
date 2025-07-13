# SparkBot_Using_API_KEY
# 🤖 SparkBot

SparkBot is an intelligent chatbot built using **Flask**, **HTML/CSS**, **Bootstrap**, and integrated with **Gemini AI (Google Generative AI)**. It supports login/signup authentication, dynamic chat history, responsive UI, and smooth user interaction. Ideal for educational, personal assistant, or customer support scenarios.


## 🚀 Features

- 🧠 Gemini AI-powered chatbot responses  
- 🔐 User Authentication (Login & Signup)  
- 💬 Dynamic Chat History with Title Auto-Renaming  
- 📱 Responsive UI (Mobile-Friendly with Sidebar Toggle)  
- 🎨 Stylish Interface using Bootstrap & Custom CSS  
- 🗑 Delete chat history or individual chat sessions  
- 📂 Session-based user chat storage using JSON  
- 📸 Background image support on login/signup pages


## 📁 Folder Structure

SparkBot/
│
├── static/
│ └── style.css # Custom styles for chatbot UI
│
├── templates/
│ ├── index.html # Main chat UI
│ ├── login.html # Login page
│ └── signup.html # Signup page
│
├── users.json # Registered user data (email, hashed password)
├── chat_history_<username>.json # Individual user chat histories
├── app.py # Main Flask backend with routing & AI integration
├── .env # Contains GEMINI_API_KEY and SECRET_KEY
└── README.md # Project overview and documentation


## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, Bootstrap  
- **Backend:** Python, Flask  
- **AI Model:** Gemini 1.5 Flash by Google  
- **Authentication:** Werkzeug password hashing  
- **Data Storage:** JSON files (for users and chat history)

## 🧪 Setup Instructions

### Clone the Repository

```bash
git clone https://github.com/your-username/SparkBot.git
cd SparkBot
