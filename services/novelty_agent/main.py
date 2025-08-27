import asyncio
import nats
import json
import os
from openai import AsyncOpenAI

# --- Constants ---
NATS_URL = "nats://localhost:4222"
NOVEL_EVENT_SUBJECT = "event.type.novel"
HYPOTHESIS_SUBJECT = "hypotheses.new"
LLM_MODEL = "gpt-3.5-turbo"

# --- OpenAI Client ---
try:
    client = AsyncOpenAI()
except Exception as e:
    print(f"[ERROR] Failed to initialize OpenAI client: {e}. Is OPENAI_API_KEY set?")
    client = None

# --- LLM Interaction ---
async def generate_hypothesis(event_content: str) -> str:
    """Generates a hypothesis about the significance of a novel event using an LLM."""
    if not client:
        return "Hypothesis generation skipped: OpenAI client not initialized."

    prompt = f"""
    An incoming piece of information has been classified as 'novel' and potentially significant.
    Based on the content: '{event_content}', generate a brief one-sentence hypothesis about its
    potential implication or connection to other concepts. Be concise.
    """
    try:
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "system", "content": "You are a concise insight generator."},
                      {"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=100)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        return "Hypothesis generation failed due to an error."

# --- NATS Message Handling ---
def create_message_handler(nc):
    """
    Creates a closure for the message handler to give it access to the NATS client connection.
    """
    async def message_handler(msg):
        subject = msg.subject
        data = msg.data.decode()
        print(f"--- [Novelty Agent] Received new perception on '{subject}' ---")

        try:
            event_data = json.loads(data)
            source_event_id = event_data.get("id")
            text_content = event_data.get("metadata", {}).get("text", "")

            if not all([source_event_id, text_content]):
                print("[WARNING] Event missing 'id' or 'text' metadata. Skipping.")
                return

            # 1. Generate hypothesis
            print(f"\nGenerating hypothesis for event {source_event_id}...")
            hypothesis = await generate_hypothesis(text_content)
            print(f"Generated Hypothesis: {hypothesis}")

            # 2. Publish the new hypothesis
            if "failed" not in hypothesis and "skipped" not in hypothesis:
                hypothesis_payload = {
                    "source_event_id": source_event_id,
                    "hypothesis_text": hypothesis,
                }
                await nc.publish(HYPOTHESIS_SUBJECT, json.dumps(hypothesis_payload).encode())
                print(f"Published hypothesis to '{HYPOTHESIS_SUBJECT}'")

        except json.JSONDecodeError:
            print(f"[ERROR] Failed to decode JSON: {data}")

        print("----------------------------------------------------------")
    return message_handler

# --- Service Main Loop ---
async def main():
    """Main function for the Novelty Agent."""
    print("Novelty Agent service starting...")
    if not client:
        print("[CRITICAL] OpenAI client not available. Service will run without hypothesis generation.")

    try:
        nc = await nats.connect(NATS_URL)
        print(f"Connected to NATS at {NATS_URL}")
    except Exception as e:
        print(f"[ERROR] Failed to connect to NATS: {e}")
        return

    # Use a closure to pass the NATS connection to the handler
    handler = create_message_handler(nc)
    await nc.subscribe(NOVEL_EVENT_SUBJECT, cb=handler)
    print(f"Subscribed to '{NOVEL_EVENT_SUBJECT}'")

    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        print("Service shutting down...")
        await nc.close()
        print("NATS connection closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nNovelty Agent service stopped by user.")
