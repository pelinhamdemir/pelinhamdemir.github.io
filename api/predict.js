  // api/predict.js
const { SentenceTransformer, util } = require('sentence-transformers');
const { Translator } = require('googletrans');
const fs = require('fs');
const path = require('path');

exports.handler = async function(event, context) {
    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            body: 'Method Not Allowed',
        };
    }

    const data = JSON.parse(event.body);
    const userInput = data.user_input;

    // Load and process data here (example code)
    const filePath = path.resolve(__dirname, 'ssb_teknoloji_taksonomisi_corrected (1).xlsx');
    const df = require('exceljs');
    const workbook = new df.Workbook();
    await workbook.xlsx.readFile(filePath);
    const sheet = workbook.getWorksheet(1);

    const model = new SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2');
    const codes = sheet.getColumn(1).values.slice(1).map(String);
    const titles = sheet.getColumn(2).values.slice(1).map(String);
    const paragraphs = sheet.getColumn(3).values.slice(1).map(String);

    const titleEmbeddings = model.encode(titles, convert_to_tensor=True);
    const paragraphEmbeddings = model.encode(paragraphs, convert_to_tensor=True);

    const translator = new Translator();
    const translated = await translator.translate(userInput, { to: 'en' });
    const inputSentence = translated.text;

    const inputEmbedding = model.encode(inputSentence, convert_to_tensor=True);
    const titleSimilarities = util.pytorch_cos_sim(inputEmbedding, titleEmbeddings)[0];
    const paragraphSimilarities = util.pytorch_cos_sim(inputEmbedding, paragraphEmbeddings)[0];

    const combinedSimilarities = titleSimilarities.map((sim, i) => ({
        titleSimilarity: sim.item(),
        paragraphSimilarity: paragraphSimilarities[i].item(),
        index: i
    }));

    combinedSimilarities.sort((a, b) => (b.titleSimilarity + b.paragraphSimilarity) - (a.titleSimilarity + a.paragraphSimilarity));

    const results = combinedSimilarities.slice(0, 3).map(sim => ({
        code: codes[sim.index],
        title: titles[sim.index],
        paragraph: paragraphs[sim.index],
        similarity: sim.titleSimilarity
    }));

    return {
        statusCode: 200,
        body: JSON.stringify(results),
    };
};
