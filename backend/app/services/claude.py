import anthropic

from app.core.config import settings

_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

RECEIPT_PARSE_PROMPT = """
You are parsing a receipt photo. Extract all line items and return a JSON object with this exact structure:
{
  "items": [
    {"name": "...", "price": <number in kopecks/cents>, "quantity": <number>},
    ...
  ],
  "total": <number>,
  "currency": "RUB"
}
Return ONLY valid JSON, no explanation.
"""


async def parse_receipt(photo_url: str) -> dict:
    """Send receipt photo to Claude API and return parsed items."""
    message = await _client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "url", "url": photo_url}},
                    {"type": "text", "text": RECEIPT_PARSE_PROMPT},
                ],
            }
        ],
    )
    import json

    raw = message.content[0].text  # type: ignore[union-attr]
    return json.loads(raw)
