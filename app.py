import pickle
import random as rd

from bot_responser import (
    vector_embedder, matrices, generator, doc_id_comments_mapper,
    find_response_message, paraphrase_message, BytesIO, gdown
)

from flask import Flask, render_template, request, jsonify
from config import CLASSIFIER_ID

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


classifier_model = get_classifier_model(CLASSIFIER_ID)

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
    response_comments = find_response_message(user_message, matrices, doc_id_comments_mapper, vector_embedder)
    response = paraphrase_message(response_comments, generator)

    class_proba = classifier(user_message, vector_embedder, classifier_model)
    classifier_text = prepare_classifier_message(class_proba, classifier_model.classes_)

    response = f"{classifier_text}\n\n{response}"
    return jsonify({'reply': response})


if __name__ == '__main__':
    app.run(debug=True, port=8050, host='0.0.0.0')