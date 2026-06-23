import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MASAR AI API")

# تفعيل الـ CORS لكي يتمكن تيم الـ React أو Laravel من الاتصال بسيرفرك بدون مشاكل أمنية
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في الإنتاج يتم استبداله برابط موقعهم الفعلي
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تهيئة عميل Gemini
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# تحديد شكل البيانات المستقبلة من التيم (السؤال)
class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_with_masar(request: ChatRequest):
    try:
        system_prompt = """
        أنت مساعد ذكي متخصص في إدارة المؤسسات والعمل الإنساني وإعداد التقارير (MASAR).
        مهمتك الأساسية هي مساعدة المؤسسات والجمعيات الخيرية والمنظمات الإنسانية في إعداد التقارير الإدارية وتلخيص الإنجازات.
        يرجى الإجابة باختصار وإيجاز باللغة العربية (لا تتجاوز سطرين أو ثلاثة).
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=request.message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7
            )
        )
        
        # إرجاع الجواب للتيم بصيغة JSON نظيفة
        return {"reply": response.text}
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            raise HTTPException(status_code=429, detail="سيرفر الذكاء الاصطناعي مضغوط حالياً، يرجى إعادة المحاولة.")
        elif "503" in error_msg or "UNAVAILABLE" in error_msg:
            raise HTTPException(status_code=503, detail="الخدمة غير متوفرة مؤقتاً، أعد المحاولة فوراً.")
        else:
            raise HTTPException(status_code=500, detail=error_msg)