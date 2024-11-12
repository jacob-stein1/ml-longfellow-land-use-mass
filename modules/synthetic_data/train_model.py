import sys
import os
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Add the path to deed_preprocessing to sys.path
sys.path.append(os.path.abspath('../deed_preprocessing'))

# Import the preprocess_text function
from preprocessor import preprocess_text

# Import the preprocess_bag_of_words function
sys.path.append(os.path.abspath('../model_experimentation'))
from bag_of_words_logistic_regression import preprocess_bag_of_words

warnings.filterwarnings("ignore", category=FutureWarning)

# Paths to data
non_racist_gt_path = '../model_experimentation/non_racist_deeds_text/'
racist_gt_path = '../model_experimentation/racist_deeds_text/'
synthetic_data_path = './synthetic_data'
misclassified_dir = './misclassified_texts'

# Ensure the directory for misclassified texts exists
os.makedirs(misclassified_dir, exist_ok=True)

print("Loading existing preprocessed data...")
with open('../model_experimentation/preprocessed_deeds.pkl', 'rb') as f:
    preprocessed_data = pickle.load(f)
print(f"Size of preprocessed data: {preprocessed_data.shape}")

# Function to preprocess and label synthetic data
def preprocess_synthetic_data(synthetic_data_path):
    synthetic_texts = []
    for filename in os.listdir(synthetic_data_path):
        if filename.endswith('.txt'):
            with open(os.path.join(synthetic_data_path, filename), 'r', encoding='utf-8') as f:
                text = f.read()
                processed = preprocess_text(text)
                processed['is_racist'] = 1
                synthetic_texts.append(processed)
    
    return synthetic_texts

print("Preprocessing synthetic data and adding to existing data...")
synthetic_data = preprocess_synthetic_data(synthetic_data_path)
preprocessed_data = pd.concat([preprocessed_data, pd.DataFrame(synthetic_data)], ignore_index=True)
print(f"Total data size after adding synthetic data: {preprocessed_data.shape}")

print("Creating Bag of Words representation...")
texts = preprocessed_data['original_text']
preprocessed_text_list = texts.apply(lambda x: {"original_text": x}).tolist()
bow_df, vectorizer = preprocess_bag_of_words(preprocessed_text_list)

# Define X and y
X = bow_df
y = preprocessed_data['is_racist']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
print(f"Training data size: {X_train.shape}, Test data size: {X_test.shape}")

# Train Logistic Regression model
print("Training Logistic Regression model...")
logistic_model = LogisticRegression(max_iter=1000)
logistic_model.fit(X_train, y_train)

# Save updated model and vectorizer
print("Saving new vectorizer and logistic model...")
with open('vectorizer.pkl', 'wb') as vec_file:
    pickle.dump(vectorizer, vec_file)
with open('logistic_model.pkl', 'wb') as model_file:
    pickle.dump(logistic_model, model_file)

# Evaluate the model
print("Evaluating model...")
y_pred = logistic_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save misclassified texts
print("Saving misclassified texts...")

misclassified_indexes = X_test.index[y_test.values != y_pred]

for idx in misclassified_indexes:
    text = preprocessed_data.loc[idx, 'original_text']
    is_racist = y_test.loc[idx]
    predicted = y_pred[X_test.index.get_loc(idx)]

    filename = f"{misclassified_dir}/misclassified_{idx}_actual_{is_racist}_pred_{predicted}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)

print(f'Saved {len(misclassified_indexes)} misclassified texts to {misclassified_dir}')


# Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 4))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", xticklabels=['Non-racist', 'Racist'], yticklabels=['Non-racist', 'Racist'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# ROC Curve
y_prob = logistic_model.predict_proba(X_test)[:, 1]
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(6, 4))
plt.plot(fpr, tpr, label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.show()

# Feature Importance
feature_importance = pd.Series(logistic_model.coef_[0], index=vectorizer.get_feature_names_out())
top_features = feature_importance.nlargest(10)

plt.figure(figsize=(8, 6))
top_features.plot(kind='barh', color='skyblue')
plt.title('Top 10 Most Influential Words for Racist Classification')
plt.xlabel('Coefficient Value')
plt.ylabel('Word')
plt.show()
