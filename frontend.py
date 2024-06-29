

import streamlit as st
from chapter_wise import AshokaNCERTAssistant
from database2 import PostgresDatabase
from QandA import AshokaNCERTQA
from fullqa import RAGSystem
from profile_summary import Profile_summary
from summary_weakness import QAsummary
from question_generator_16 import QuestionGenerator16
from solve_x import SolveX
from testing4 import UserVisitTracker

import json
from datetime import datetime, timedelta
import random
import pandas as pd
import os


def main_overview(user_id):
    tracker = UserVisitTracker(user_id)
    streak = tracker.display_user_info()
    tracker.display_visit_calendar()
    tracker.display_time_spent()
    return streak

questions_intro = [
    "What is your name?",
    "Which exam(s) are you preparing for (e.g., NEET, JEE, higher secondary exams)?",
    "How old are you? and What is your gender?",
    "How many times have you attempted these exams before?",
    "How would you self-assess your proficiency level in physics (e.g., easy, medium, hard)?",
    "Which school or institution are you currently attending?",
    "How much time do you dedicate to studying physics each week?",
    "Do you use any additional resources (e.g., coaching classes, online courses, textbooks) for your exam preparation?",
    "What are your strengths and weaknesses in specific physics topics (e.g., mechanics, thermodynamics, electromagnetism)?",
    "Do you prefer certain types of learning methods (e.g., visual aids, hands-on experiments, reading textbooks)?",
    "What is your target score or rank for your upcoming exam?",
    "Do you have a study plan or schedule?",
    "When is your next exam scheduled?",
    "Do you participate in any group study sessions or discussions?",
    "What is your motivation or reason for choosing your specific exam (e.g., career goals, personal interest)?",
    "Do you have any particular challenges or obstacles in your preparation (e.g., time management, understanding complex concepts)?"
]


# Define chapter dictionaries

if 'pargra' not in st.session_state:
    st.session_state.pargra = 1

class_12_physics_chapters = {
    1: 'Electric Charges and Fields',
    2: 'Electrostatic Potential and Capacitance',
    3: 'Current Electricity',
    4: 'Moving Charges and Magnetism',
    5: 'Magnetism and Matter',
    6: 'Electromagnetic Induction',
    7: 'Alternating Current',
    8: 'Electromagnetic Waves',
    9: 'Ray Optics and Optical Instruments',
    10: 'Wave Optics',
    11: 'Dual Nature of Radiation and Matter',
    12: 'Atoms',
    13: 'Nuclei',
    14: 'Semiconductor Electronics: Materials, Devices and Simple Circuits',
    15: 'Communication Systems'
}


if 'streak' not in st.session_state:
    st.session_state.streak = 0

# Initialize the database connection
db = PostgresDatabase()
db.connect()

# Function to handle navigation
def navigate(page):
    st.session_state.page = page

# Function to check if user exists
def user_exists(user_id):
    return db.user_exists(user_id)

# Initialize the session state
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'questionss' not in st.session_state:
    st.session_state.questionss = questions_intro            
if 'additional_questions' not in st.session_state:
    st.session_state.additional_questions = []     
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'current_additional_question' not in st.session_state:
    st.session_state.current_additional_question = 0
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""  
    

## other initialization

if 'question_activation' not in st.session_state:
    st.session_state.question_activation = 0
        
        
if st.session_state.question_activation == 1:           
    if 'questions' not in st.session_state:
        user_id = st.session_state.user_id
        q16 = QuestionGenerator16(user_id)
        additional_questions = q16.fetch_questions()
        st.session_state.questions = additional_questions[2:18]
        st.session_state.question_activation += 1


if 'profile_updater' not in st.session_state:
    st.session_state.profile_updater = []
 
if 'additional_questionss' not in st.session_state :
    st.session_state.additional_questionss = [] 
if 'current_questions' not in st.session_state:
    st.session_state.current_questions = 0
if 'current_additional_questions' not in st.session_state:
    st.session_state.current_additional_questions = 0
    
if 'student_analysis' not in st.session_state:
    st.session_state.student_analysis = 0 
    
    
if 'star_count' not in st.session_state:
    st.session_state.star_count = 0
    

# Function to handle chapter initialization and response generation
def handle_chapter(chapter_number, assistant):
    st.title("Ashoka NCERT Assistant")
    
    if st.button('Back', key=f'chapter_{chapter_number}_back'):
        st.write('You will be redirected soon')
        navigate("study")
        st.session_state.pargra = 1
        st.rerun()
           
    pargra = st.session_state.pargra
        
    if pargra:
        with st.spinner('Gathering Data'):
            response = assistant.get_response(f'Ncert text book class 11 part 1 chapter {chapter_number}, explanation each chapter page no {pargra} detailed explanation.')
            clickable_response = assistant.make_links_clickable(response)
            with st.expander("View Response"):
                st.markdown(clickable_response)
            if st.button('Next page or next paragraph', key=f'next_page_{chapter_number}'):
                st.session_state.pargra += 1
                st.rerun()

