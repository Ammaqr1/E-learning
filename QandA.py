    
    
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_pinecone import PineconeVectorStore
from langchain.globals import set_verbose, get_verbose
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from database2 import PostgresDatabase
import re



class AshokaNCERTQA:
    def __init__(self, profile_summary, chapter_x,user_id):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        self.db = PostgresDatabase(dbname='new_db_name', user='postgres', password='ammar')
        self.db.connect()
        
        self.profile_summary = profile_summary
        
        self.chapter_x = chapter_x
        self.user_id = user_id
        
        set_verbose(True)

        
        self.instruction_to_system = f"""
        Task: Generate and evaluate questions.

        Subject: Physics

        Chapter: {self.chapter_x}

        Profile Summary: {self.profile_summary}

        Instructions:
        1. Review the provided profile summary to understand the learner's background, strengths, and weaknesses.
        2. Generate a set of questions specifically related to {self.chapter_x} in physics, tailored to the learner's profile and exam type (NEET, JEE, Higher Secondary, CUET, etc.).
        3. Present one question to the learner at a time based on their request.
        4. Evaluate the learner's answer to each question.

        User Commands:
        - "Ask a question" -> Present a question from the specified chapter.
        - "Next question" -> Present the next question, varying in difficulty (easy, medium, hard).
        - "Give an answer" -> Provide a detailed explanation of the answer provided by the learner.

        Response Logic Based on Chat History:
        1. If the last message in the chat history is "Ask a question":
        - Present a question from the specified chapter, ensuring it's not repetitive.
        2. If the last message in the chat history contains a learner's answer:
        - Evaluate the answer.
        - If correct, provide an expanded explanation of the question and answer, covering related concepts and deeper insights.
        - If incorrect, explain why the answer is wrong, identify areas for improvement, and provide a detailed explanation of the correct answer.
        3. If the last message in the chat history is "Next question":
        - Present the next question, varying in difficulty (easy, medium, hard), and ensuring it's not repetitive.

        Output Format:
        1. Question: [Present the question]
        2. Learner's Answer: [Provide the learner's response]
        3. Explanation (if correct):
        - Detailed explanation of the question and correct answer.
        - Related concepts and deeper insights.
        4. Feedback (if incorrect):
        - Why the answer is wrong.
        - Areas to focus on for improvement.
        - Step-by-step explanation of how to solve the question correctly.

        Example Output:
        1. Question: [Insert question here]
        2. Learner's Answer: [Insert learner's response here]

        If Correct:
        3. Explanation:
        - [Detailed explanation]
        - [Related concepts]

        If Incorrect:
        3. Feedback:
        - Why the answer is wrong: [Explanation]
        - Areas to focus on: [Areas of improvement]
        - Correct solution: [Step-by-step guidance]
        """

        self.template2 = """
       

        Question: {question}
        
        context: {context} explain based on this context

        User Commands:
        * "Ask a question" -> Receive a question from the specified chapter.
        * "Next question" -> Receive the next question, with varying difficulty.
        * "Give an answer" -> Provide a detailed explanation of the learner's response.

        Example Workflow:
        1. User: "Ask a question"
        Bot: [Provides a question tailored to the learner's profile and chapter]
        2. User: [Provides an answer]
        Bot: [Evaluates the answer]
        - If correct, provides an expanded explanation.
        - If incorrect, provides feedback and a detailed explanation.
        3. User: "Next question"
        Bot: [Provides the next question with a different difficulty level]

        Note: The questions should be matched to the learner's profile and relevant exam type (NEET, JEE, Higher Secondary, CUET, etc.)
        """
        
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
        # self.model = ChatVertexAI(model="gemini-pro")


                # Creating the prompt template
        self.question_make_prompt = ChatPromptTemplate.from_messages([
            ('system', self.instruction_to_system + self.template2),
            MessagesPlaceholder(variable_name='chat_history'),
            ('human','context{context}'),
            ('human', '{question}')
        ])


      
        
        
        # self.prompt = PromptTemplate(template=self.instruction_to_system + self.template2, input_variables=["context","question",'role'])
        # self.chain = load_qa_chain(self.model, chain_type="stuff", prompt=self.prompt)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vector_store = PineconeVectorStore(embedding=self.embeddings, index_name='ragfusion')

    def get_response(self, user_question):

        chat_history = self.db.get_message_history(self.user_id,f'question_answer_{self.chapter_x}_{self.user_id}')
        docs = self.vector_store.similarity_search(user_question)
        formated_question = self.question_make_prompt.format_messages(
            chat_history = chat_history,
            context=docs, 
            question = user_question
            
        )
        self.db.save_message(self.user_id,f'question_answer_{self.chapter_x}_{self.user_id}','user',user_question)
        # role = 'A genius ncert physics class 11 question and explanation giver'
        response = self.model.invoke(formated_question)
        self.db.save_message(self.user_id,f'question_answer_{self.chapter_x}_{self.user_id}','assistant',response.content)
        return response.content
    
    @staticmethod
    def make_links_clickable(response_text):
        # Convert URLs in the text to Markdown links
        url_pattern = re.compile(r'(http[s]?://\S+)')
        return url_pattern.sub(r'[\1](\1)', response_text)
    
    

# import streamlit as st


# # Initializing the assistant
# user_id = 'user124'
# assistant = AshokaNCERTQA('Ammar', "ncert text class 11 part1_chapter1 physical world", user_id)

# question = st.text_input('enter your question')

# if question:
#     answer = assistant.get_response(question)
#     st.write(answer)