# https://docs.mistral.ai/guides/rag/

from mistralai import Mistral
import mistralai
import requests
import numpy as np
import faiss
import os
import pickle
from pathlib import Path
from app.utils import load_json
import time


api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)


def _get_chunk_embedding(input: str) -> list[float]:
    """
    Generates an embedding for the given input using the 'mistral-embed' model.
    This function attempts to create an embedding for the provided input by calling the embeddings API.
    If an SDKError occurs during the API call, it will print the error, wait for 10 seconds, and retry until successful.
    Args:
        input: The input data to be embedded. This should be in a format accepted by the embeddings API.
    Returns:
        list: The embedding vector corresponding to the input.
    Raises:
        This function does not raise exceptions directly; it retries on SDKError until successful.
    """

    while True:
        try:
            embeddings_batch_response = client.embeddings.create(
                model="mistral-embed", inputs=input
            )
            return embeddings_batch_response.data[0].embedding
        except mistralai.models.sdkerror.SDKError as e:
            print(e)
            print("Retrying...")
            time.sleep(10)


def embed_text(
    texts: list[str], chunk_size: int
) -> tuple[faiss.Index, np.ndarray, list[str]]:
    """
    Splits input texts into chunks, computes embeddings for each chunk, and indexes them using FAISS.
    Args:
        texts (list[str]): A list of input text strings to be embedded.
        chunk_size (int): The maximum size of each text chunk. If None or greater than 8192, defaults to 8192.
    Returns:
        tuple[faiss.Index, np.ndarray, list[str]]:
            - faiss.Index: The FAISS index containing the embeddings.
            - np.ndarray: Array of computed embeddings for each chunk.
            - list[str]: List of text chunks corresponding to the embeddings.
    Notes:
        - Each text in `texts` is split into chunks of size `chunk_size`.
        - Embeddings are computed for each chunk using the `_get_chunk_embedding` function.
        - The resulting embeddings are indexed using FAISS for efficient similarity search.
    """

    if chunk_size is None or chunk_size > 8192:
        chunk_size = 8192

    chunks = [
        text[i : i + chunk_size]
        for text in texts
        for i in range(0, len(text), chunk_size)
    ]

    print(len(chunks), "chunks created")

    start_embeddings = time.time()

    text_embeddings = []
    for idx, chunk in enumerate(chunks):
        print(f"Processing {idx}/{len(chunks)}")
        text_embeddings.append(_get_chunk_embedding(chunk))

    text_embeddings = np.array(text_embeddings)
    embeddings_duration = time.time() - start_embeddings
    print(
        f"Durée du calcul des embeddings des chunks: {embeddings_duration:.2f} secondes"
    )
    d = text_embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(text_embeddings)

    return index, text_embeddings, chunks


def save_index(index, text_embeddings, chunks, filename="faiss_index.pkl"):
    """
    Saves the FAISS index, embeddings, and chunks to a file.

    Args:
        index: The FAISS index
        text_embeddings: The text embeddings
        chunks: The original text chunks
        filename: The name of the save file
    """
    # Créer le dossier data s'il n'existe pas
    folder = Path(__file__).parent / Path("data")
    folder.mkdir(exist_ok=True)

    # Chemin complet du fichier
    filepath = folder / filename

    # Sauvegarder l'index FAISS
    faiss.write_index(index, str(filepath.with_suffix(".faiss")))

    # Sauvegarder les embeddings et les chunks
    with open(filepath, "wb") as f:
        pickle.dump({"text_embeddings": text_embeddings, "chunks": chunks}, f)

    print(f"Index sauvegardé dans {filepath}")


def load_index(filename="faiss_index.pkl"):
    """
    Loads the FAISS index, embeddings, and chunks from a file.

    Args:
        filename: The name of the save file

    Returns:
        tuple: (index, text_embeddings, chunks)
    """
    filepath = Path(__file__).parent / Path("data") / filename

    # Vérifier si les fichiers existent
    if not filepath.exists() or not filepath.with_suffix(".faiss").exists():
        raise FileNotFoundError(f"Fichiers de sauvegarde non trouvés: {filepath}")

    # Charger l'index FAISS
    index = faiss.read_index(str(filepath.with_suffix(".faiss")))

    # Charger les embeddings et les chunks
    with open(filepath, "rb") as f:
        data = pickle.load(f)
        text_embeddings = data["text_embeddings"]
        chunks = data["chunks"]

    print(f"Index chargé depuis {filepath}")
    return index, text_embeddings, chunks


texts = load_json("docs_all_site_contents")


def get_chunks_from_question(
    index, chunks, question: str, num_chunks: int
) -> list[str]:
    """
    Retrieves the most relevant text chunks for a given question using a vector index.
    Args:
        index: A FAISS index or similar object for nearest neighbor search.
        chunks: List of text chunks (not directly used in function).
        question (str): The input question to embed and search for.
        num_chunks (int): Number of top relevant chunks to retrieve.
    Returns:
        list[str]: List of retrieved chunk contents most relevant to the question.
    """

    # Mesure du temps pour l'embedding de la question
    question_embeddings = np.array([_get_chunk_embedding(question)])
    D, I = index.search(question_embeddings, k=num_chunks)  # distance, index
    retrieved_chunks = [texts[i]["content"] for i in I.tolist()[0]]
    print("here")
    print(retrieved_chunks)

    return retrieved_chunks


if __name__ == "__main__":
    titles = [text["title"] for text in texts]
    save_index(*embed_text(titles, chunk_size=None))