class_11_physics_chapters = {
    1: 'Physical World',
    2: 'Units and Measurements',
    3: 'Motion in a Straight Line',
    4: 'Motion in a Plane',
    5: 'Laws of Motion',
    6: 'Work, Energy, and Power',
    7: 'System of Particles and Rotational Motion',
    8: 'Gravitation',
    9: 'Mechanical Properties of Solids',
    10: 'Mechanical Properties of Fluids',
    11: 'Thermal Properties of Matter',
    12: 'Thermodynamics',
    13: 'Kinetic Theory',
    14: 'Oscillations',
    15: 'Waves'
}


def handle_chapter_assessment(chapter_number, i):
    st.title(f'Chapter {chapter_number} Assessment')
    
    if st.button('Back', key=f'chapter_{chapter_number}_qa_back'):
        navigate('test')
        return
    
        
    if st.button(f"history_{i}", key=f'history_{i}_button'):
        st.session_state.page = f'history_{i}'
        st.rerun()
    
    if st.button("Ask a Question", key=f'ask_question_{chapter_number}') and not st.session_state.get(f'initialized_{chapter_number}', False):
        initial_question = f'Ncert text book class 11 part 1 chapter {chapter_number}, Give a question'
        response = assistant.get_response(initial_question)
        st.session_state[f'current_question_{chapter_number}'] = response
        st.session_state[f'initialized_{chapter_number}'] = True
        st.rerun()
        

        
    if 'j' not in st.session_state:
        st.session_state.j = 0
        
    j = st.session_state.j
    
    # Display the retrieved question and provide input for the user's answer
    if st.session_state.get(f'initialized_{chapter_number}', False) and st.session_state.get(f'current_question_{chapter_number}'):
        st.markdown(f"**Assistant:** {st.session_state[f'current_question_{chapter_number}']}")
        
        # Text input for user to enter their answer
        user_answer = st.text_input('Enter your answer:', key=f'user_answer_{chapter_number}')
        if st.button('Submit Answer', key=f'submit_answer_{chapter_number}'):
            answer = user_answer
            assistant_response = assistant.get_response(answer)
            j += 1
            st.session_state[f'conversation_{chapter_number}'] = st.session_state.get(f'conversation_{chapter_number}', [])
            st.session_state[f'conversation_{chapter_number}'].append({
                'question': st.session_state[f'current_question_{chapter_number}'],
                'answer': answer,
                'assistant_response': assistant_response
            })
            
            
            st.session_state[f'current_question_{chapter_number}'] = ""
            st.session_state[f'initialized_{chapter_number}'] = False
            st.rerun()  # Rerun to update the conversation display
    
    # Display conversation history
    if st.session_state.get(f'conversation_{chapter_number}', []):
        for turn in st.session_state[f'conversation_{chapter_number}']:
            st.markdown(f"**Assistant:** {turn['question']}")
            st.markdown(f"**You:** {turn['answer']}")
            st.markdown(f"**Assistant's Explanation:** {turn['assistant_response']}")
    
    # Option to ask a follow-up question or get the next question
    if st.session_state.get(f'conversation_{chapter_number}', []):
        user_followup = st.text_input('Ask a follow-up question or request the next question:', key=f'user_followup_{chapter_number}_{j}')
        if st.button('Submit Follow-up or Next Question', key=f'submit_followup_{chapter_number}'):
            followup_question = user_followup
            followup_response = assistant.get_response(followup_question)
            
            st.session_state[f'conversation_{chapter_number}'].append({
                'question': followup_question,
                'answer': "",
                'assistant_response': followup_response
            })
            
            
            st.session_state[f'user_followup_{chapter_number}'] = ""



            st.rerun()



# Welcome Page
if st.session_state.page == 'welcome':
    st.title("Welcome")
    if st.button("Login", key='welcome_login'):
        navigate('login')
        st.rerun()
    if st.button("Sign Up", key='welcome_signup'):
        navigate('signup')
        st.rerun()
        

        

# Login Page
elif st.session_state.page == 'login':
    st.title("Login")
    if st.button('back',key='login_back'):
        navigate('welcome')
    user_id = st.text_input("Username")
    if st.button("Login", key='login_login'):
        if user_exists(user_id):
            st.session_state.user_id = user_id
            navigate('dashboard') 
            st.rerun()          
        else:
            st.write("User does not exist. Please sign up.")
                    
