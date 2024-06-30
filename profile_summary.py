from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import GoogleGenerativeAI, HarmBlockThreshold, HarmCategory
# from database2 import PostgresDatabase
from database3 import SQLiteDatabase

class Profile_summary:
    def __init__(self, user_id):
        # Initialize the database connection with default parameters
        self.db = SQLiteDatabase()
        self.db.connect('chat_database.db')
        self.user_id = user_id
        print(user_id)
        print(self.user_id)

        # Instruction to the system
        self.instruction_to_system = '''
        After analyzing the student's responses to the following sixteen questions, generate a comprehensive summary of their performance and preparation status. 
        Describe their weaknesses and provide solutions to address these weaknesses. 
        Provide the summary in the following structure:

        Summary: 
        Weaknesses: 
        Solutions: 

        Questions:
        1. What is your name?
        2. Which exam(s) are you preparing for (e.g., NEET, JEE, higher secondary exams)?
        3. How old are you?
        4. What is your gender?
        5. How many times have you attempted these exams before?
        6. How would you self-assess your proficiency level in physics (e.g., easy, medium, hard)?
        7. Which school or institution are you currently attending?
        8. How much time do you dedicate to studying physics each week?
        9. Do you use any additional resources (e.g., coaching classes, online courses, textbooks) for your exam preparation?
        10. What are your strengths and weaknesses in specific physics topics (e.g., mechanics, thermodynamics, electromagnetism)?
        11. Do you prefer certain types of learning methods (e.g., visual aids, hands-on experiments, reading textbooks)?
        12. What is your target score or rank for your upcoming exam?
        13. Do you have a study plan or schedule?
        14. When is your next exam scheduled?
        15. Do you participate in any group study sessions or discussions?
        16. What is your motivation or reason for choosing your specific exam (e.g., career goals, personal interest)?
        17. Do you have any particular challenges or obstacles in your preparation (e.g., time management, understanding complex concepts)?

        Analyze the responses to these questions and generate the summary accordingly.
        rules:
        ** if there are valuable answers from the question ->  prepare a summary according to the format 
        ** Don't forgot to get profile summary using format
        
                    ** summary **: ........
                    ** Weakness **:.....
                    ** Solution **:....
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

        # Format the prompt template with chat history
        formatted_messages = self.question_make_prompt.format_messages(
            chat_history=chat_history,
            question='',
        )

        # Generate response from the language model
        response = self.llm.invoke(formatted_messages,returns_only_output = True)

        # Split response into a list of questions
        profile_summary = response.strip().split('\n')
        # print(profile_summary)
        
        self.db.clear_message_history(self.user_id,f'profile_summary_{self.user_id}')
        self.db.save_message(self.user_id,f'profile_summary_{self.user_id}','assistant',profile_summary)
        
        
        
        

        

# # Example usage:
# if __name__ == "__main__":
# #     # Initialize QuestionGenerator with user_id
    
#     db = PostgresDatabase(dbname='new_db_name', user='postgres', password='ammar')
#     db.connect()
#     generator = Profile_summary(user_id=';lakj')
#     generator.fetch_questions()
#     h = db.get_message_history(';lakj','profile_summary_;lakj')
#     print(h)
#     # Generate list of questions
#     generator.fetch_questions()
    
#     print(db.get_message_history('hello','profile_summary_hello'))
    # print(question_list)

    # Print or use the generated questions as needed
