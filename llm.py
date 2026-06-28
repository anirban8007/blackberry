import google.generativeai as genai
import json, re, config

SYSTEM_PROMPT = """
You are Blackberry, a highly personal AI assistant.
You are always concise, friendly, and smart.
You live on the user's laptop and phone.

When the user gives a command that requires an action, respond ONLY in this JSON format:
{
  "speech": "what you will say out loud",
  "action": "action_type or null",
  "target": "app name / URL / contact name or null",
  "payload": "message text / search query / null"
}

Available action types:
- open_app       → open an application (target = app command e.g. "firefox", "spotify")
- browse_url     → open a URL in browser (target = full URL)
- google_search  → search Google (payload = search query)
- send_whatsapp  → send WhatsApp message (target = name/number, payload = message)
- type_text      → type something on screen (payload = text to type)
- system_command → run a shell command (payload = command)
- none           → just talk, no action needed

If no action is needed (just a conversation), use action: null.

Memory from past conversations:
{memory_context}
"""

_model = None

def _get_model():
    global _model
    if _model is None:
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set. Add it to ~/.blackberry/.env")
        genai.configure(api_key=config.GEMINI_API_KEY)
        _model = genai.GenerativeModel(config.GEMINI_MODEL)
        print("[LLM] Gemini ready.")
    return _model


def ask(user_text: str, memory_context: str = "No memory yet.") -> dict:
    """Send user command to Gemini, return parsed response dict."""
    prompt = SYSTEM_PROMPT.format(memory_context=memory_context)
    model  = _get_model()

    try:
        response = model.generate_content(
            [{"role": "user", "parts": [prompt + "\n\nUser: " + user_text]}]
        )
        raw = response.text.strip()
        print(f"[LLM] Raw response: {raw}")

        # Try to extract JSON from response
        match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())

        # If no JSON found, treat entire response as speech only
        return {
            "speech": raw,
            "action": None,
            "target": None,
            "payload": None
        }

    except Exception as e:
        print(f"[LLM] Error: {e}")
        return {
            "speech": "Sorry, I had trouble thinking. Please try again.",
            "action": None,
            "target": None,
            "payload": None
        }