# Sign Up Page
elif st.session_state.page == 'signup':
    st.title("Sign Up")
    if st.button('Back',key='signup_back'):
        navigate('welcome')
    user_id = st.text_input("Username")
    
    if st.button("Sign Up", key='signup_signup'):
        if user_exists(user_id):
            st.write('The user already exists. Please go back to the login page.')
        elif user_id.strip() == '' or len(user_id) < 3 or user_id.isdigit():
            st.write("Invalid user_id. Ensure it's not empty, not just spaces, length >= 3, and not entirely numeric.")
        else:
            db.save_message(user_id, "default", "assistant", "The user is new")
            st.write('Your account has been created successfully.')
            st.session_state.user_id = user_id
            navigate('evaluation')
            st.rerun()
          

# Evaluation Page
elif st.session_state.page == 'evaluation':
    st.title("Evaluation Page")
    user_id = st.session_state.user_id
    if not user_id or not user_exists(user_id):
        st.write("Access denied. Please sign up as a new user to access this page.")
        st.stop()

    questions = st.session_state.questionss
    current_question = st.session_state.current_question

    if current_question < len(questions):
        question = questions[current_question]
        if current_question == 0 :
            # print(db.get_message_history(user_id, f"profile_evaluation_{user_id}")[-1]['content'] != question)
            db.save_message(user_id, f"profile_evaluation_{user_id}", "assistant", question)
        st.write(question)
        answer = st.text_input("Your answer")
        
        if st.button("Submit Answer", key=f'evaluation_submit_{current_question}'):
            db.save_message(user_id, f"profile_evaluation_{user_id}", "user", answer)
            st.session_state.current_question += 1
            if st.session_state.current_question == len(questions):
                st.session_state.question_activation += 1

            else:
                st.rerun()  # Reload the page to show the next question
    else:
        st.write("You have completed all the questions. Thank you! Now you will be redirected to another page.")
        # if st.button('please click here',key='key_more_page'):
        navigate('more')
        st.session_state.current_question = 0
        st.rerun()
                    


# More Page
elif st.session_state.page == 'more':
    st.title("More Page")
    user_id = st.session_state.user_id
    if not user_id or not user_exists(user_id):
        st.write("Access denied. Please sign up as a new user to access this page.")
        st.stop()

    questions = st.session_state.questions
    current_question = st.session_state.current_questions

    if current_question < len(questions):
        question = questions[current_question]
        if current_question == 0 or db.get_message_history(user_id, f"profile_evaluation_{user_id}")[-1]['content'] != question:
            db.save_message(user_id, f'evaluation_question_{user_id}', "assistant", question)
        st.write(question)
        answer = st.text_input("Your answer")
        
        if st.button("Submit Answer", key=f'evaluation_submit_{current_question}'):
            db.save_message(user_id, f'evaluation_question_{user_id}', "user", answer)
            st.session_state.current_questions += 1

            if st.session_state.current_questions == len(questions):
                navigate('dashboard')
            else:
                st.rerun()  # Reload the page to show the next question
    else:
        st.write("You have completed all the questions. Thank you! Now you will be redirected to another page.")
        if st.button('please click here',key='key_more_page'):
            navigate('dashboard')
            st.rerun()


# Dashboard Page
elif st.session_state.page == 'dashboard':
    st.title("Dashboard")
    
    user_id = st.session_state.user_id
    
    
    if st.session_state.streak:
        
        st.button(f"⭐ {st.session_state.streak}")

    
    st.markdown(f" #### Your user_id is   {user_id}")
    
    if st.button('Student analysis',key = "student_analysis"):
        navigate('Overview')
    if st.button("Summary", key='dashboard_summary'):
        navigate('summary')
    if st.button('Profile Details', key='dashboard_profile_details'):
        navigate('profile_summary')
    if st.button('Start Studying', key='dashboard_start_studying'):
        navigate('study')
    if st.button('Chapter_wise_TEST', key = 'chapter_wise_test'):
        navigate('test')
    if st.button('Live Doubt Clearance', key='dashboard_live_doubt_clearance'):
        navigate('Doubt_clearance')
    if st.button('solve_x'):
        navigate('solve_x')
    if st.button('log out'):
        navigate('welcome')

elif st.session_state.page == 'Overview':
    if st.button('back', key='student_analysis_back'):
        navigate('dashboard')
        

    
    
    
    user_id = st.session_state.user_id
    streak = main_overview(user_id)
    st.session_state.streak = streak



        

