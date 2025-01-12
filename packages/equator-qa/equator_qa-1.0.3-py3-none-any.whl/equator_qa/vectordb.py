from loguru import logger
import json
import chromadb
import requests


class VectorDB_Controller(object):
    def __init__(self, keepVectorDB):
        self.base_url = "http://localhost:11434"  # in container
        self.chroma_client = chromadb.PersistentClient(path=".")
        self.keepVectorDB = keepVectorDB
        if not keepVectorDB:
            # open file for vector score
            # Open and load the JSON file
            with open("data/linguistic_benchmark.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            # Initialize a list to store the parsed conversations
            conversations = []

            # Iterate over the list of dictionaries
            for entry in data:
                parsed_entry = {
                    "id": entry.get(
                        "index", ""
                    ),  # Use "index" as the unique identifier
                    "category": entry.get("category", ""),  # Extract category
                    "question": entry.get("question", ""),  # Extract the question
                    "response": entry.get(
                        "human_answer", ""
                    ),  # Extract the human answer
                }
                conversations.append(parsed_entry)
            logger.info(conversations)
            self.create_vector_db(conversations)

    def generate_embeddings(self, model, input_text, truncate=True):
        url = f"{self.base_url}/api/embed"
        payload = {"model": model, "input": input_text, "truncate": truncate}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raise an error for bad responses
            if response.headers.get("Content-Type").startswith("application/json"):
                response_json = response.json()
                if "embeddings" in response_json:
                    return response_json
                else:
                    logger.error(f"No embeddings found in response: {response_json}")
                    return None
            else:
                logger.error(
                    f"Unexpected response content type: {response.headers.get('Content-Type')}"
                )
                logger.error(f"Response content: {response.text}")
                return None
        except requests.RequestException as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return None

    def retrieve_embedding(self, prompt, n_results=1):
        # print("line 411 retrieve embedding prompt  ==", prompt)
        response = self.generate_embeddings(model="all-minilm", input_text=prompt)
        # print("line 413 Generate Embeddings ==", response)
        if not response or "embeddings" not in response:
            logger.error("Failed to retrieve embeddings from the model.")
            return None
        prompt_embedding = self.flatten_embedding(response["embeddings"])
        vector_db = self.chroma_client.get_collection(name="conversations")
        try:
            results = vector_db.query(
                query_embeddings=[prompt_embedding], n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Error querying vector DB: {e}")
            return None

    def add_to_vector_db(self, vector_db, entry_id, serialized_conversations, metadata):
        response = self.generate_embeddings(
            model="all-minilm", input_text=serialized_conversations
        )

        if not response or "embeddings" not in response:
            logger.error(
                f"Failed to retrieve embeddings for entry {entry_id}. Response: {response}"
            )
            return
        # Flatten the embedding if it is nested
        embedding = self.flatten_embedding(response["embeddings"])

        converted_metadata = {
            k: self.convert_metadata_value(v) for k, v in metadata.items()
        }

        try:
            vector_db.add(
                ids=[str(entry_id)],
                embeddings=[embedding],
                documents=[serialized_conversations],
                metadatas=[converted_metadata],
            )
        except Exception as e:
            logger.error(f"Error adding entry {entry_id} to the vector DB: {e}")

    def create_vector_db(self, conversations):
        vector_db_name = "conversations"
        try:
            self.chroma_client.delete_collection(name=vector_db_name)
        except ValueError:
            pass  # Handle collection not existing
        vector_db = self.chroma_client.create_collection(name=vector_db_name)
        for c in conversations:
            serialized_conversations = json.dumps(c)
            self.add_to_vector_db(vector_db, c["id"], serialized_conversations, c)

    def convert_metadata_value(self, value):
        if value is None:
            return ""
        if isinstance(value, (list, dict)):
            return json.dumps(value)
        return value

    def flatten_embedding(self, embedding):
        # Flatten nested embeddings if necessary
        if isinstance(embedding[0], list):
            return [item for sublist in embedding for item in sublist]
        return embedding

    def add_to_vector_db(self, vector_db, entry_id, serialized_conversations, metadata):
        response = self.generate_embeddings(
            model="all-minilm", input_text=serialized_conversations
        )
        if not response or "embeddings" not in response:
            logger.error(
                f"Failed to retrieve embeddings for entry {entry_id}. Response: {response}"
            )
            return
        # Flatten the embedding if it is nested
        embedding = self.flatten_embedding(response["embeddings"])

        converted_metadata = {
            k: self.convert_metadata_value(v) for k, v in metadata.items()
        }

        try:
            vector_db.add(
                ids=[str(entry_id)],
                embeddings=[embedding],
                documents=[serialized_conversations],
                metadatas=[converted_metadata],
            )
        except Exception as e:
            logger.error(f"Error adding entry {entry_id} to the vector DB: {e}")
