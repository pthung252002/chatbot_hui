from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os
import traceback

# Danh sách API key từ OpenRouter để thay khi hết token
API_KEYS = [
    "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", #hung2508-github
    "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", #hungkr
    "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", #hung2508
    "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", #hunggr
    "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", #hung12
]

# Khai báo chung
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local("vector_db", embedding)

custom_prompt_template = """Sử dụng thông tin dưới đây để trả lời câu hỏi của người dùng.

- Nếu bạn không biết câu trả lời, hãy nói là bạn không biết và nhờ người dùng đặt lại câu hỏi rõ ràng hơn, đừng bịa ra câu trả lời.
- Tất cả câu trả lời PHẢI được viết bằng tiếng Việt.
- Câu trả lời PHẢI bao gồm đầy đủ các bước hướng dẫn, kèm theo **mọi thông tin liên quan xuất hiện sau các bước**, đặc biệt là **hình ảnh minh họa (<img>)** và **video hướng dẫn (<iframe>)** NẾU CÓ.
- KHÔNG được bịa ra bất kỳ thông tin nào nếu không có trong context.
- Câu trả lời PHẢI được định dạng bằng HTML đơn giản: <p>, <b>, <ul>, <li>, <br>. KHÔNG dùng markdown hoặc các ký tự đặc biệt.
- Luôn xưng hô là "Em" và gọi người dùng là "Anh/Chị".

Context: {context}
Question: {question}
"""

custom_prompt = PromptTemplate(
    template=custom_prompt_template,
    input_variables=["context", "question"]
)

def create_llm(api_key: str):
    return ChatOpenAI(
        model_name="qwen/qwen2.5-vl-72b-instruct:free",  # hoặc model bạn muốn
        temperature=0,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        request_timeout=15  # giới hạn tối đa 15 giây
    )

# Hàm để reset slot sau khi cang cấp các hướng dẫn
class ActionResetSlots(Action):
    def name(self):
        return "action_reset_slots"

    def run(self, dispatcher, tracker, domain):
        return [
            SlotSet("hoat_dong_chinh", None),
            SlotSet("hoat_dong_phu", None),
            SlotSet("doi_tuong", None),
            SlotSet("doi_tuong_phu", None),
            SlotSet("trang_thai", None),
            SlotSet("tro_tu", None),
            SlotSet("tro_tu2", None)
        ]
class ActionProvideGuide(Action):

    def name(self) -> Text:
        return "action_provide_guide"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_question = tracker.latest_message.get("text")
        print(f"** Câu hỏi từ người dùng: {user_question}")

        answer = "Xin lỗi, đã có lỗi xảy ra khi xử lý câu hỏi của bạn."

        for api_key in API_KEYS:
            try:
                print(f"Đang thử key: {api_key[:15]}...")
                llm = create_llm(api_key)
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    retriever=vectorstore.as_retriever(),
                    chain_type="stuff",
                    chain_type_kwargs={"prompt": custom_prompt},
                    return_source_documents=True
                )
                result = qa_chain({"query": user_question})
                answer = result["result"]

                print(f"Dùng key {api_key[:15]}... thành công!")
                #for doc in result["source_documents"]:
                    #print("📄 Chunk:\n", doc.page_content[:1000])
                break  # Thành công thì dừng thử key tiếp theo

            except Exception as e:
                print(f"Key {api_key[:15]}... lỗi: {str(e)}")
                print(traceback.format_exc())
                continue

        dispatcher.utter_message(json_message={"html": answer})
        return []

class ActionAnswerDuration(Action):
    def name(self) -> Text:
        return "action_answer_duration"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_question = tracker.latest_message.get("text")
        print(f"** Câu hỏi từ người dùng: {user_question}")

        answer = "Xin lỗi, đã có lỗi xảy ra khi xử lý câu hỏi của bạn."

        for api_key in API_KEYS:
            try:
                print(f"Đang thử key: {api_key[:15]}...")
                llm = create_llm(api_key)
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    retriever=vectorstore.as_retriever(),
                    chain_type="stuff",
                    chain_type_kwargs={"prompt": custom_prompt},
                    return_source_documents=True
                )
                result = qa_chain({"query": user_question})
                answer = result["result"]

                print(f"Dùng key {api_key[:15]}... thành công!")
                #for doc in result["source_documents"]:
                    #print("📄 Chunk:\n", doc.page_content[:1000])
                break  # Thành công thì dừng thử key tiếp theo

            except Exception as e:
                print(f"Key {api_key[:15]}... lỗi: {str(e)}")
                print(traceback.format_exc())
                continue

        dispatcher.utter_message(json_message={"html": answer})
        return []