#solve x
elif st.session_state.page == 'solve_x':
    if st.button('back',key ='back_button_in_solvex'):
        navigate('dashboard')
    
    from PIL import Image

    
    app = SolveX()

    st.header("Solve Your problem using through Image")
    input_text = st.text_input("Input Prompt: ", key="input")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    image = ""   
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)

    submit = st.button("Start Solving")
    
    if submit:
        response = app.get_gemini_response(input_text, image)
        st.subheader("The Response is")
        st.write(response)



elif st.session_state.page == 'study':
    st.title('Choose the chapter to start learning') 
    if st.button('Back', key='study_back'):
        navigate('dashboard')
    
    st.title("Select a Chapter")
    for i in range(1, 16):
        if st.button(f"Chapter {i}", key=f'chapter_{i}_button'):
            st.session_state.page = f'chapter_{i}'
            st.rerun()

# Chapter Pages
elif st.session_state.page.startswith('chapter_'):
    chapter_number = int(st.session_state.page.split('_')[-1])
    chapter_name = class_11_physics_chapters[chapter_number]
    profile_summary_dict = db.get_message_history(st.session_state.user_id, f'profile_summary_{st.session_state.user_id}')
    profile_summary = [messages['content'][1:-1] for messages in profile_summary_dict]
    chapter_x = f"ncert text class 11 part1_chapter{chapter_number} physical world"
    assistant = AshokaNCERTAssistant(profile_summary, chapter_x + " " + chapter_name)

    handle_chapter(chapter_number, assistant)
    st.success("Assistant initialized!")
        
        
# Chapter 1 QA
elif st.session_state.page == 'test':
    if st.button('Back', key='chapter_one_qa_back'):
        navigate('dashboard')     
    st.title("Select a Chapter for Assessment")
    for i in range(1, 16):
        if st.button(f"Chapter {i} Assessment", key=f'chapter_test_{i}_button'):
            st.session_state.page = f'test_lesson_wise_{i}'
            st.rerun()



elif st.session_state.page.startswith('test_lesson_wise_'):
    chapter_number = int(st.session_state.page.split('_')[-1])      
        
    chapter_name = class_11_physics_chapters[chapter_number]
    user_id = st.session_state.user_id
    profile_summary_dict = db.get_message_history(user_id, f'profile_summary_{user_id}') 
    profile_summary = [messages['content'][1:-1] for messages in profile_summary_dict]
    full_chapter = str(chapter_number) + ' ' + chapter_name   
    chapter_x = f'Part 1 Chapter {full_chapter}'
    assistant = AshokaNCERTQA(profile_summary, chapter_x, user_id) 
    handle_chapter_assessment(full_chapter,chapter_number)
    

elif st.session_state.page.startswith('history_'):

    chapter_number = int(st.session_state.page.split('_')[-1])
    if st.button('Back',key = f'history_{chapter_number}'):
        navigate(f'test_lesson_wise_{chapter_number}')
        
        
    chapter_name = class_11_physics_chapters[chapter_number]
    user_id = st.session_state.user_id
    full_chapter = str(chapter_number) + ' ' + chapter_name   
    chapter_x = f'Part 1 Chapter {full_chapter}'
    
    from datetime import datetime
    
    
    history = db.get_message_history(user_id,f'question_answer_{chapter_x}_{user_id}') ## Change here 
    
    for message in history:
        role = message['role']
        content = message['content']
        timestamp = message['timestamp']

        readable_time = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        formatted_message = f"{role.capitalize()} ({readable_time}):\n{content}\n"
        
        st.markdown(formatted_message)    


 

       
        
        
        
# Doubt Clearance Page
elif st.session_state.page == 'Doubt_clearance':
    st.title("Live Doubt Clearance")
    if st.button('Back', key='doubt_clearance_back'):
        navigate('dashboard')
        
        

    user_id = st.session_state.user_id
    ragsystem = RAGSystem(user_id)
    ragsystem.main()
        
               
    if st.button('History',key="live_history"):
        navigate('History_Doubt')
        
      
elif st.session_state.page == 'History_Doubt':
    st.title("History messages Doubts")
    if st.button('Back'):
        navigate('Doubt_clearance')  
    from datetime import datetime
    
    
    
    user_id = st.session_state.user_id
    
    history = db.get_message_history(user_id,f'live_doubts_{user_id}')
    
    for message in history:
        role = message['role']
        content = message['content']
        timestamp = message['timestamp']

        # Convert timestamp to readable format
        readable_time = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        formatted_message = f"{role.capitalize()} ({readable_time}):\n{content}\n"
        
        st.markdown(formatted_message)
  
    
            
            

