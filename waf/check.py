import joblib
import pandas as pd

# Load the feature extractor and detector
feature_extractor = joblib.load('waf_feature_extractor.pkl')
detector = joblib.load('waf_bypass_detector_complete.pkl')

print("Model and feature extractor loaded successfully on Kali!")

# Example usage (assuming X_train.columns was saved or known)
# A dummy payload for testing (replace with actual test payload if needed)
dummy_payload = "GET /index.html HTTP/1.1"
features = feature_extractor.extract_all_features(dummy_payload)

# You need the column names from the training data for prediction
# For simplicity, let's assume we have X_train_cols available from your Colab session
# In a real scenario, you'd ensure your feature extraction generates consistent columns
# For this example, we'll create a DataFrame with just the extracted features
# and then assume a fixed set of column names (e.g., from X_train.columns)

# IMPORTANT: To make predictions, the features_df MUST have the same columns in the same order as X_train
# You would typically save X_train.columns or a list of feature names during training
# For demonstration, we'll just create a DataFrame from the extracted features
features_df = pd.DataFrame([features])

# If you saved X_train.columns, you would ensure features_df aligns with it:
# expected_columns = [...] # Load this from a saved file if available
# missing_cols = set(expected_columns) - set(features_df.columns)
# for col in missing_cols:
#     features_df[col] = 0
# features_df = features_df[expected_columns]

# Make prediction
prediction, probability = detector.predict(features_df)

if prediction[0] == 1:
    print(f"Detected Attack/Bypass with confidence: {probability[0]*100:.2f}%")
else:
    print(f"Detected Benign traffic with confidence: {(1-probability[0])*100:.2f}%")
