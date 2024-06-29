from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

class SolveX:
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro-vision')

    def get_gemini_response(self, input, image):
        prompt = f"""You are a genius mathematician and physics
        tutor which can explain any complex math problem, 
        solve the following problem or answer the question 
        based on the provided image and input:\n\nProblem: {input}
        if the image is not related to problem just say i don't know
        """
        if image:
            response = self.model.generate_content([prompt, image])
        else:
            response = self.model.generate_content(prompt)
        return response.text