# Profile Summary Page
elif st.session_state.page == 'profile_summary':
    st.title("Profile Summary Page")
    if st.button('Back', key='profile_summary_back'):
        navigate('dashboard')
    if st.button('update_profile_summary',key='update_profile_summary'):
        navigate('update_profile_summary')
        user_id = st.session_state.user_id 
        db.clear_message_history(user_id,f'profile_summary_{user_id}')
        db.clear_message_history(user_id,f'profile_evaluation_{user_id}')
        st.session_state.current_question = 0
        
        
    # user_id = st.session_state.user_id
    # sumi = Profile_summary(user_id)  
    # sumi.fetch_questions()  
    
    
      


        
        

    if not st.session_state.profile_updater:
        user_id = st.session_state.user_id
        sumi = Profile_summary(user_id)  
        sumi.fetch_questions() 
        profile_summary_dict = db.get_message_history(user_id, f'profile_summary_{user_id}')
        profile_summary = []
        for messages in profile_summary_dict:
            profile_summary.append(messages['content'][1:-1])  
        st.session_state.profile_updater = profile_summary
    else:
        print("hello")
        profile_summary = st.session_state.profile_updater
    
    
    
       
    
    if st.button('Show profile summary',key='show profile summary evaluation'):       
        with st.expander("View Response"):
                st.session_state['profile_summary'] = profile_summary
                st.write(profile_summary)
    elif 'profile_summary' in st.session_state:
            with st.expander("View Response"):  
                st.write(st.session_state['profile_summary'])
    else:
            st.write("No summary available.")
                        
                        
# update_profile_summary page                   
elif st.session_state.page == 'update_profile_summary':
    st.title('update your profile')
    
    user_id = st.session_state.user_id
         
    questions = st.session_state.questionss
    current_question = st.session_state.current_question
    print(current_question)

    if current_question < len(questions):
        question = questions[current_question]
        if current_question == 0:
            print(current_question)
            db.save_message(user_id, f"profile_evaluation_{user_id}", "assistant", question)
        st.write(question)
        answer = st.text_input("Your answer")
        
        if st.button("Submit Answer", key=f'evaluation_submit_{current_question}'):
            db.save_message(user_id, f"profile_evaluation_{user_id}", "user", answer)
            st.session_state.current_question += 1
            if st.session_state.current_question == len(questions):
                pass
            else:
                st.rerun()  # Reload the page to show the next question
    else:
        navigate('dashboard')
        st.session_state.current_question = 0
        st.write("You have completed all the questions. Thank you! Now you will be redirected to dashboard.")
        st.session_state.profile_updater = []
        st.session_state.profile_summary = []
        st.rerun()
        
        
        

# Summary Page
elif st.session_state.page == 'summary':
    st.title("Summary Page")
    if st.button('Back', key='summary_back'):
        navigate('dashboard')    
            
    user_id = st.session_state.user_id     
    if st.button("Your Understanding", key='summary_your_understanding'):
        navigate('Your_understanding')
    
    for i in range(1, 16):
        if st.button(f"Chapter_{i}_summary", key=f'chapter_summary_{i}_button'):
            st.session_state.page = f'summary_chapter_{i}'
            st.rerun()
   
        
elif st.session_state.page.startswith('summary_chapter_'):  
    chapter_number = int(st.session_state.page.split('_')[-1])
    chapter_name = class_11_physics_chapters[chapter_number]
    if st.button('back',key=f'{chapter_name}'):
        navigate('summary')
    user_id = st.session_state.user_id
    full_chapter = str(chapter_number) + ' ' + chapter_name   
    chapter_x = f'Part 1 Chapter {full_chapter}'
    conversational_id = f'question_answer_{chapter_x}_{user_id}'
    qa_summary = QAsummary(user_id,conversational_id)
    summary = qa_summary.fetch_questions()
    if st.button('Show summary',key=f'show {chapter_number} evaluation'):       
        with st.expander("View Response"):
                st.session_state[f'{chapter_number}'] = summary
                st.write(summary)
    else:
        pass
    
            

elif st.session_state.page == 'Your_understanding':
    st.title('Evaluation_summary')
    if st.button('Back',key='Your_understanding_back'):
        navigate('summary')
       
    user_id = st.session_state.user_id
              
    sumi = QAsummary(user_id,f'evaluation_question_{user_id}')
      
    summary = sumi.fetch_questions()  
    
    
    if st.button('Show summary',key='show summary evaluation'):       
        with st.expander("View Response"):
                st.session_state['summary'] = summary
                st.write(summary)
    elif 'summary' in st.session_state:
            with st.expander("View Response"):  
                st.write(st.session_state['summary'])


