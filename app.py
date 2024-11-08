from flask import Flask, render_template, jsonify, request
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import os
import json
import random

app = Flask(__name__)

# Configure Google Generative AI (Gemini) SDK using environment variable
GOOGLE_API_KEY = "AIzaSyC9KuySK4yAV-W6gPKGwloTkTbTl3F6k40"   # Set this environment variable
if GOOGLE_API_KEY is None:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable")

genai.configure(api_key=GOOGLE_API_KEY)

# Function to fetch video transcript from YouTube
def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item['text'] for item in transcript])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

# Function to generate quiz prompt based on provided text
def get_prompt_quiz(text):
    return f'''
    Please create a multiple-choice quiz question based on the following text:
    "{text}"
    Each question should have 4 answer options (A, B, C, D) and one correct answer.
    Also, provide a brief explanation for the correct answer.
    Return the response as a valid JSON string in this format:

    {{
        "question": "What does the backend usually send to the frontend for communication?",
        "options": {{
            "A": "HTML",
            "B": "JSON",
            "C": "XML",
            "D": "All of the above"
        }},
        "correct_answer": "D",
        "explanation": "The backend can send various formats, but in many cases, JSON is preferred due to its lightweight structure."
    }}
    '''

def quiz_content(text):
    prompt = get_prompt_quiz(text)
    model = genai.GenerativeModel('gemini-pro')
    
    try:
        response = model.generate_content(prompt)
        quiz_json = json.loads(response.text)
        return quiz_json
    except (json.JSONDecodeError, IndexError) as e:
        return {
            "question": "Unable to generate quiz",
            "options": {
                "A": "N/A",
                "B": "N/A",
                "C": "N/A",
                "D": "N/A"
            },
            "correct_answer": "A",
            "explanation": "No explanation available."
        }

# Route to the homepage with video ID input
@app.route('/')
def index():
    return render_template('index.html')

# Route to generate two distinct quizzes from YouTube video transcript
@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    video_id = request.form['video_id']
    text = get_video_transcript(video_id)
    
    if text:
        # Split the transcript into smaller parts (chunks) for quiz generation
        transcript_split = text.split(". ")
        
        if len(transcript_split) > 2:
            # Randomly select two different parts of the transcript for generating distinct quizzes
            segment1 = random.choice(transcript_split)
            segment2 = random.choice([seg for seg in transcript_split if seg != segment1])
            
            quiz1 = quiz_content(segment1)
            quiz2 = quiz_content(segment2)
        else:
            quiz1 = quiz_content(text)
            quiz2 = quiz_content(text)
        
        return render_template('atheno_quiz.html', quiz1=quiz1, quiz2=quiz2)
    else:
        return "No transcript available for this video", 400

# Route to check the user's answer
@app.route('/check_answer', methods=['POST'])
def check_answer():
    user_answer = request.form['answer']
    correct_answer = request.form['correct_answer']
    explanation = request.form['explanation']
    
    if user_answer == correct_answer:
        return jsonify({"result": "correct"})
    else:
        return jsonify({
            "result": "incorrect",
            "explanation": explanation
        })

@app.route('/athenocards', methods=['GET', 'POST'])
def atheno_cards():
    return render_template('atheno_cards.html')

@app.route('/athenolite', methods=['GET', 'POST'])
def atheno_lite():
    return render_template('atheno_lite.html')

@app.route('/athenotask', methods=['GET', 'POST'])
def atheno_task():
    return render_template('atheno_task.html')


if __name__ == '__main__':
    app.run(debug=True)






