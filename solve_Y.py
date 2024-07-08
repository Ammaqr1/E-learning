from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import time

class SolveY:
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
        
        self.save_path = 'fysics_videos'

    def get_gemini_response(self, input_text, video_file):
        prompt = f"""You are an expert physics tutor with a talent for explaining complex topics in a clear and understandable manner. 
        Your task is to help the user with their specific needs related to the provided physics video. 

        User's request: {input_text}

        Instructions:
        1. Review the user's input carefully to identify the specific timestamp or part of the video where they need help if none from user;s request explain the video.
        2. Describe the content of the video and explain the physics concept or problem being discussed at the specified timestamp.
        3. Provide a step-by-step explanation or clarification of the concept or problem to help the user understand it better.
        4. If the video is not related to physics or math, inform the user appropriately by stating, "The video is not related to physics or mathematics."

        Remember, your goal is to make the explanation as clear and detailed as possible to ensure the user fully understands the concept or solution."""
        
        while video_file.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(10)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError(video_file.state.name)
                    
        if video_file:
            response = self.model.generate_content([prompt, video_file],
                                  request_options={"timeout": 600})
        else:
            print('No file is being detected, check the type of the file')
        
        if os.path.exists(self.save_path):
            os.remove(self.save_path)
        
        return response.text


