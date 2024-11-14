from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
from fuzzywuzzy import process  # Fuzzy matching for symptom correction

app = Flask(__name__)

# Sample dataset for Symptoms and corresponding Medicines and Diet
data = {
    'Symptoms': [
        'fever', 'fever, cough', 'headache', 'nausea, vomiting', 'chest pain',
        'fever, body pain', 'shortness of breath', 'stomach ache', 'sore throat',
        'runny nose', 'dizziness', 'rash', 'diarrhea', 'constipation', 'muscle pain',
        'fatigue', 'back pain', 'joint pain', 'dry cough', 'chest tightness',
        'sneezing, itchy eyes', 'high blood pressure', 'heartburn', 'insomnia',
        'allergic reaction (mild)', 'migraine', 'toothache', 'earache',
        'sore muscles after exercise', 'cold sores', 'urinary tract infection (UTI)',
        'menstrual cramps', 'anxiety', 'depression', 'flu-like symptoms',
        'bloating', 'sunburn', 'acne', 'cold feet (poor circulation)',
        'indigestion', 'high cholesterol'
    ],
    'Medicines': [
        'Paracetamol', 'Paracetamol, Cough Syrup', 'Migraine Medicine', 'Antiemetic',
        'Aspirin', 'Paracetamol, Pain Reliever', 'Inhaler', 'Antacid', 'Throat Lozenges',
        'Antihistamine', 'Meclizine', 'Hydrocortisone Cream', 'Oral Rehydration Solution',
        'Laxative', 'Ibuprofen', 'Vitamin Supplements', 'Ibuprofen, Muscle Relaxant',
        'Diclofenac Gel, Pain Reliever', 'Cough Suppressant', 'Bronchodilator',
        'Antihistamine, Allergy Eye Drops', 'Amlodipine', 'Antacid, Proton Pump Inhibitor (PPI)',
        'Melatonin, Sleep Aid', 'Antihistamine, Hydrocortisone Cream', 'Sumatriptan, Migraine Medicine',
        'Ibuprofen, Oral Analgesic Gel', 'Ear Drops, Ibuprofen', 'Ibuprofen, Muscle Rub',
        'Antiviral Cream', 'Antibiotic', 'Ibuprofen, Heating Pad', 'Benzodiazepine, Relaxation Techniques',
        'Antidepressant, Cognitive Behavioral Therapy', 'Paracetamol, Flu Medicine',
        'Antiflatulent, Probiotic Supplement', 'Aloe Vera Gel, Sunscreen',
        'Benzoyl Peroxide, Salicylic Acid Cream', 'Warm Compress, Vasodilator',
        'Antacid, Digestive Enzyme', 'Statins'
    ],
    'Diet': [
        'Stay hydrated, rest', 'Plenty of fluids, warm soups', 'Ginger tea, cold compress',
        'Clear liquids, bland foods', 'Healthy fats, whole grains', 'Fluids, protein-rich foods',
        'Fruits rich in Vitamin C', 'Light, bland foods', 'Warm fluids, soft foods',
        'Spicy foods, rest', 'Foods with iron', 'Cooling foods, hydration', 'Rice, banana, toast',
        'Fiber-rich foods, water', 'Lean protein, anti-inflammatory foods', 'Energy-rich snacks',
        'Magnesium-rich foods', 'Calcium-rich foods', 'Throat-soothing foods', 'High fiber diet',
        'Fruits rich in Vitamin C, ginger', 'Low sodium diet', 'Low acid foods, small meals',
        'Chamomile tea, warm milk', 'Antioxidant-rich foods', 'Caffeine, sugar reduction',
        'Soft foods, no cold drinks', 'Protein, healthy fats', 'Turmeric, ginger', 'Antiviral foods',
        'Cranberry juice, water', 'Dark chocolate, magnesium', 'Leafy greens, omega-3 foods',
        'Vitamin D, zinc-rich foods', 'Fiber-rich diet, probiotics', 'Hydration, electrolytes',
        'Cooling foods, water', 'Omega-3 rich foods', 'Warming foods, ginger tea',
        'Low fat, low sugar foods', 'Heart-healthy foods'
    ]

    # Your data here
}

# Convert dictionary to DataFrame
df = pd.DataFrame(data)

# Preprocess Data: Combine symptoms into one string per row
df['symptoms_combined'] = df['Symptoms'].apply(lambda x: ' '.join(str(x).split(',')))

# Vectorizing the symptom data
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['symptoms_combined'])

# Medicines (target variable)
y_medicine = df['Medicines']
y_diet = df['Diet']

# Split the data into training and testing sets
X_train, X_test, y_train_medicine, y_test_medicine, y_train_diet, y_test_diet = train_test_split(X, y_medicine, y_diet, test_size=0.2, random_state=42)

# Train the Random Forest Classifier for medicines
model_medicine = RandomForestClassifier(random_state=42)
model_medicine.fit(X_train, y_train_medicine)

# Train another Random Forest Classifier for diet
model_diet = RandomForestClassifier(random_state=42)
model_diet.fit(X_train, y_train_diet)

# Function to predict medicine and diet based on symptoms with fuzzy matching
def predict_medicine_and_diet(symptoms_input):
    # Use fuzzy matching to find the closest matching symptom in the dataset
    possible_symptoms = df['Symptoms'].tolist()
    matched_symptom, confidence = process.extractOne(symptoms_input, possible_symptoms)

    # Set a threshold for the confidence score
    if confidence < 75:  # If confidence is below 75%, consider it a mismatch
        return "Symptom not found", "Symptom not found"

    # Preprocess the matched symptom
    symptoms_input = [' '.join(matched_symptom.split(','))]
    symptoms_vector = vectorizer.transform(symptoms_input)

    # Get predictions
    try:
        predicted_medicine = model_medicine.predict(symptoms_vector)[0]
    except IndexError:
        predicted_medicine = "Medicine not found"

    try:
        predicted_diet = model_diet.predict(symptoms_vector)[0]
    except IndexError:
        predicted_diet = "Diet not found"

    return predicted_medicine, predicted_diet

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# Endpoint to process the user input and return predictions
@app.route('/predict', methods=['POST'])
def predict():
    symptoms = request.form['symptoms']
    predicted_medicine, predicted_diet = predict_medicine_and_diet(symptoms)
    return render_template('result.html', medicine=predicted_medicine, diet=predicted_diet)

if __name__ == '__main__':
    app.run(debug=True)
