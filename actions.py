import subprocess


def execute(action: str, target: str = None, payload: str = None):
    """Route action type to the correct handler."""
    if not action or action == "none":
        return

    print(f"[ACTION] {action} | target={target} | payload={payload}")

    handlers = {
        "open_app":      lambda: open_app(target),
        "browse_url":    lambda: browse_url(target),
        "google_search": lambda: google_search(payload),
        "send_whatsapp": lambda: send_whatsapp(target, payload),
        "type_text":     lambda: type_text(payload),
        "system_command":lambda: system_command(payload),
    }

    handler = handlers.get(action)
    if handler:
        try:
            handler()
        except Exception as e:
            print(f"[ACTION] Failed: {e}")
    else:
        print(f"[ACTION] Unknown action: {action}")


# ── Individual action handlers ─────────────────────────────────────────────

def open_app(app: str):
    """Open an application by command name."""
    subprocess.Popen([app],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    print(f"[ACTION] Opened: {app}")


def browse_url(url: str):
    """Open a URL in the default browser."""
    if not url.startswith("http"):
        url = "https://" + url
    subprocess.Popen(["xdg-open", url],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    print(f"[ACTION] Browsing: {url}")


def google_search(query: str):
    """Search Google in browser."""
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    browse_url(url)


def send_whatsapp(contact: str, message: str):
    """Open WhatsApp Web with pre-filled message (wa_bridge.js needed for auto-send)."""
    import urllib.parse
    msg_encoded = urllib.parse.quote(message or "")
    # If contact is a phone number
    if contact and (contact.startswith("+") or contact.isdigit()):
        url = f"https://wa.me/{contact}?text={msg_encoded}"
    else:
        # Open WhatsApp Web and let user select contact
        url = f"https://web.whatsapp.com"
        print(f"[ACTION] WhatsApp bridge not set up yet — opening WhatsApp Web")
    browse_url(url)


def type_text(text: str):
    """Type text at current cursor position."""
    import time
    time.sleep(0.5)
    try:
        import pyautogui
        pyautogui.typewrite(text, interval=0.05)
    except ImportError:
        # fallback using xdotool
        subprocess.run(["xdotool", "type", "--clearmodifiers", text])


def system_command(cmd: str):
    """Run a shell command."""
    result = subprocess.run(cmd, shell=True,
                            capture_output=True, text=True)
    print(f"[ACTION] Command output: {result.stdout}")
    return result.stdout
