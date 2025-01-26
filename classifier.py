import pickle
import json
from sentence_transformers import SentenceTransformer
import os
import numpy as np
import tqdm


from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedShuffleSplit, GridSearchCV

from config import CLEAN_DATA_JSON_ID, MATRIX_ID

# Load your Reddit dataset
def load_dataset(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        f.close()

        return data

# Step 1: Build the retrieval corpus
def prepare_corpus(data):

    corpus = []
    corpus_group = []
    doc_set = set()
    for post in data:
        content = post['post_content']
        group = post['group']
        if content not in doc_set:
            doc_set.add(content)
            corpus.append(content)
            corpus_group.append(group)


    return corpus, corpus_group

# Step 2: Create and store embeddings
def build_post_matrix(corpus, model_name='all-MiniLM-L6-v2', matrix_file_path='model/matrix_corpus.pickle'):

    embedder = SentenceTransformer(model_name)
    if not os.path.isfile(matrix_file_path):
        matrix = np.array([embedder.encode(doc, convert_to_tensor=False) for doc in tqdm(corpus)])
        with open(matrix_file_path, 'wb') as file:
            # Serialize and write the variable to the file
            pickle.dump(matrix, file)
            file.close()
    else:
        with open(matrix_file_path, 'rb') as file:
            # Deserialize and retrieve the variable from the file
            matrix = pickle.load(file)
            file.close()

    return embedder, matrix

data = load_dataset("data/clean/clean_data.json")
corpus, corpus_labels = prepare_corpus(data)
# Build retrieval system
_, matrices = build_post_matrix(corpus)

y = np.array(corpus_labels)
if __name__ == "__main__":
    print("Label distribution:")
    for label in set(corpus_labels):
        print(f"{round((y==label).sum() * 100 / y.shape[0], 2)}% {label}")

    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=0)
    X_train, X_test, y_train, y_test = None, None, None, None

    for train_index, test_index in splitter.split(matrices, y):
        X_train, X_test = matrices[train_index], matrices[test_index]
        y_train, y_test = y[train_index], y[test_index]

    # 1vsR + SVC: 79%: OneVsRestClassifier(SVC())
    parameters = {'kernel':('linear', 'poly', 'rbf', 'sigmoid'), 'C': [10**i for i in range(-3, 3)]}

    searcher = GridSearchCV(SVC(probability=True, class_weight='balanced', random_state=0), parameters)
    print()
    searcher.fit(X_train, y_train)
    print("finish grid search")
    print(searcher.best_params_)

    svc_model = SVC(probability=True, class_weight='balanced', random_state=0)
    svc_model.set_params(**searcher.best_params_) # C=1, kernel="poly"
    svc_1vR_model = OneVsRestClassifier(svc_model)

    svc_1vR_model.fit(X_train, y_train)
    print('finish training')
    score = svc_1vR_model.score(X_test, y_test)
    print(score)

    with open("model/svc_1vR_classifier.pickle", 'wb') as file:
        # Serialize and write the variable to the file
        pickle.dump(svc_1vR_model, file)
        file.close()