from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from googletrans import Translator

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://pelinhamdemir.github.io"}})

file_path = 'ssb_teknoloji_taksonomisi_corrected (1).xlsx'
df = pd.read_excel(file_path)

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
codes = df.iloc[:, 0].astype(str).tolist()
titles = df.iloc[:, 1].astype(str).tolist()
paragraphs = df.iloc[:, 2].astype(str).tolist()

title_embeddings = model.encode(titles, convert_to_tensor=True)
paragraph_embeddings = model.encode(paragraphs, convert_to_tensor=True)

def find_related_codes(input_sentence, top_n=3):
    translator = Translator()
    translated = translator.translate(input_sentence, dest='en')
    input_sentence = translated.text

    input_embedding = model.encode(input_sentence, convert_to_tensor=True)

    title_similarities = util.pytorch_cos_sim(input_embedding, title_embeddings)[0]
    paragraph_similarities = util.pytorch_cos_sim(input_embedding, paragraph_embeddings)[0]

    combined_similarities = [(title_similarities[i].item(), paragraph_similarities[i].item(), i) for i in range(len(titles))]
    combined_similarities.sort(key=lambda x: (x[0] + x[1]), reverse=True)

    results = []
    for sim in combined_similarities[:top_n]:
        best_index = sim[2]
        best_code = codes[best_index]
        best_title = titles[best_index]
        best_paragraph = paragraphs[best_index]
        similarity_score = sim[0]

        results.append({
            "code": best_code,
            "title": best_title,
            "paragraph": best_paragraph,
            "similarity": similarity_score
        })

    return results

@app.route('/api/predict', methods=['POST'])
def search():
    data = request.get_json()
    user_input = data.get('user_input')
    results = find_related_codes(user_input, top_n=3)
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
