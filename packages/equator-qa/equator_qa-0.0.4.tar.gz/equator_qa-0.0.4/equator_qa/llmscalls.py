import os
import json
from loguru import logger
import requests
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def call_groq_evaluator_api(evaluator_model, student_answer, evaluator_system_prompt):
    api_key = os.environ.get("GROQ_API_KEY")
    gorq_api = Groq(api_key=api_key)
    completion_eval = gorq_api.chat.completions.create(
        temperature=0,
        model=evaluator_model,
        messages=evaluator_system_prompt,
    )
    response_eval = completion_eval.choices[0].message.content

    if response_eval:
        logger.info(f"call_groq_evaluator_api: {response_eval}")

        return student_answer, response_eval
    else:
        logger.error("Failed to get evaluator response.")
        return None


def call_ollama_evaluator_api(evaluator_model, student_answer, evaluator_system_prompt):
    url = "http://localhost:11434/api/chat"
    payload = {"model": evaluator_model, "messages": evaluator_system_prompt}

    # Make a single POST request (remove the duplicate)
    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        stream=True,
    )

    complete_message = ""

    # Read the streamed response line by line
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode("utf-8"))
            # Safely retrieve content if present
            if "message" in chunk and "content" in chunk["message"]:
                complete_message += chunk["message"]["content"]

            # If the API signals completion
            if chunk.get("done"):
                break

    print("Complete message:", complete_message)

    # Return the result (simply return the text)
    return student_answer, complete_message


def call_openrouter_student_api(full_prompt_student, warning_prompt, model_path):
    api_key = os.environ.get("OPENROUTER_KEY")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    model_path = str(model_path)

    # Make the API call
    completion = client.chat.completions.create(
        model=model_path,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a student who is being tested, please follow the directions given exactly. "
                    "You are welcomed to reason through the question. "
                    "You must return only your final answer in a JSON Object example  {'student_answer':'<My final Answer here>'}"
                ),
            },
            {
                "role": "user",
                "content": warning_prompt + full_prompt_student,
            },
        ],
    )
    # last_api_call_time = time.time()  # Update the time of the last API call
    response = completion.choices[0].message.content
    return response


def call_ollama_student_api(full_prompt_student, warning_prompt, student_model):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": student_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a student who is being tested, please follow the directions given exactly. You are welcomed to reason through the question "
                + "You must return only your final answer in a JSON Object example {'student_answer':'<My final Answer here>'}",
            },
            {"role": "user", "content": warning_prompt + full_prompt_student},
        ],
    }

    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        stream=True,
    )
    complete_message = ""
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode("utf-8"))
            complete_message += chunk["message"]["content"]
            if chunk.get("done"):
                break
    print("line 119, LLMSCALLS ollama student = ", complete_message)
    if complete_message is not None:
        # return {"student_answer": complete_message}
        return complete_message

def call_groq_student_api(full_prompt_student, warning_prompt, groq_student_model):
    api_key = os.environ.get("GROQ_API_KEY")
    gorq_api = Groq(api_key=api_key)
    completion_eval = gorq_api.chat.completions.create(
        temperature=0,
        model=groq_student_model,
        messages=[
            {
                "role": "system",
                "content": "You are a student who is being tested, please follow the directions given exactly. You are welcomed to reason through the question "
                + "You must return only your final answer in a JSON Object example {'student_answer':'<My final Answer here>'}",
            },
            {"role": "user", "content": warning_prompt + full_prompt_student},
        ],
    )
    response = completion_eval.choices[0].message.content

    if response:
        logger.info(f"call_groq_student_api: {response}")

        return response
    else:
        logger.error("Failed to get evaluator response.")
        return None
