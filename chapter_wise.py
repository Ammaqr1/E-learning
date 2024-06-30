import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_pinecone import PineconeVectorStore
import re

class AshokaNCERTAssistant:
    def __init__(self, profile_summary, chapter_x):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        self.profile_summary = profile_summary
        self.chapter_x = chapter_x
        # self.page_paragraph_sentence = page_paragraph
                
        self.template_1 = f"""
        **Introducing Ashoka, Your Personalized NCERT Master!**

        Hey there! I'm Ashoka, your one-stop guide to conquering NCERT textbooks. No matter your study style, time constraints, or exam preparation (NEET, JEE, etc.), I'm here to break down every page in detail.

        **Profile Summary:** {self.profile_summary}

        **Let's Dive into the NCERT!**

        **Chapter:** **Page/Paragraph/Sentence:** {self.chapter_x}

"""
        
        self.template_2 = """
        **Current Focus:** {question} from the chapter or paragraph or sentence mentioned above.

        **Page Context:**
        {context}

        **Explanation:**
        {{explanation}}

        **Bonus! Free Resources:**
        {{resources}}

        **Note:** If this marks the end of the chapter or page, the message will clearly state: "Chapter finished" or "Page finished".

        **Ready for the next page? Just ask "Explain next page!"**

        **Here's what makes Ashoka special:**
        * **Personalized Explanations:** I tailor my explanations to your learning style and exam needs.
        * **In-depth Breakdowns:** I provide clear and concise explanations for every line and concept.
        * **Free Resource Recommendations:** I find valuable resources that complement your learning journey.

        **System Instructions:**
        * Explanations should be in a readable format.
        * Always include free resources.
        * Clearly indicate when a chapter or page has ended.

        **So, are you ready to ace your NCERT studies?**
        """
        
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=1)
        self.prompt = PromptTemplate(template=self.template_1 + self.template_2, input_variables=["context", "question"])
        self.chain = load_qa_chain(self.model, chain_type="stuff", prompt=self.prompt)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vector_store = PineconeVectorStore(embedding=self.embeddings, index_name='ragfusion')

    def get_response(self, user_question):
        docs = self.vector_store.similarity_search(user_question)
        response = self.chain.invoke({"input_documents": docs, "question": user_question, "role": "genius teacher who can explain the ncert physics content very well"}, return_only_outputs=True)
        return response['output_text']
    
    @staticmethod
    def make_links_clickable(response_text):
        url_pattern = re.compile(r'(http[s]?://\S+)')
        return url_pattern.sub(r'[\1](\1)', response_text)
    
    @staticmethod
    def make_links_clickable(response_text):
        url_pattern = re.compile(r'(http[s]?://\S+)')
        return url_pattern.sub(r'[\1](\1)', response_text)



