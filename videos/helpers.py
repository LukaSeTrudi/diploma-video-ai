from openai import OpenAI
client = OpenAI(api_key="") # Add your OpenAI API key here
import json
import os
from pydub import AudioSegment
import whisper
import ffmpeg
chatgptmodel = "gpt-4o-mini"
temperature = 0.7
def question_ai(transcription, prompt):
    completion = client.chat.completions.create(
        model=chatgptmodel,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": f"{transcription}"
            }
        ]
    )
    return completion.choices[0].message.content

def abstract_summary_extraction(transcription):
    message = "You are a highly skilled AI trained in language comprehension and summarization. I would like you to read the following transcription and summarize it into a concise abstract paragraph. Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text. Please avoid unnecessary details or tangential points. Ensure all extracted points are in the same language as the input text."
    return question_ai(transcription, message)

def key_points_extraction(transcription):
    message = "You are a proficient AI with a specialty in distilling information into key points. Based on the following segmented text with timestamps, identify and list only the most crucial main points that encapsulate the essence of the discussion, along with their corresponding timestamps. These should be the most important ideas, findings, or topics that are crucial to understanding the discussion. Your goal is to provide a JSON object that someone could read to quickly understand what was discussed and when each key point was mentioned. Ensure that the timestamps are accurately reflected from the input and that all content is in the same language as the input text."
    return question_ai(transcription, message)

def extract_questions(transcription):
    message = "You are an AI expert in language comprehension and question generation. Please read the following text and generate a list of questions along with their corresponding answers based on the content. These questions and answers should cover a range of topics and aspects discussed in the text, aiming to probe deeper into the subject matter and encourage further exploration and understanding. Your output should be a JSON object with two keys: 'questions' for the list of questions and 'answers' for the corresponding answers. Each question should have a relevant and thought-provoking answer. Ensure all content is in the same language as the input text."
    return question_ai(transcription, message)

def fix_slo_transcribe(transcription):
    message = "You are an expert in language processing. Please correct the transcription below, fixing any grammar, punctuation, and spelling errors while preserving the original meaning. Respond in the same language as the transcription."
    return question_ai(transcription, message)

def ask_ai(messages, image):
    formatted_messages = []
    for message in messages:
        formatted_messages.append({
            "role": message["role"],
            "content": message["content"]
        })
    
    formatted_messages[-1]["content"].append(
        {"type": "image_url", "image_url": {
            "url": image,
            "detail": "low",
            }
        })
    completion = client.chat.completions.create(
        model=chatgptmodel,
        messages=formatted_messages,
        temperature=temperature,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "response_ai",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Response to the question",
                            },
                            "timestamp": {
                                "type": "integer",
                                "description": "The timestamp of the video if relevant. Infer this from transcription. Use seconds."
                            }
                        },
                        "required": ["text"],
                    }
                }
            }
        ],
        tool_choice="required"
    )

    output = json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
    print(output)

    return {
        "role": 'assistant',
        "content": [{'type': 'text', **output }]
    }


def convert_video_to_mp3(input_file):
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    output_file = f"{base_name}.mp3"
    try:
        # Uporabimo knjižnico ffmpeg
        ffmpeg.input(input_file).output(output_file, format='mp3', ab='192k',
                    acodec='libmp3lame', ar='44100', ac=2).run(capture_stdout=True, capture_stderr=True)
            
        print(f"Konverzija končana: {output_file}")
        return output_file
    except Exception as e:
        print(f"Napaka: {str(e)}")

def transcribe_audio(input_file):
    try:
        model = whisper.load_model("base")

        result = model.transcribe(input_file)

        return result
    except Exception as e:
        print(f"Napaka: {str(e)}")


def minimize_json(input, decimals=1):
    # Ohranimo samo besedilo segmenta in zaokrožimo čase
    minimized_data = {
        "segments": [
            {
                "start": round(segment["start"], decimals),
                "end": round(segment["end"], decimals),
                "text": segment["text"]
            } for segment in input["segments"]
        ]
    }
    return minimized_data

def generate_transcription(video_path):
    audio_path = convert_video_to_mp3(video_path)
    transcription = transcribe_audio(audio_path)
    optimized_transcription = minimize_json(transcription)
    return optimized_transcription

def transcribe_audio_api(audio_file):
    audio = AudioSegment.from_mp3(audio_file)
    segments = split_audio(audio, 20 * 60 * 1000)
    all_transcripts = []
    current_time_offset = 0.0

    for i, segment in enumerate(segments):
        segment_file = f"segment_{i}.mp3"
        segment.export(segment_file, format="mp3")
    
        seg_file = open(segment_file, "rb")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=seg_file,
            response_format="verbose_json",
            timestamp_granularities=["segment"]
        )
        
        for segment in transcript.segments:
            segment["start"] += current_time_offset
            segment["end"] += current_time_offset
        
        all_transcripts.extend(transcript.segments)
        
        current_time_offset += len(segment) / 1000.0

    minimized_data = { 
        "segments": [
            {
                "start": round(segment["start"], 1),
                "end": round(segment["end"], 1),
                "text": segment["text"]
            } for segment in all_transcripts
            ]
    }
    return minimized_data