FINANCE FORWARD - AI-POWERED WEBSITE PROTOTYPE

WHAT THIS IS
A runnable Flask website with a real AI analysis backend using the OpenAI Responses API.
It accepts pasted messages/URLs and PNG/JPG/WEBP screenshots. The model analyzes text and image
content and returns risk level, an estimated score, warning signs, and safe next steps.

IMPORTANT
- This is a prototype, not a bank-grade fraud detection product.
- It does not query live URL reputation databases or bank transaction systems.
- AI can be wrong. "Low risk" does not mean safe.
- Never ask users for passwords, card numbers, PINs, or OTPs.
- The API key must stay on the server, never in frontend JavaScript.
- API usage may incur charges according to your provider account and model pricing.

RUN LOCALLY
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Create a virtual environment (recommended):
   python -m venv .venv
   Windows: .venv\\Scripts\\activate
   macOS/Linux: source .venv/bin/activate
4. Install packages:
   pip install -r requirements.txt
5. Copy .env.example to .env and add your secret API key.
6. Load the environment variables before starting the app.
   macOS/Linux:
     export OPENAI_API_KEY="your_key"
     export OPENAI_MODEL="gpt-5.5"
   Windows PowerShell:
     $env:OPENAI_API_KEY="your_key"
     $env:OPENAI_MODEL="gpt-5.5"
7. Start:
   python app.py
8. Open http://127.0.0.1:5000

DEPLOYMENT
Deploy the folder to a Python hosting service (for example, Render, Railway, or a university server).
Set OPENAI_API_KEY and optionally OPENAI_MODEL as server-side environment variables.
Use HTTPS, add rate limiting, logging controls, privacy/retention policy, and abuse protection
before allowing public users.

API DESIGN
- POST /api/analyze (multipart form: text and/or image)
- GET /health

The backend uses the OpenAI Responses API. Image input is sent as a base64 data URL.
See official documentation:
https://developers.openai.com/api/docs/quickstart
https://developers.openai.com/api/reference/resources/responses/methods/create
