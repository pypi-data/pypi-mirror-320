import requests
import json
import os
from pprint import pprint
from typing import Annotated, List, Literal
import uuid

api_key = os.environ["ELEVEN_LABS_API_KEY"]
voices = {"adam": "pNInz6obpgDQGcFmaJgB", "rachel": "21m00Tcm4TlvDq8ikWAM"}


def e_l_text_to_speech(
    text_to_speak="this is the text that will be passed for TTS",
    voice_name="adam",
    model_id="eleven_monolingual_v1",
    out_directory_path: Annotated[str, "the output directory name"] = "out/ElevenLabs",
    filename: Annotated[str, "the local name for the file wihtout extension"] = str(
        uuid.uuid4()
    ),
):
    voice_id = voices[voice_name]
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?optimize_streaming_latency=0"
    headers = {
        "accept": "audio/mpeg",
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    data = {
        "text": text_to_speak,
        "model_id": model_id,
        "voice_settings": {"stability": 0, "similarity_boost": 0},
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    audio_data = response.content

    os.makedirs(out_directory_path, exist_ok=True)
    final_output_video_filepath = os.path.join(out_directory_path, f"{filename}.wav")
    with open(final_output_video_filepath, "wb") as file:
        file.write(audio_data)
    return os.path.abspath(final_output_video_filepath)


def list_voices():
    url = "https://api.elevenlabs.io/v1/voices"
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the response JSON
        response_json = response.json()
        voices = response_json["voices"]
        ret = []
        for voice in voices:
            labels = voice["labels"]
            ret.append(
                {
                    "voice_id": voice["voice_id"],
                    "name": voice["name"],
                    "accent": labels["accent"],
                    "age": labels["age"],
                    "gender": labels["gender"],
                    "description": (
                        labels["description"] if "description" in labels else ""
                    ),
                    "use case": labels["use case"] if "use case" in labels else "",
                }
            )

        pprint(ret)
        return ret
        # Access specific keys in the response

    else:
        print("Error:", response.status_code)
        print("Response:", response.text)

    return response
