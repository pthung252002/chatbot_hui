import traceback
import requests
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

# Khai báo chung
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local("vector_db", embedding)

# Danh sách API key của Gemini để luân phiên sử dụng
API_KEYS = [

]

# Mẫu prompt để kết hợp context và câu hỏi người dùng
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

def call_gemini_api(prompt: str, api_key: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, headers=headers, json=body, timeout=15)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

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
        print(f"[1] Câu hỏi từ người dùng: {user_question}")

        # Trích xuất context từ vectorstore FAISS
        docs = vectorstore.similarity_search(user_question, k=4)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Dựng prompt
        final_prompt = custom_prompt_template.format(context=context, question=user_question)

        answer = "Xin lỗi, đã có lỗi xảy ra khi xử lý câu hỏi của bạn."

        for api_key in API_KEYS:
            try:
                print(f"[2] Đang thử key: {api_key[:15]}...")
                answer = call_gemini_api(final_prompt, api_key)
                print(f"[3] Dùng key {api_key[:15]}... thành công! \n")
                break
            except Exception as e:
                print(f"Key {api_key[:15]}... lỗi: {str(e)} \n")
                print(traceback.format_exc())
                continue

        dispatcher.utter_message(json_message={"html": answer})
        return []

class ActionAnswerDuration(Action):
    def name(self) -> Text:
        return "action_answer_duration"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_question = tracker.latest_message.get("text")
        print(f"[1] Câu hỏi từ người dùng: {user_question}")

        # Trích xuất context từ vectorstore FAISS
        docs = vectorstore.similarity_search(user_question, k=4)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Dựng prompt
        final_prompt = custom_prompt_template.format(context=context, question=user_question)

        answer = "Xin lỗi, đã có lỗi xảy ra khi xử lý câu hỏi của bạn."

        for api_key in API_KEYS:
            try:
                print(f"[2] Đang thử key: {api_key[:15]}...")
                answer = call_gemini_api(final_prompt, api_key)
                print(f"[3] Dùng key {api_key[:15]}... thành công! \n")
                break
            except Exception as e:
                print(f"Key {api_key[:15]}... lỗi: {str(e)} \n")
                print(traceback.format_exc())
                continue

        dispatcher.utter_message(json_message={"html": answer})
        return []

class ActionAnswerUnkownQuestions(Action):
    def name(self) -> Text:
        return "action_handle_unknown_question"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_question = tracker.latest_message.get("text")
        print(f"[1] Câu hỏi từ người dùng: {user_question}")

        # Trích xuất context từ vectorstore FAISS
        docs = vectorstore.similarity_search(user_question, k=4)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Dựng prompt
        final_prompt = custom_prompt_template.format(context=context, question=user_question)

        answer = "Xin lỗi, đã có lỗi xảy ra khi xử lý câu hỏi của bạn."

        for api_key in API_KEYS:
            try:
                print(f"[2] Đang thử key: {api_key[:15]}...")
                answer = call_gemini_api(final_prompt, api_key)
                print(f"[3] Dùng key {api_key[:15]}... thành công! \n")
                break
            except Exception as e:
                print(f"Key {api_key[:15]}... lỗi: {str(e)} \n")
                print(traceback.format_exc())
                continue

        dispatcher.utter_message(json_message={"html": answer})
        return []