from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from langdetect import detect
from app.config import MODEL_NAME, SIMILARITY_THRESHOLD
from app.embeddings import embed_query
from app.vectorstore import search

_tokenizer = None
_model = None


def load_llm():
    global _tokenizer, _model

    if _model is None:
        print("Loading generation model...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    return _tokenizer, _model


def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"


def build_prompt(context_chunks, question, lang="en"):
    context_text = "\n\n".join(context_chunks)

    if lang == "hi":
        prompt = f"""
आप एक आधिकारिक विश्वविद्यालय सहायक हैं।

केवल नीचे दिए गए संदर्भ के आधार पर उत्तर दें।
यदि उत्तर संदर्भ में नहीं है, तो कहें:
"मेरे पास इस विषय में सत्यापित जानकारी उपलब्ध नहीं है।"

संदर्भ:
{context_text}

प्रश्न:
{question}

उत्तर:
"""
    else:
        prompt = f"""
You are an official university assistant.

Answer ONLY using the provided context.
If the answer is not found in the context, say:
"I do not have verified information about this."

Context:
{context_text}

Question:
{question}

Answer:
"""

    return prompt


def generate_answer(question):
    lang = detect_language(question)

    query_embedding = embed_query(question)
    results = search(query_embedding)

    # Filter by similarity threshold
    filtered = [r for r in results if r["score"] >= SIMILARITY_THRESHOLD]

    if not filtered:
        if lang == "hi":
            return {
                "answer": "मेरे पास इस विषय में सत्यापित जानकारी उपलब्ध नहीं है।",
                "sources": []
            }
        else:
            return {
                "answer": "I do not have verified information about this.",
                "sources": []
            }

    context_chunks = [r["text"] for r in filtered]

    prompt = build_prompt(context_chunks, question, lang)

    tokenizer, model = load_llm()

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=0.2,
            do_sample=False
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Suggested follow-up
    if lang == "hi":
        follow_up = "\n\nआप और क्या जानना चाहेंगे? उदाहरण: प्रवेश प्रक्रिया, शुल्क संरचना, छात्रावास नियम।"
    else:
        follow_up = "\n\nWould you like information about admission process, fee structure, hostel rules, or departments?"

    return {
        "answer": response.strip() + follow_up,
        "sources": list(set([r["doc_id"] for r in filtered]))
    }