import os
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain.load import dumps
from database3 import SQLiteDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq





class Exam:
    def __init__(self,user_id):
        load_dotenv()  # Ensure environment variables are loaded
        os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')

        self.index_name = "ragfusion"
        self.user_id = user_id
        self.db = SQLiteDatabase()
        self.db.connect('chat_database.db')
        
        
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        

        
        self.setup_generative_ai()
        self.setup_vector_store()

    def setup_generative_ai(self):
        # Configure Google Generative AI
        self.model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
        self.llm = ChatGroq(temperature=0, groq_api_key=self.api_key, model_name="llama3-8b-8192")
        self.llmm = ChatGroq(temperature=0, groq_api_key=self.api_key, model_name="llama3-70b-8192")


        

    def setup_vector_store(self):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vector_store = PineconeVectorStore(embedding=embeddings, index_name=self.index_name)
        self.retriever = self.vector_store.as_retriever()
        


    def get_question(self):

                
        profile_summary_dict = self.db.get_message_history(self.user_id, f'profile_summary_{self.user_id}')
        profile_summary = [messages['content'][1:-1] for messages in profile_summary_dict]
        
        if len(profile_summary)<4:
            profile_summary = 'Name unknown preparing for jee examination'
        
        print('profile_summmmi',profile_summary)
                
        answer_template_1 = f"""
        You are an AI language model assistant. Your task is to generate multiple-choice
        questions (MCQs) based on the user's profile summary, which includes details on their preparation for a 
        specific exam. Ensure that the questions are from the NCERT physics syllabus for class 11 and 12.
        profile_summary: {profile_summary}
        """

        answer_template_2 = """

      You are an AI assistant generating multiple-choice questions (MCQs) for a specific exam based on the user's profile summary. Ensure questions are from the NCERT physics syllabus for class 11 and 12.

            Instructions:
            1. Determine the exam the learner is preparing for (e.g., JEE, NEET, Higher Secondary, CUET) from the profile summary.
            2. Identify the typical number of physics questions in that exam.
            3. Generate a set of MCQs from the NCERT physics syllabus for class 11 or 12.
            4. Provide four answer options for each question, including one correct answer.
            5. Ensure each subsequent question is progressively harder than the previous one.
            6. Do not repeat questions.
            7. Question should have exact information inorder to get the answer For eg:
            
            Do not give question like this 
             Question: A force of 40 N is applied on an object for 1.5 seconds. What is the total work done on the object?  
                Given answer: 240 J
                Correct answer: The work done (W) is given by the formula:
                W = F × d
                where F is the force and d is the distance.
                Since the distance is not provided, we cannot calculate the exact value of the work done. However, the given answer 240 J is possible if the distance is 6 m. (Insufficient information)
            


            Example Output for NEET (45 physics questions):

            1. Question: Which of the following is a fundamental unit in the SI system?
            a) Meter
            b) Kilogram
            c) Second
            d) All of the above

            2. Question: A body of mass 10 kg is moving with a velocity of 5 m/s. What is its kinetic energy?
            a) 125 J
            b) 250 J
            c) 500 J
            d) 1000 J

            3. Question: A particle is moving in a circular path of radius 10 m with a constant speed of 20 m/s. What is the centripetal force acting on the particle?
            a) 40 N
            b) 80 N
            c) 160 N
            d) 320 N

            4. Question: A convex lens of focal length 10 cm forms an image of an object placed 20 cm from the lens. What is the magnification of the image?
            a) -1
            b) -2
            c) +1
            d) +2

            5. Question: A parallel plate capacitor has a capacitance of 10 μF. If the distance between the plates is doubled, what will be the new capacitance?
            a) 5 μF
            b) 10 μF
            c) 20 μF
            d) 40 μF

            If the profile summary does not mention a specific exam, generate a minimum of 30 (thirty) NCERT physics questions.
            If the query is outside the scope of NCERT physics, respond with "I only know answers related to NCERT physics."
                    """


 

        docs2 = self.retriever.invoke('questions of previous examinations')


      
        prompt = ChatPromptTemplate.from_template(answer_template_1 + answer_template_2)
        
  
        final_rag_chain = (
             prompt
            | self.llmm
            | StrOutputParser()
            | (lambda x: x.split("\n")) 
        )
        
        question = 'start the exam'
        
        self.result = final_rag_chain.invoke({'context':docs2,"question": question})
        
    def get_question_paper(self):
        self.get_question()
        
        
        
        questions = []
        question = None
        options = []

        for line in self.result:
            line = line.strip()
            # print(f"Processing line: '{line}'")  # Debug print

            # Identify the line containing the question
            if any([line.startswith(f'{i}. Question:') for i in range(1, 50)]):
                if question:
                    questions.append({
                        'question': question,
                        'options': options
                    })
                question = line.split('Question: ')[1].strip()
                options = []
            elif line.startswith('a)') or line.startswith('b)') or line.startswith('c)') or line.startswith('d)'):
                options.append(line.split(') ')[1].strip())

        # Add the last question if it exists
        if question:
            # print(f"Appending last question: '{question}' with options: {options}")  # Debug print
            questions.append({
                'question': question,
                'options': options
            })
             
        print('the original list',questions)
                
        return questions

                


