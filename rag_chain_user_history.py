import os
import json
import asyncio
from datetime import datetime

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_community.chat_message_histories import ChatMessageHistory
from database2 import PostgresDatabase

import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.load import dumps
from langchain_google_genai import GoogleGenerativeAI, HarmBlockThreshold, HarmCategory



class RAGSystem:
    def __init__(self, db_config, index_name):
        self.db = PostgresDatabase(**db_config)
        self.db.connect()

        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')

        # Initialize Pinecone
        self.index_name = index_name

        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        # Create PineconeVectorStore
        self.vector_store = PineconeVectorStore(embedding=self.embeddings, index_name=self.index_name)

        self.retriever = self.vector_store.as_retriever(search_type='mmr')

        # Template for generating query perspectives
        template = """You are an AI language model assistant. Your task is to generate five 
        different versions of the given user question to retrieve relevant documents from a vector 
        database. By generating multiple perspectives on the user question, your goal is to help
        the user overcome some of the limitations of the distance-based similarity search. 
        Provide these alternative questions separated by newlines. Original question: {question}"""

        self.prompt_perspectives = ChatPromptTemplate.from_template(template)
        self.model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

        self.generate_queries = (
            self.prompt_perspectives 
            | self.model
            | StrOutputParser() 
            | (lambda x: x.split("\n"))
        )
        
    

        self.retrieval_chain_rag_fusion = self.generate_queries | self.retriever.map() | self.reciprocal_rank_fusion




        # Creating the prompt template
        self.question_make_prompt = ChatPromptTemplate.from_messages(
            [
                ('system', self.instruction_to_system),
                MessagesPlaceholder(variable_name='chat_history'),
                ('human', '{question}')
            ]
        )

        self.llm = GoogleGenerativeAI(
            model="gemini-pro",
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )

    def reciprocal_rank_fusion(self, results: list[list], k=60):
        """ Reciprocal_rank_fusion that takes multiple lists of ranked documents 
            and an optional parameter k used in the RRF formula """
        
        fused_scores = {}

        for docs in results:
            for rank, doc in enumerate(docs):
                doc_str = dumps(doc)
                if doc_str not in fused_scores:
                    fused_scores[doc_str] = 0
                previous_score = fused_scores[doc_str]
                fused_scores[doc_str] += 1 / (rank + k)

        reranked_results = [
            (json.loads(doc), score)
            for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        ]

        return reranked_results

    def main(self, question, user_id):
        history = self.db.get_message_history(user_id, 'default')

        context = self.retrieval_chain_rag_fusion.invoke({"question": question})

        template = """
        You are an AI language model assistant. Given the context and question, provide a response according to the following criteria:

        1. If the context is found and it matches the question, provide an expanded and detailed explanation. Make sure to clarify all relevant concepts thoroughly.
        2. If no relevant context is found, simply respond with "I don't know."

        Context:
        {context}

        Question:
        {question}

        Response:
"""

        prompt = ChatPromptTemplate.from_template(template)

        final_rag_chain = (
            {"context": context, "question": itemgetter("question")}
            | prompt
            | self.model
            | StrOutputParser()
        )

        answer = final_rag_chain.invoke({'question': question})

        print(answer)


if __name__ == "__main__":
    db_config = {
        'dbname': 'new_db_name',
        'user': 'postgres',
        'password': 'ammar'
    }
    index_name = "ragfusion"

    rag_system = RAGSystem(db_config, index_name)
    rag_system.main("give me the first 2 pages summary of icd 11", "user124")
