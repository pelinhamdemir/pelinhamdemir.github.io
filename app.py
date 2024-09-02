from flask import Flask, request, jsonify, send_from_directory, render_template
from dotenv import load_dotenv
import os
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
from googletrans import Translator
import pandas as pd

# Çevresel değişkenleri yükleyin
load_dotenv()

# Flask uygulamasını başlatın
app = Flask(__name__)
CORS(app)  # CORS'u etkinleştirin, böylece diğer alan adlarından gelen istekler kabul edilir

# Çevresel değişkenlerden debug modunu alın
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG')

# Ana sayfa rotası - index.html dosyasını render eder
@app.route('/')
def index():
    return render_template('index.html')  

# Sentence Transformer modelini yükleyin
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# Excel dosyasını yükleyin ve verileri dataframe'e aktarın
file_path = 'ssb_teknoloji_taksonomisi_corrected (3).xlsx'
df = pd.read_excel(file_path)

# Excel'den kodlar, başlıklar, 3. ve 4. sütundaki paragrafları alın
codes = df.iloc[:, 0].astype(str).tolist()
titles = df.iloc[:, 1].astype(str).tolist()
paragraphs_to_compare = df.iloc[:, 2].astype(str).tolist()  # 3. sütundaki paragraflar
paragraphs_to_display = df.iloc[:, 3].astype(str).tolist()  # 4. sütundaki paragraflar

# 3. sütundaki paragraf metinlerini embed ederek tensorlara dönüştürün
paragraph_embeddings = model.encode(paragraphs_to_compare, convert_to_tensor=True)

# Arama API rotası - Kullanıcıdan gelen cümleye göre en iyi eşleşmeleri döndürür
@app.route('/search', methods=['POST'])
def search():
    # Kullanıcıdan gelen cümleyi alın
    input_sentence = request.json['input_sentence']
    translator = Translator()

    # Girdi cümlesini İngilizceye çevirin
    translated = translator.translate(input_sentence, dest='en')
    input_sentence = translated.text

    # Girdi cümlesini embed edin ve 3. sütundaki paragraflar ile olan benzerlikleri hesaplayın
    input_embedding = model.encode(input_sentence, convert_to_tensor=True)
    paragraph_similarities = util.pytorch_cos_sim(input_embedding, paragraph_embeddings)[0]

    # Paragraf benzerliklerini sıralayın
    combined_similarities = [(paragraph_similarities[i].item(), i) for i in range(len(paragraphs_to_compare))]
    combined_similarities.sort(key=lambda x: x[0], reverse=True)

    # En iyi 3 sonucu alın
    results = []
    top_n = 3
    for sim in combined_similarities[:top_n]:
        best_index = sim[1]
        best_code = codes[best_index]
        best_title = titles[best_index]
        best_paragraph_to_compare = "EN: " + paragraphs_to_compare[best_index]  # 3. sütundaki paragraf
        best_paragraph_to_display = "TR: " + paragraphs_to_display[best_index]  # 4. sütundaki paragraf
        similarity_score = sim[0]  # Paragraf benzerlik skoru

        # Sonuçları bir sözlük olarak ekleyin
        results.append({
            "code": best_code,
            "title": best_title,
            "paragraph_to_compare": best_paragraph_to_compare,  # 3. sütundaki paragraf (TR)
            "paragraph_to_display": best_paragraph_to_display,  # 4. sütundaki paragraf (EN)
            "similarity": round(similarity_score, 2)  # Benzerlik skorunu yuvarlayın
        })

    # Sonuçları benzerlik skoruna göre sıralayın
    results.sort(key=lambda x: x['similarity'], reverse=True)

    # Sonuçları konsola yazdırın
    for result in results:
        print(f"Code: {result['code']}, Title: {result['title']}, Similarity: {result['similarity']}")
        print(f"  {result['paragraph_to_compare']}")
        print(f"  {result['paragraph_to_display']}\n")

    if not results:
        print("No valid results found.")    

    # Sonuçları JSON formatında döndürün
    return jsonify(results)

# Uygulamayı başlatı
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
