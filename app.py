from flask import Flask, request, jsonify, send_from_directory
from sentence_transformers import SentenceTransformer, util
from googletrans import Translator
import pandas as pd
from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return send_from_directory(".",'index.html')

# Modeli yükleyin
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Excel dosyasını yükleyin
file_path = 'ssb_teknoloji_taksonomisi_corrected (1).xlsx'
df = pd.read_excel(file_path)
codes = df.iloc[:, 0].astype(str).tolist()
titles = df.iloc[:, 1].astype(str).tolist()
paragraphs = df.iloc[:, 2].astype(str).tolist()

# Embed işlemleri
title_embeddings = model.encode(titles, convert_to_tensor=True)
paragraph_embeddings = model.encode(paragraphs, convert_to_tensor=True)

@app.route('/search', methods=['POST'])
def search():
    input_sentence = request.json['input_sentence']
    translator = Translator()

    translated = translator.translate(input_sentence, dest='en')
    input_sentence = translated.text

    input_embedding = model.encode(input_sentence, convert_to_tensor=True)
    title_similarities = util.pytorch_cos_sim(input_embedding, title_embeddings)[0]
    paragraph_similarities = util.pytorch_cos_sim(input_embedding, paragraph_embeddings)[0]

    combined_similarities = [(title_similarities[i].item(), paragraph_similarities[i].item(), i) for i in range(len(titles))]
    combined_similarities.sort(key=lambda x: (x[0] + x[1]), reverse=True)

    results = []
    top_n = 3
    for sim in combined_similarities[:top_n]:
        best_index = sim[2]
        best_code = codes[best_index]
        best_title = titles[best_index]
        best_paragraph = paragraphs[best_index]
        similarity_score = sim[0]  # Toplam similarity score

        results.append({
            "code": best_code,
            "title": best_title,
            "paragraph": best_paragraph,
            "similarity": round(similarity_score, 2)
        })

    # Results'ı similarity değerine göre sıralayın
    results.sort(key=lambda x: x['similarity'], reverse=True)

    for result in results:
        print(f" {result['code']}, {result['title']}, Similarity: {result['similarity']},paragraph: {result['paragraph']}")

    if not results:
        print("No valid results found.")

    return results


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5001)
