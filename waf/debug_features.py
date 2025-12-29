import joblib
import pandas as pd
from waf_bypass import WAFBypassDetector, WAFBypassFeatureExtractor

try:
    detector = joblib.load('waf_bypass_detector_complete.pkl')
    print("Model loaded.")
    
    if hasattr(detector.scaler, 'feature_names_in_'):
        print("\nExpected features (from scaler):")
        print(list(detector.scaler.feature_names_in_))
        print(f"\nTotal expected features: {len(detector.scaler.feature_names_in_)}")
    else:
        print("Scaler does not have feature_names_in_")

    # Also check the script's X_train_columns
    from waf_bypass import X_train_columns
    print("\nFeatures in script (X_train_columns):")
    print(X_train_columns)
    print(f"\nTotal script features: {len(X_train_columns)}")

    if hasattr(detector.scaler, 'feature_names_in_'):
        expected = list(detector.scaler.feature_names_in_)
        actual = X_train_columns
        
        missing = set(expected) - set(actual)
        extra = set(actual) - set(expected)
        
        if missing:
            print(f"\nMissing in script: {missing}")
        if extra:
            print(f"\nExtra in script: {extra}")
            
        if expected != actual:
            print("\nOrder mismatch or content mismatch detected.")
            
except Exception as e:
    print(f"Error: {e}")
