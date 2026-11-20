
import os

from google import genai
from google.genai import types


EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768


def create_client():
    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.getenv(
        "GOOGLE_CLOUD_LOCATION",
        "us-central1",
    )

    return genai.Client(
        vertexai=True,
        project=project_id,
        location=location,
    )


def generate_embedding(text, task_type="RETRIEVAL_DOCUMENT"):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must not be empty")

    client = create_client()

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )

    return response.embeddings[0].values


def main():
    sample_text = (
        "A peaceful devotional Hindi bhajan "
        "about Lord Krishna, suitable for morning."
    )

    print("\n========== EMBEDDING TEST ==========")
    print("Model:", EMBEDDING_MODEL)
    print("Input:", sample_text)

    vector = generate_embedding(sample_text)

    print("Embedding dimensions:", len(vector))
    print("First 10 vector values:", vector[:10])
    print("Embedding generated successfully!")


if __name__ == "__main__":
    main()

