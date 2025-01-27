import pickle
import random as rd

# from bot_responser import (
#     vector_embedder, matrices, generator, doc_id_comments_mapper,
#     find_response_message, paraphrase_message
# )

# from bot_responser import build_post_matrix

from io import BytesIO
import gdown, lzma, json

from flask import Flask, render_template, request, jsonify
# from config import CLASSIFIER_ID, CLEAN_DATA_JSON_ID, SUMMERIZER_ID, MATRIX_ID, EMBEDDER_ID

from config import PORT, CLASSIFIER_ID, DOC_ID_COMMENTS_MAPPER_ID, SUMMERIZER_ID, MATRIX_ID, EMBEDDER_ID

def load_dataset(clean_data_json_id):
    file_url = f"https://drive.google.com/uc?id={clean_data_json_id}"
    memory_file = BytesIO()
    gdown.download(file_url, output=memory_file, quiet=False)
    memory_file.seek(0)
    return json.load(memory_file)


def prepare_corpus(doc_id_comments_id):

    file_url = f"https://drive.google.com/uc?id={doc_id_comments_id}"
    memory_file = BytesIO()
    gdown.download(file_url, output=memory_file, quiet=False)
    memory_file.seek(0)
    return json.load(memory_file)

    # doc_id_comments = {}
    # doc_set = set()
    # doc_ids = dict()
    # for post in data:
    #     content = post['post_content']
    #     if content not in doc_set:
    #         doc_ids[content] = len(doc_set)
    #         doc_set.add(content)
    #
    #     doc_id_comments[doc_ids[content]] = [
    #         {
    #             'comment_content': comment['comment_content'],
    #             'comment_score': comment['comment_score']
    #         } for comment in post['comments_list']
    #     ]

    # return doc_id_comments


def build_post_matrix(
        # corpus,
        matrix_id,
        embedder_id,
        model_name='all-MiniLM-L6-v2',
        matrix_file_path='model/matrix_corpus.pickle',
        embedder_file_path='model/sentence_embedder.pickle'
):


    # # this is the old version to get the embedded corpus matrix

    # if not os.path.isfile(embedder_file_path):
    #     embedder = SentenceTransformer(model_name)
    #     with open(embedder_file_path, 'wb') as file:
    #         # Serialize and write the variable to the file
    #         pickle.dump(embedder, file)
    #         file.close()
    # else:
    #     with open(embedder_file_path, 'rb') as file:
    #         # Deserialize and retrieve the variable from the file
    #         embedder = pickle.load(file)
    #         file.close()

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

    file_url = f"https://drive.google.com/uc?id={embedder_id}"
    embedder_memory_file = BytesIO()
    gdown.download(file_url, output=embedder_memory_file, quiet=True)
    embedder_memory_file.seek(0)

    embedder = pickle.load(lzma.open(embedder_memory_file, 'rb'))

    file_url = f"https://drive.google.com/uc?id={matrix_id}"
    matrix_memory_file = BytesIO()
    gdown.download(file_url, output=matrix_memory_file, quiet=True)
    matrix_memory_file.seek(0)

    matrix = pickle.load(lzma.open(matrix_memory_file, 'rb'))

    return embedder, matrix

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

    generator = pickle.load(lzma.open(memory_file, "rb"))
    return generator


def get_classifier_model(classifier_id, cls_model_pickle_file="model/svc_1vR_classifier.pickle"):
    # with open(cls_model_pickle_file, 'rb') as file:
    #     # Deserialize and retrieve the variable from the file
    #     cls_1vR_model = pickle.load(file)

    file_url = f"https://drive.google.com/uc?id={classifier_id}"
    memory_file = BytesIO()
    gdown.download(file_url, output=memory_file, quiet=True)
    memory_file.seek(0)

    cls_1vR_model = pickle.load(memory_file)

    return cls_1vR_model

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


def classifier(query, embedder, classifier):
    embedded_vector = embedder.encode(query, convert_to_tensor=False).reshape(1,-1)
    y_pred = classifier.predict_proba(embedded_vector)
    # print(classifier.class_)
    return y_pred


def prepare_classifier_message(predicted_result, classes):
    chosen_class = None
    max_acc = 0
    class_acc_mapper = dict()
    for i, acc in enumerate(predicted_result[0]):
        class_acc_mapper[classes[i]] = str(round(acc*100, 2)) + "%"
        if acc > max_acc:
            chosen_class = classes[i]
            max_acc = acc
    message_format = rd.choice([
        "Here's the predicted outcome for your condition:",
        "The analysis suggests the following syndrome:",
        "Based on your input, the predicted result is:",
        "Your potential health condition is identified as:",
        "The system has identified the following result for your symptoms:"
    ])
    for i, cls in enumerate(classes):
        if (i > 0):
            message_format += ", "
        message_format += f" {cls}: {class_acc_mapper[cls]}"
    return message_format

# data = load_dataset(CLEAN_DATA_JSON_ID)
doc_id_comments_mapper = prepare_corpus(DOC_ID_COMMENTS_MAPPER_ID)
vector_embedder, matrices = build_post_matrix(MATRIX_ID, EMBEDDER_ID)

# generator = load_generative_model(SUMMERIZER_ID)
# classifier_model = get_classifier_model(CLASSIFIER_ID)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/greeting', methods=['POST'])
def greeting():
    greetings = [
        "Hello! I’m a Bot, designed to provide information and support on topics such as Depression, Anxiety, Eating Disorders, Bipolar Disorder, ADHD, PTSD, and OCD. Feel free to share your thoughts with me, and I’ll do my best to assist you.",
        "Hi there! I’ve been trained with knowledge on various mental health topics, including Depression, Anxiety, Eating Disorders, Bipolar Disorder, ADHD, PTSD, and OCD. Let me know what’s on your mind, and I’ll try to help as much as I can.",
        "Greetings! I’m here to assist with questions or concerns about mental health, such as Depression, Anxiety, Eating Disorders, Bipolar Disorder, ADHD, PTSD, and OCD. Please share your story with me, and I’ll do my best to support you.",
        "Welcome! I’m a chatbot created to help with discussions about mental health topics, including Depression, Anxiety, Eating Disorders, Bipolar Disorder, ADHD, PTSD, and OCD. Tell me your story, and I’ll provide the best assistance I can.",
        "Hi! I’m here to support conversations on mental health topics like Depression, Anxiety, Eating Disorders, Bipolar Disorder, ADHD, PTSD, and OCD. Share your thoughts with me, and I’ll do my best to provide a helpful response.",
        "Hello! I’m equipped to talk about mental health concerns, including Depression, Anxiety, Eating Disorders, Bipolar Disorder, ADHD, PTSD, and OCD. Feel free to open up about your experience, and I’ll strive to assist you."
    ]

    return jsonify({'reply': rd.choice(greetings)})


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    # response_comments = find_response_message(user_message, matrices, doc_id_comments_mapper, vector_embedder)
    # response = paraphrase_message(response_comments, generator)
    #
    # class_proba = classifier(user_message, vector_embedder, classifier_model)
    # classifier_text = prepare_classifier_message(class_proba, classifier_model.classes_)
    # response = f"{classifier_text}\n\n{response}"

    # return jsonify({'reply': response})
    return jsonify({'reply': user_message})


if __name__ == '__main__':
    app.run()