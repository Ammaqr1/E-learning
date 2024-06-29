from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import GoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from database2 import PostgresDatabase

class QAsummary:
    def __init__(self, user_id,conversational_id):
        # Initialize the database connection with default parameters
        self.db = PostgresDatabase()
        self.db.connect()
        self.user_id = user_id
        self.conversational_id = conversational_id

        # Instruction to the system
        self.instruction_to_system = '''
        
        You are an execcellent physics tutor After analyzing the all the questions and answers from the history, come up with a summary of the student's performance. 
        Describe their weaknesses and provide the best solutions to address these weaknesses.After give some best free resourcess to overcome those mentioned weakness,Also note that 
        Do not give description if the history of humman messages are less than two:
        Provide the summary in the following structure: 
        

        Summary: 
        Weaknesses: 
        Solutions: 
        Resources:
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
        chat_history = self.db.get_message_history(self.user_id, self.conversational_id)
        print(chat_history)
        
        # print('chat history',chat_history)

        # Format the prompt template with chat history
        formatted_messages = self.question_make_prompt.format_messages(
            chat_history=chat_history,
            question='',
        )
        
        print("The mesage is ",formatted_messages)

        # Generate response from the language model
        response = self.llm.invoke(formatted_messages)

        # Split response into a list of questions
        question_list = response.strip().split('\n')
        
        # self.db.save_message(self.user_id,f'summary_{self.user_id}','assistant',question_list)
        

        return question_list

# # Example usage:
# if __name__ == "__main__":
#     # Initialize QuestionGenerator with user_id
    # generator = QuestionGenerator(user_id='jkl;!')

#     # Generate list of questions
#     question_list = generator.fetch_questions()
#     print(question_list)

    # Print or use the generated questions as needed
