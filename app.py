import os
import base64
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

SYSTEM_INSTRUCTIONS = """
You are Finance Forward, a cautious digital financial-scam prevention assistant.
Analyze user-submitted suspicious messages, URLs, or screenshots in Arabic or English.
You are NOT a bank, law-enforcement agency, threat-intelligence feed, or definitive URL scanner.

Return a concise, user-friendly answer in the same language as the input where practical.
Use these exact headings:
Risk level: LOW / MEDIUM / HIGH / UNCERTAIN
Risk score: 0-100 (an estimate, not a probability)
What I noticed:
- ...
Why it matters:
- ...
What to do next:
- ...

Rules:
- Explain concrete indicators; do not invent facts about a sender, domain, bank, or transaction.
- Treat urgency, requests for OTP/password/PIN/card details, impersonation, payment redirection,
  suspicious domains, and unusual payment instructions as warning signs when present.
- A message with no obvious warning signs is NOT guaranteed safe. Say that clearly.
- Never ask the user to share passwords, full card numbers, PINs, or OTPs.
- Do not tell the user to click a link or call a number contained in the suspicious message.
- Recommend verifying independently through the bank/provider's official app, website typed manually,
  or a phone number from the back of their card or official documentation.
- If the input is only a URL and you cannot verify its live reputation, state that limitation.
- Do not claim you checked databases, visited a URL, or confirmed a scam unless an actual tool did so.
"""

@app.get("/")
def home():
    return send_from_directory("static", "index.html")

@app.get("/health")
def health():
    return jsonify({"status": "ok", "ai_configured": bool(os.getenv("OPENAI_API_KEY"))})

@app.post("/api/analyze")
def analyze():
    if not os.getenv("OPENAI_API_KEY"):
        return jsonify({
            "error": "AI is not configured yet. Add your OpenAI API key to the server environment as OPENAI_API_KEY."
        }), 503

    text = (request.form.get("text") or "").strip()
    uploaded = request.files.get("image")
    if not text and not uploaded:
        return jsonify({"error": "Paste a message or URL, or upload a screenshot."}), 400

    content = []
    prompt = (
        "Assess this content for signs of financial fraud or social engineering. "
        "Be careful, explain uncertainty, and follow the required headings."
    )
    if text:
        prompt += "\n\nUser-provided text or URL:\n" + text[:12000]
    content.append({"type": "input_text", "text": prompt})

    if uploaded:
        mime = uploaded.mimetype or ""
        if mime not in ("image/png", "image/jpeg", "image/webp"):
            return jsonify({"error": "Please upload a PNG, JPG, or WEBP screenshot."}), 400
        raw = uploaded.read()
        if len(raw) > 4 * 1024 * 1024:
            return jsonify({"error": "Image must be smaller than 4 MB."}), 400
        encoded = base64.b64encode(raw).decode("ascii")
        content.append({
            "type": "input_image",
            "image_url": f"data:{mime};base64,{encoded}",
            "detail": "high"
        })

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_INSTRUCTIONS,
            input=[{"role": "user", "content": content}],
            max_output_tokens=900
        )
        return jsonify({"analysis": response.output_text, "model": MODEL})
    except Exception as exc:
        # Avoid exposing credentials or stack traces to the browser.
        app.logger.exception("AI analysis request failed")
        return jsonify({"error": "The AI analysis service could not complete the request. Check the server configuration and try again."}), 502

@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "Upload is too large. Maximum request size is 5 MB."}), 413

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
