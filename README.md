#🎓 NLP-Powered College Information Chatbot
This project is a smart chatbot built using Natural Language Processing (NLP) to answer common queries related to a college. It uses Flask for the backend and SpaCy for intent detection and keyword extraction. The chatbot intelligently matches questions using a rule-based knowledge base and a CSV dataset of FAQs.

🌐 Overview
This chatbot helps students, parents, and visitors quickly get answers to important questions like admissions, fees, scholarships, hostel, placements, and more.

Technologies Used:

Flask for building the web application

SpaCy for processing user input and extracting meaningful tokens

FuzzyWuzzy for matching similar questions from the dataset

CSV-based FAQ dataset for flexible and scalable Q&A handling

🚀 Key Features
Intent Detection: Greets, helps, or says goodbye using keyword-based NLP

Knowledge Base Lookup: Uses rule-based matching from a custom knowledge_base.py file

CSV Support: Searches a college_qa_dataset.csv file using fuzzy matching to cover many more questions

Fallback Handling: Returns a polite default message if no good match is found

User-Friendly Interface: Simple web UI built with HTML + CSS

🛠️ Setup Instructions
✅ Requirements
Python 3.7+

Flask

SpaCy (en_core_web_sm)

Pandas

FuzzyWuzzy + python-Levenshtein

📦 Installation
bash
Copy
Edit
git clone https://github.com/YOUR_USERNAME/college-chatbot.git
cd college-chatbot

pip install -r requirements.txt
python -m spacy download en_core_web_sm
🚀 Running the App
bash
Copy
Edit
python app.py
Visit: http://localhost:5000

📁 Project Structure
php
Copy
Edit
college-chatbot/
│
├── app.py                      # Main Flask server
├── knowledge_base.py           # Rule-based intent and keyword responses
├── requirements.txt
├── data/
│   └── college_qa_dataset.csv  # CSV file with extra Q&A
├── static/
│   ├── style.css               # Custom CSS
│   └── assets/                 # Optional images
├── templates/
│   └── index.html              # Chatbot frontend
💬 How the Chatbot Works
Input: User types a question.

Intent Matching: If the question matches a greeting, help, or goodbye keyword — it responds accordingly.

Knowledge Base: If keywords match a custom topic (admission, hostel, etc.), it pulls from knowledge_base.py.

CSV Matching: If not matched above, it uses fuzzy matching to find a similar question from college_qa_dataset.csv.

Fallback: If nothing fits, it gives a generic polite reply.

📚 Example Questions It Can Answer
"How can I apply for admission?"

"What is the fee for B.Tech?"

"How many students can stay in the hostel?"

"Tell me about placements"

"How to apply for scholarships?"

🙌 About the Developer
Built by Abhishek as part of a college project exploring practical applications of NLP in education.

Tech Stack: Flask, SpaCy, Pandas, FuzzyWuzzy

Role: Backend logic, NLP pipeline, and knowledge base integration

