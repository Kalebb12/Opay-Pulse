import httpx
import os
import time
from faster_whisper import WhisperModel

# Load model once at startup — not on every request
# Use "tiny" for speed, "base" for better accuracy
# tiny = ~75MB RAM, base = ~145MB RAM
model = WhisperModel("tiny", device="cpu", compute_type="int8")

async def transcribe_voice_note(media_url: str) -> str | None:
    temp_path = None

    try:
        temp_path = await download_audio(media_url)

        # Transcribe locally — no API call
        segments, info = model.transcribe(
            temp_path,
            language="en",  # Force English/Pidgin
            beam_size=5
        )

        transcribed = " ".join([seg.text for seg in segments]).strip()

        print(f"🎤 Transcribed: {transcribed}")
        return transcribed if transcribed else None

    except Exception as e:
        print(f"Transcription error: {str(e)}")
        return None

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


async def download_audio(media_url: str) -> str:
    temp_path = f"/tmp/voice_{int(time.time())}.ogg"

    # Follow redirects and handle Twilio 3xx redirect responses which point
    # to the signed CDN URL. httpx won't forward auth to other hosts, so
    # allow redirects and fallback to explicitly fetching the Location.
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            media_url,
            auth=(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            ),
            timeout=30.0
        )

        # Some Twilio media endpoints return a 3xx redirect to a signed
        # CDN URL. Follow the Location explicitly if the initial response
        # is still a redirect, because auth should not be forwarded to a
        # different host.
        if response.is_redirect and response.headers.get("location"):
            response = await client.get(
                response.headers["location"],
                timeout=30.0,
                follow_redirects=True
            )

        response.raise_for_status()

        with open(temp_path, "wb") as f:
            f.write(response.content)

    return temp_path