import json
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline

import pickle
import os.path
from tqdm import tqdm
import random as rd
import gdown
from io import BytesIO

from config import CLEAN_DATA_JSON_ID, SUMMERIZER_ID, MATRIX_ID


# Load your Reddit dataset
def load_dataset(clean_data_json_id):
    file_url = f"https://drive.google.com/uc?id={clean_data_json_id}"
    memory_file = BytesIO()
    gdown.download(file_url, output=memory_file, quiet=True)
    memory_file.seek(0)
    return json.load(memory_file)


# Step 1: Build the retrieval corpus
def prepare_corpus(data):

    doc_id_comments = {}
    corpus = []
    doc_set = set()
    doc_ids = dict()
    for post in data:
        content = post['post_content']
        if content not in doc_set:
            doc_ids[content] = len(doc_set)
            doc_set.add(content)
            corpus.append(content)

        doc_id_comments[doc_ids[content]] = [
            {
                'comment_content': comment['comment_content'],
                'comment_score': comment['comment_score']
            } for comment in post['comments_list']
        ]

    return corpus, doc_ids, doc_id_comments

# Step 2: Create and store embeddings
def build_post_matrix(corpus, matrix_id, model_name='all-MiniLM-L6-v2', matrix_file_path='model/matrix_corpus.pickle'):

    embedder = SentenceTransformer(model_name)

    # # this is the old version to get the embedded corpus matrix
    # if not os.path.isfile(matrix_file_path):
    #     matrix = np.array([embedder.encode(doc, convert_to_tensor=False) for doc in tqdm(corpus)])
    #     with open(matrix_file_path, 'wb') as file:
    #         # Serialize and write the variable to the file
    #         pickle.dump(matrix, file)
    #         file.close()
    # else:
    #     with open(matrix_file_path, 'rb') as file:
    #         # Deserialize and retrieve the variable from the file
    #         matrix = pickle.load(file)
    #         file.close()

    file_url = f"https://drive.google.com/uc?id={matrix_id}"
    memory_file = BytesIO()
    gdown.download(file_url, output=memory_file, quiet=True)
    memory_file.seek(0)

    matrix = pickle.load(memory_file)

    return embedder, matrix

# Step 3: Generative model setup
def load_generative_model(paraphaser_id, model_name='google-t5/t5-small', file_path='model/summarizer_pipeline.pickle'):

    # # below is the old version, I modfify to load it from google drive so the app is lighter
    # if not os.path.isfile(file_path):
    #     generator = pipeline("summarization", model=model_name)
    #     with open(file_path, 'wb') as file:
    #         # Serialize and write the variable to the file
    #         pickle.dump(generator, file)
    #
    # else:
    #     with open(file_path, 'rb') as file:
    #         # Deserialize and retrieve the variable from the file
    #         generator = pickle.load(file)
    # return generator

    file_url = f"https://drive.google.com/uc?id={paraphaser_id}"
    memory_file = BytesIO()
    gdown.download(file_url, output=memory_file, quiet=True)
    memory_file.seek(0)

    generator = pickle.load(memory_file)

    return generator


# Step 4: Find response from data
def find_response_message(query, corpus_matrix, comment_indexer, embedder):
    embedded_vector = embedder.encode(query, convert_to_tensor=False).reshape(1,-1)

    similarity_score = ((corpus_matrix - embedded_vector) ** 2).sum(axis = 1)

    min_score = similarity_score.min()

    doc_ids_list = [i for i, score in enumerate(similarity_score) if score == min_score]
    comments = []

    for doc_id in doc_ids_list:
        comments += comment_indexer[doc_id]

    if len(comments) == 0:
        order_similarity_score = sorted(list(similarity_score))
        k = 1
        min_score = order_similarity_score[k]
        while (len(comments) == 0) and k < 10:
            doc_ids_list = [i for i, score in enumerate(similarity_score) if score == min_score]
            for doc_id in doc_ids_list:
                comments += comment_indexer[doc_id]
            k += len(doc_ids_list)
            min_score = order_similarity_score[k]


    total_score = sum(cmt['comment_score'] for cmt in comments)
    if total_score == 0:
        return rd.choice(comments)['comment_content']
    alpha = 0.15
    weights_ = []
    no_vote_count = 0
    for cmt in comments:
        if cmt["comment_score"] != 0:
            weights_.append(cmt["comment_score"] * (1 - alpha))
        else:
            weights_.append(0)
            no_vote_count += 1
    if no_vote_count == 0:
        return rd.choices(comments, weights=weights_)[0]['comment_content']
    for i in range(len(comments)):
        if weights_[i] == 0:
            weights_[i] == total_score * alpha / no_vote_count

    return rd.choices(comments, weights=weights_)[0]['comment_content']

# Step 5: refining response
def paraphrase_message(message, generator):

    # Generate a refined response
    paragraph_list = message.split("\n")
    returned_message = ""
    for paragraph in paragraph_list:
        if len(paragraph) < 20:
            continue
        sentence_list = paragraph.split('.')
        curr_len = len(sentence_list[0])
        curr_sentence = sentence_list[0]

        refined_paragraph = ""
        for i, sentence in enumerate(sentence_list[1:]):
            if curr_len + len(sentence) + 2 < 200:
                curr_sentence += '. ' + sentence
            else:
                refined_message_obj = generator(curr_sentence,  num_return_sequences=3)
                refined_sentence = rd.choice(refined_message_obj)['summary_text']
                refined_paragraph += refined_sentence.strip() + ". "
                curr_len = len(sentence)
                curr_sentence = sentence
            if i == (len(sentence_list) - 2):
                refined_message_obj = generator(curr_sentence,  num_return_sequences=3)
                refined_sentence = rd.choice(refined_message_obj)['summary_text']
                refined_paragraph += refined_sentence.strip() + "."

        returned_message += refined_paragraph + "\n\n"
    return returned_message[:-2] if returned_message[-2:] == '\n\n' else returned_message

    # Load and preprocess data
data = load_dataset(CLEAN_DATA_JSON_ID)
corpus, doc_ids, doc_id_comments_mapper = prepare_corpus(data)
# # Build retrieval system
generator = load_generative_model(SUMMERIZER_ID)
vector_embedder, matrices = build_post_matrix(corpus, MATRIX_ID)
