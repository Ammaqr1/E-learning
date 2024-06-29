import os
import pdfplumber
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from operator import itemgetter
from langchain_pinecone import PineconeVectorStore
from langchain.load import dumps
import json
from database2 import PostgresDatabase
import streamlit as st





class RAGSystem:
    def __init__(self, user_id):
        load_dotenv()  # Ensure environment variables are loaded
        os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')

        self.index_name = "ragfusion"
        self.user_id = user_id
        
        # Initialize database connection
        self.db = PostgresDatabase()
        self.db.connect()
        
        self.setup_generative_ai()
        self.setup_vector_store()

    def setup_generative_ai(self):
        # Configure Google Generative AI
        self.model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
        
        template = """You are an AI language model assistant. Your task is to generate only five 
        different versions of the given user question to retrieve relevant documents from a vector 
        database. By generating multiple perspectives on the user question, your goal is to help
        the user overcome some of the limitations of the distance-based similarity search. 
        Provide these alternative questions separated by newlines. Original question: {question}"""
        
        
        self.prompt_perspectives = ChatPromptTemplate.from_template(template)

    def setup_vector_store(self):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vector_store = PineconeVectorStore(embedding=embeddings, index_name=self.index_name)
        self.retriever = self.vector_store.as_retriever()

    def reciprocal_rank_fusion(self, results: list[list], k=60):
        # Perform reciprocal rank fusion on retrieved results
        fused_scores = {}
        for docs in results:
            for rank, doc in enumerate(docs):
                doc_str = dumps(doc)
                if doc_str not in fused_scores:
                    fused_scores[doc_str] = 0
                fused_scores[doc_str] += 1 / (rank + k)
        reranked_results = [
            (json.loads(doc), score)  # Use json.loads instead of loads
            for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        ]
        return reranked_results

    def answer_question_using_rag(self, question):
        self.generate_queries = (
            self.prompt_perspectives
            | self.model
            | StrOutputParser()
            | (lambda x: x.split("\n"))
        )
        
        retrieval_rag_chain = self.generate_queries | self.retriever.map() | self.reciprocal_rank_fusion
        # context = retrieval_rag_chain.invoke({'question': question})
        
        profile_summary_dict = self.db.get_message_history(self.user_id, f'profile_summary_{self.user_id}')
        profile_summary = [messages['content'][1:-1] for messages in profile_summary_dict]
        
        answer_template_1 = f"""Task: Clear doubts and provide detailed explanations.
        Subject: Physics
        Profile Summary: {profile_summary}
        """
        answer_template_2 = """
        Chapter: {context}
        Doubt: {question}
        Role: 
        Instructions:
        1. Review the provided profile summary to understand the learner's background, strengths, and weaknesses.
        2. Receive a specific doubt or question related to ncert physics chapter class 11 from the learner.
        3. Provide a detailed, clear explanation tailored to the learner's understanding and learning style.
        4. Include step-by-step guidance and related concepts to ensure comprehensive understanding.
        5. Suggest free resources (e.g., websites, videos, articles) for further learning and practice.
        Output Format:
        1. Doubt/Question: [Present the learner's doubt or question]
        2. Detailed Explanation:
        - Clear and concise answer to the question.
        - Step-by-step explanation or solution, if applicable.
        - Related concepts and deeper insights.
        - Examples or analogies to aid understanding.
        - Tips on areas to focus on for better understanding.
        3. Free Resources:
        - List of websites, videos, or articles that provide additional explanations or practice problems related to the question.
        Profile Summary Example:
        - Background: [Student's previous education, familiarity with physics, etc.]
        - Strengths: [Specific areas where the student excels]
        - Weaknesses: [Specific areas where the student struggles]
        - Learning Style: [Preferred learning methods, e.g., visual, auditory, kinesthetic]
        Example Output:
        1. Doubt/Question: Why does an object in motion stay in motion according to Newton's first law?
        2. Detailed Explanation:
        - Newton's first law, also known as the law of inertia, states that an object will remain at rest or in uniform motion in a straight line unless acted upon by an external force. This means that in the absence of any force, an object's motion will not change.
        - Step-by-step explanation: If you push a book on a table, it moves and then gradually stops because of friction. Without friction (in an ideal frictionless environment), the book would keep moving indefinitely.
        - Related concepts: Inertia, external forces, friction, equilibrium.
        - Example: Think of an ice puck gliding on an ice rink. It moves much farther than a book on a table because there is much less friction on the ice.
        - Tips: Focus on understanding the role of external forces like friction and gravity in changing the motion of objects.
        3. Free Resources:
        - [Khan Academy](https://www.khanacademy.org/science/physics): Provides video lessons and practice problems on Newton's laws of motion.
        - [
        """

        prompt = ChatPromptTemplate.from_template(answer_template_1 + answer_template_2)
        final_rag_chain = (
            {"context": retrieval_rag_chain, "question": itemgetter("question")}
            | prompt
            | self.model
            | StrOutputParser()
        )
        
        result = final_rag_chain.invoke({"question": question})
        print(f'Result: {result}')
        return result
        
    def main(self):
        question = st.text_input("Enter your question:")
        if st.button('Submit'):
            if question:
                answer = self.answer_question_using_rag(question)
                st.write(f"Answer: {answer}")
                self.db.save_message(self.user_id,f'live_doubts_{self.user_id}','user',question)
                self.db.save_message(self.user_id,f'live_doubts_{self.user_id}','assistant',answer)
                
            else:
                st.write("Please provide all inputs.")
                


