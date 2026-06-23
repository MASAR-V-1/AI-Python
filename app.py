import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# 1. تهيئة الصفحة (يجب أن يكون أول أمر تفاعلي)
st.set_page_config(page_title="MASAR Chatbot", page_icon="🤖")

# 2. عرض الشعار والعناوين
st.image("logo.png", width=100)
st.title("MASAR's AI Agent 🤖")

# 3. دعم اتجاه القراءة العربي والألوان للثيمين
st.markdown("""
    <style>
        .main .block-container { direction: rtl; text-align: right; }
        .stChatInputContainer { direction: rtl; }
        @media (prefers-color-scheme: light) { h1, h2 { color: #2563eb !important; } .stSpinner { color: #0d9488 !important; } }
        @media (prefers-color-scheme: dark) { h1, h2 { color: #60a5fa !important; } .stSpinner { color: #2dd4bf !important; } }
    </style>
""", unsafe_allow_html=True)

# 4. تثبيت العميل بالكاش
@st.cache_resource
def get_genai_client():
    return genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

client = get_genai_client()

# 5. إدارة الرسائل المرئية
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. استقبال المدخلات وتوليد الاستجابة بموديل مستقر
if user_input := st.chat_input("Ask me for anything..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        with st.spinner("جاري التفكير..."):
            try:
                system_prompt = """
                أنت مساعد ذكي متخصص في إدارة المؤسسات والعمل الإنساني وإعداد التقارير (MASAR).
                مهمتك الأساسية هي مساعدة المؤسسات والجمعيات الخيرية والمنظمات الإنسانية في إعداد التقارير الإدارية وتلخيص الإنجازات.
                يرجى الإجابة باختصار وإيجاز باللغة العربية (لا تتجاوز سطرين أو ثلاثة).
                """
                
                # تم التبديل إلى موديل 1.5 الفلاش المستقر وأوسع الحصص لكسر الـ 429 نهائياً
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_input,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.7
                    )
                )
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                error_msg = str(e)
                # اصطياد خطأ الحصّة 429
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    st.warning("⚠️ الحصة الحالية ممتلئة. يرجى الانتظار ثوانٍ وسيقوم خادم مَسَار بتصفير العداد تلقائياً.")
                
                # اصطياد خطأ الضغط على السيرفر 503 (الجديد)
                elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                    st.info("🔄 سيرفرات جوجل مضغوطة حالياً.. يرجى إعادة إرسال سؤالك الآن وسيعمل مباشرة.")
                
                else:
                    st.error(f"حدث خطأ أثناء الاتصال: {error_msg}")