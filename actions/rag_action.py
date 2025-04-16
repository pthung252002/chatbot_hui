# actions/rag_action.py

import os
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
# LangChain components
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings


embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local("vector_db/", embedding)

custom_prompt_template = """Sử dụng thông tin dưới đây để trả lời câu hỏi của người dùng.

- Nếu bạn không biết câu trả lời, hãy trả lời "Tôi không biết", đừng bịa ra câu trả lời.
- Tất cả câu trả lời PHẢI được viết bằng tiếng Việt.
- Câu trả lời phải đủ các bước và những nội dung kèm theo.
- Câu trả lời PHẢI được định dạng bằng HTML đơn giản, bao gồm các thẻ như: <p>, <b>, <ul>, <li>, <br>.
- Các câu xuống dùng thì hãy dùng thẻ <br> trong html.
- Thẻ <img> và thẻ <iframe> trong thml phải được cách nhau bằng thẻ <br>.
- Hãy luôn xưng hô là "Em" và gọi người dùng là "Anh/Chị".

Context: {context}
Question: {question}
"""

custom_prompt = PromptTemplate(
    template=custom_prompt_template,
    input_variables=["context", "question"]
)

# LLM từ OpenRouter (DeepSeek)
os.environ["OPENAI_API_KEY"] = "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"  # 🔁 Thay bằng OpenRouter key
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

llm = ChatOpenAI(
    model_name="deepseek/deepseek-r1-distill-qwen-32b:free",
    temperature=0.2,
    openai_api_base=os.environ["OPENAI_API_BASE"],
    openai_api_key=os.environ["OPENAI_API_KEY"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type="stuff",
    chain_type_kwargs={"prompt": custom_prompt}
)

class ActionAskRAG(Action):

    def name(self) -> Text:
        return "action_rag_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_question = tracker.latest_message.get("text")

        try:
            result = qa_chain({"query": user_question})
            answer = result["result"]
        except Exception as e:
            answer = f"Lỗi khi tìm câu trả lời: {str(e)}"

        dispatcher.utter_message(text=answer)
        return []
