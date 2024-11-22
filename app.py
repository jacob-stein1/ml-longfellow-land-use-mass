from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
from modules.google_cloud_ocr.google_cloud_ocr import google_cloud_ocr
from modules.azure_cloud_ocr.azure_cloud_ocr import azure_cloud_ocr
from modules.deed_preprocessing.spellcheck import correct_spelling
from modules.deed_preprocessing.preprocessor import preprocess_text
from modules.openai.racist_chatgpt_analysis import racist_chatgpt_analysis
from modules.model_experimentation.bag_of_words_logistic_regression import predict

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

with open('modules/model_experimentation/vectorizer.pkl', 'rb') as vec_file:
    vectorizer = pickle.load(vec_file)

with open('modules/model_experimentation/logistic_model.pkl', 'rb') as model_file:
    logistic_model = pickle.load(model_file)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    ocr_engine = request.form.get('ocr_engine', 'google')
    analysis_method = request.form.get('analysis_method', 'chatgpt')

    try:
        if ocr_engine == 'google':

            # Step 1: Get text using Google OCR
            google_text = google_cloud_ocr(file)

            # Step 2: Pass text through the spell checker
            spellchecked_text = correct_spelling(google_text)

            # Step 3: Pass text through the preprocessor
            processed_text = preprocess_text(spellchecked_text)
            
            # Step 4: Choose analysis method
            if analysis_method == 'chatgpt':
                analysis_result = racist_chatgpt_analysis(processed_text['original_text'])
                return jsonify({
                    'status': 'success',
                    'ocr_engine': 'google',
                    'analysis_method': 'chatgpt',
                    'original_text': google_text,
                    'spellchecked_text': spellchecked_text,
                    'processed_text': processed_text,
                    'result': analysis_result
                }), 200
            elif analysis_method == 'logistic_regression':
                lr_result = predict(processed_text, vectorizer, logistic_model)['is_racist']
                return jsonify({
                    'status': 'success',
                    'ocr_engine': 'google',
                    'analysis_method': 'logistic_regression',
                    'original_text': google_text,
                    'spellchecked_text': spellchecked_text,
                    'processed_text': processed_text,
                    'result': lr_result
                }), 200
            else:
                return jsonify({'error': 'Unsupported analysis method selected'}), 400
        elif ocr_engine == 'azure':
            azure_text = azure_cloud_ocr(file)
            return jsonify({'status': 'success', 'ocr_engine': 'azure', 'text': azure_text}), 200
        else:
            return jsonify({'error': 'Unsupported OCR engine selected'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
