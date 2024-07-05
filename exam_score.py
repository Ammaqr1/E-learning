import os
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain.load import dumps
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI






class Exam_Score:
    def __init__(self,question):
        load_dotenv()  # Ensure environment variables are loaded
        os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')

        self.question = question
        
        
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        

        
        self.setup_generative_ai()

    def setup_generative_ai(self):
        self.llm = ChatGroq(temperature=0.9, groq_api_key=self.api_key, model_name="llama3-8b-8192")
        self.ll = ChatGroq(temperature=0.2, groq_api_key=self.api_key, model_name="gemma-7b-it")
        self.llmm = ChatGroq(temperature=0.2, groq_api_key=self.api_key, model_name="llama3-70b-8192") #much better
        self.llmm1 = ChatGroq(temperature=0.2, groq_api_key=self.api_key, model_name="mixtral-8x7b-32768") #much less better
        self.llmm2 = ChatGroq(temperature=0.2, groq_api_key=self.api_key, model_name="gemma2-9b-it") #much less less better
        
        self.model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

    def get_score(self): 
        prompt_template = """
            You are an AI assistant tasked with evaluating a set ncert physics exam of multiple-choice questions and their given answers, then providing a score based on their correctness. Each question and answer pair is worth one point.

            Instructions:
            1. Review the provided questions and given answers.
            2. Compare the given answer with the correct answer.
            3. Provide feedback for each question, indicating whether the given answer is correct or incorrect, and supply the correct answer if necessary.
            4. Assign one point for each correct answer.
            5. Sum the points to provide a total score.
            6. The output should include each question with its given answer, the correct answer, an indication of whether the given answer was correct or incorrect, and the total score at the end.

            Example Input:
            Which of the following is a fundamental unit in the SI system? - Second
            A body of mass 10 kg is moving with a velocity of 5 m/s. What is its kinetic energy? - 500 J
            A particle is moving in a circular path of radius 10 m with a constant speed of 20 m/s. What is the centripetal force acting on the particle? - 160 N

            Example Output:
            1. Question: Which of the following is a fundamental unit in the SI system?
            Given answer: Second
            Correct answer: Second (Correct)

            2. Question: A body of mass 10 kg is moving with a velocity of 5 m/s. What is its kinetic energy?
            Given answer: 500 J
            Correct answer: The kinetic energy (KE) is given by the formula:
            KE = 1/2 mv²
            Substituting m = 10 kg and v = 5 m/s:
            KE = 1/2 × 10 × 5² = 1/2 × 10 × 25 = 125 J
            The correct answer is 125 J. (Incorrect)

            3. Question: A particle is moving in a circular path of radius 10 m with a constant speed of 20 m/s. What is the centripetal force acting on the particle?
            Given answer: 160 N
            Correct answer: The centripetal force (Fc) is given by the formula:
            Fc = mv²/r
            However, the mass of the particle is not provided in the question. Without the mass (m), we cannot calculate the exact value of the centripetal force. Therefore, the provided answer cannot be verified as correct or incorrect. (Insufficient information)

            Total Score: 1/3
            
            Also need entire output at once and give the total score
            
            
            question and answer : {question}
            
            """
            
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
  
        final_rag_chain = (
             prompt
            | self.llmm
            | StrOutputParser()
        )
        
        
        self.result = final_rag_chain.invoke({"question": self.question})
        
        # print(self.result)
        
        return self.result
    
 
# question = ['Which of the following is a fundamental unit in the SI system? - Second', 'A body of mass 10 kg is moving with a velocity of 5 m/s. What is its kinetic energy? - 500 J', 'A particle is moving in a circular path of radius 10 m with a constant speed of 20 m/s. What is the centripetal force acting on the particle? - 160 N', 'A convex lens of focal length 10 cm forms an image of an object placed 20 cm from the lens. What is the magnification of the image? - +1', 'A parallel plate capacitor has a capacitance of 10 μF. If the distance between the plates is doubled, what will be the new capacitance? - 20 μF', 'A force of 10 N is applied on an object for 5 seconds. What is the total work done on the object? - 100 J', 'A particle is moving with a velocity of 10 m/s. If its velocity is doubled, what will be its new velocity? - 20 m/s', 'A spring has a spring constant of 100 N/m. If a force of 50 N is applied on the spring, what will be its extension? - 2 m', 'A current of 2 A flows through a resistance of 4 Ω. What is the power consumed by the resistance? - 16 W', 'A particle is moving in a circular path of radius 5 m with a constant speed of 10 m/s. What is the centripetal force acting on the particle? - 80 N', 'A convex lens of focal length 20 cm forms an image of an object placed 30 cm from the lens. What is the magnification of the image? - +1', 'A parallel plate capacitor has a capacitance of 20 μF. If the distance between the plates is halved, what will be the new capacitance? - 40 μF', 'A force of 20 N is applied on an object for 3 seconds. What is the total work done on the object? - 240 J', 'A particle is moving with a velocity of 15 m/s. If its velocity is tripled, what will be its new velocity? - 15 m/s', 'A spring has a spring constant of 50 N/m. If a force of 25 N is applied on the spring, what will be its extension? - 2 m', 'A current of 3 A flows through a resistance of 6 Ω. What is the power consumed by the resistance? - 36 W', 'A particle is moving in a circular path of radius 10 m with a constant speed of 20 m/s. What is the kinetic energy of the particle? - 1600 J', 'A convex lens of focal length 15 cm forms an image of an object placed 25 cm from the lens. What is the magnification of the image? - +1', 'A parallel plate capacitor has a capacitance of 30 μF. If the distance between the plates is tripled, what will be the new capacitance? - 30 μF', 'A force of 30 N is applied on an object for 2 seconds. What is the total work done on the object? - 240 J', 'A particle is moving with a velocity of 20 m/s. If its velocity is halved, what will be its new velocity? - 15 m/s', 'A spring has a spring constant of 75 N/m. If a force of 37.5 N is applied on the spring, what will be its extension? - 2 m', 'A current of 4 A flows through a resistance of 8 Ω. What is the power consumed by the resistance? - 64 W', 'A particle is moving in a circular path of radius 15 m with a constant speed of 30 m/s. What is the centripetal force acting on the particle? - 360 N', 'A convex lens of focal length 25 cm forms an image of an object placed 35 cm from the lens. What is the magnification of the image? - +1', 'A parallel plate capacitor has a capacitance of 40 μF. If the distance between the plates is doubled, what will be the new capacitance? - 40 μF', 'A force of 40 N is applied on an object for 1.5 seconds. What is the total work done on the object? - 240 J', 'A particle is moving with a velocity of 25 m/s. If its velocity is quadrupled, what will be its new velocity? - 15 m/s', 'A spring has a spring constant of 100 N/m. If a force of 50 N is applied on the spring, what will be its extension? - 2 m', 'A current of 5 A flows through a resistance of 10 Ω. What is the power consumed by the resistance? - 100 W']
    
# ex = Exam_Score(question)
# hist = ex.get_score()

# print(hist)
        