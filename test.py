


from PIL import Image
import streamlit as st
from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

class SolveX:
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        # self.model = genai.GenerativeModel('gemini-pro-vision')
        self.model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")


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