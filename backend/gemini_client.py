import os
from google import genai
from google.genai import types


def main():
    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]

    client = genai.Client(
        vertexai=True,
        project=project_id,
        location="global",
        http_options=types.HttpOptions(
            api_version="v1"
        )
    )

    prompt = (
        "Suggest three classic Hindi devotional songs "
        "suitable for morning listening. "
        "Provide only the song titles."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=300
        )
    )

    print("Gemini response:")
    print(response.text)


if __name__ == "__main__":
    main()
