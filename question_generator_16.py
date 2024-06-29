from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import GoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from database2 import PostgresDatabase  # Replace with actual import for your database
import os
import google.generativeai as genai
from dotenv import load_dotenv

class QuestionGenerator16:
    def __init__(self, user_id):
        # Initialize the database connection with default parameters
        self.db = PostgresDatabase(dbname='new_db_name', user='postgres', password='ammar')
        self.db.connect()
        self.user_id = user_id
        
        
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)

        # Instruction to the system
        self.instruction_to_system = '''
        Create a set of 16 questions and profile_ that directly assess a student's knowledge and understanding of fundamental physics concepts. 
        Ensure each question focuses on testing the student's grasp of essential theories, laws, and principles commonly covered in physics exams.
        These questions should be designed to evaluate conceptual understanding rather than study habits or exam preparation strategies.
        if the chat history is None generate a 16 question which is based on physics text book
        '''

        # Creating the prompt template
        self.question_make_prompt = ChatPromptTemplate.from_messages([
            ('system', self.instruction_to_system),
            MessagesPlaceholder(variable_name='chat_history'),
            ('human', '{question}')
        ])

        # Initialize the language model
        self.llm = GoogleGenerativeAI(
            model="gemini-pro",
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )

    def fetch_questions(self):
        # Fetch message history based on user_id from the database
        chat_history = self.db.get_message_history(self.user_id, f'profile_evaluation_{self.user_id}')
        
        print(chat_history)

        # Format the prompt template with chat history
        formatted_messages = self.question_make_prompt.format_messages(
            chat_history=chat_history,
            question='',

        )

        # Generate response from the language model
        response = self.llm.invoke(formatted_messages)
        
        # Split response into a list of questions
        question_list = response.strip().split('\n')
        
        self.db.save_message(self.user_id,f'profile_questions16_{self.user_id}','assistant',question_list)
        
        print(question_list)

        return question_list

# # Example usage:
# if __name__ == "__main__":
#     # Initialize QuestionGenerator with user_id
#     generator = QuestionGenerator(user_id='user124')

#     # Generate list of questions
#     question_list = generator.fetch_questions()

#     # Print or use the generated questions as needed
#     print(question_list)
