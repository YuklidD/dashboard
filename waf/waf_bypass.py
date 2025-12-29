import joblib
import pandas as pd
import numpy as np
import re
from collections import Counter
import warnings

# Suppress all warnings for cleaner output in production/Kali environment
warnings.filterwarnings('ignore')

# --- BEGIN WAFBypassFeatureExtractor CLASS DEFINITION (from previous cell) ---
class WAFBypassFeatureExtractor:
    """Extract features specifically for WAF bypass detection"""

    def __init__(self):
        self.encoding_patterns = {
            'url_encoding': r'%[0-9a-fA-F]{2}',
            'unicode': r'\\u[0-9a-fA-F]{4}',
            'hex_encoding': r'0x[0-9a-fA-F]+',
            'hex_escape': r'\\x[0-9a-fA-F]{2}',
            'octal_encoding': r'\\[0-7]{3}',
            'html_entity': r'&#[0-9]+;|&[a-z]+;',
            'double_encoding': r'%25[0-9a-fA-F]{2}'
        }

        self.obfuscation_patterns = {
            'comment_injection': r'/\\*.*\\*/|--', # Escaped for regex
            'comment_hash': r'#',
            'whitespace_abuse': r'[\\s\\t\\r\\n]{3,}', # Escaped for regex
            'null_bytes': r'%00',
            'null_bytes_hex': r'\\x00',
            'concatenation': r'\\+|\\|\\|', # Escaped for regex
            'concat_keyword': r'concat',
        }

        self.attack_keywords = {
            'sqli': ['union', 'select', 'insert', 'delete', 'drop', 'update',
                    'exec', 'execute', 'from', 'where'],
            'xss': ['script', 'alert', 'onerror', 'onload', 'eval', 'iframe',
                   'svg', 'img', 'onclick', 'onmouseover'],
            'path_traversal': ['etc/passwd', 'win.ini', 'dotdot'],
            'command_injection': ['cat', 'ls', 'wget', 'curl', 'bash']
        }

        # Additional patterns that need special handling
        self.special_patterns = {
            'path_dotdot': r'\\.\\./[\\/\\\\]', # Escaped for regex
            'path_encoded': r'%2e%2e',
        }

    def extract_encoding_features(self, payload: str) -> dict:
        """Detect encoding patterns"""
        features = {}

        for name, pattern in self.encoding_patterns.items():
            matches = re.findall(pattern, payload, re.IGNORECASE)
            features[f'enc_{name}_count'] = len(matches)
            features[f'enc_{name}_present'] = int(len(matches) > 0)

        # Multiple encoding layers
        total_encodings = sum(1 for k, v in features.items() if 'present' in k and v > 0)
        features['enc_layers'] = total_encodings
        features['enc_multi_layer'] = int(total_encodings >= 2)

        return features

    def extract_obfuscation_features(self, payload: str) -> dict:
        """Detect obfuscation techniques"""
        features = {}

        for name, pattern in self.obfuscation_patterns.items():
            matches = re.findall(pattern, payload, re.IGNORECASE)
            features[f'obf_{name}_count'] = len(matches)

        # Entropy calculation
        if payload:
            char_freq = Counter(payload)
            total = len(payload)
            entropy = -sum((c/total) * np.log2(c/total) for c in char_freq.values())
            features['payload_entropy'] = entropy
        else:
            features['payload_entropy'] = 0

        # Charset mixing
        has_alpha = bool(re.search(r'[a-zA-Z]', payload))
        has_digit = bool(re.search(r'[0-9]', payload))
        has_special = bool(re.search(r'[^a-zA-Z0-9\\s]', payload)) # Escaped for regex
        features['charset_mixed'] = int(sum([has_alpha, has_digit, has_special]) >= 2)

        # Case variation
        if payload:
            upper_count = sum(1 for c in payload if c.isupper())
            lower_count = sum(1 for c in payload if c.islower())
            if upper_count + lower_count > 0:
                features['case_variation'] = abs(upper_count - lower_count) / (upper_count + lower_count)
            else:
                features['case_variation'] = 0
        else:
            features['case_variation'] = 0

        return features

    def extract_attack_keywords(self, payload: str) -> dict:
        """Detect attack keywords"""
        features = {}
        payload_lower = payload.lower()

        for attack_type, keywords in self.attack_keywords.items():
            for keyword in keywords:
                # Direct match
                features[f'kw_{attack_type}_{keyword}'] = int(keyword in payload_lower)

                # Obfuscated match (characters separated)
                # Escape special regex characters in keyword before joining
                escaped_keyword = ''.join(['\\' + c if not c.isalnum() else c for c in keyword])
                obfusc_pattern = '.*'.join(list(escaped_keyword))
                features[f'kw_obf_{attack_type}_{keyword}'] = int(
                    bool(re.search(obfusc_pattern, payload_lower, re.IGNORECASE))
                )

        # Handle special patterns separately
        features['path_dotdot_present'] = int(bool(re.search(r'\\.\\./[\\/\\\\]', payload))) # Escaped for regex
        features['path_encoded_present'] = int(bool(re.search(r'%2e%2e', payload, re.IGNORECASE)))

        return features

    def extract_structural_features(self, payload: str) -> dict:
        """Extract structural features"""
        features = {}

        features['length'] = len(payload)
        features['word_count'] = len(re.findall(r'\\w+', payload)) # Escaped for regex
        features['special_char_ratio'] = sum(not c.isalnum() for c in payload) / max(len(payload), 1)
        features['digit_ratio'] = sum(c.isdigit() for c in payload) / max(len(payload), 1)
        features['alpha_ratio'] = sum(c.isalpha() for c in payload) / max(len(payload), 1)

        # Special characters count
        special_chars = ['<', '>', '"', "'", ';', '/', '\\', '(', ')', '{', '}', '[', ']'] # Escaped backslash
        for char in special_chars:
            features[f'char_{ord(char)}'] = payload.count(char)

        return features

    def extract_all_features(self, payload: str) -> dict:
        """Extract all features"""
        features = {}

        # Handle None/NaN
        if pd.isna(payload):
            payload = ""
        payload = str(payload)

        features.update(self.extract_encoding_features(payload))
        features.update(self.extract_obfuscation_features(payload))
        features.update(self.extract_attack_keywords(payload))
        features.update(self.extract_structural_features(payload))

        return features
# --- END WAFBypassFeatureExtractor CLASS DEFINITION ---


# --- BEGIN WAFBypassDetector CLASS DEFINITION (from previous cell) ---
# Required imports for WAFBypassDetector (ensure they are available on Kali)
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest, VotingClassifier, RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from imblearn.ensemble import BalancedRandomForestClassifier
# Note: SMOTE is used for training, not in prediction, so it's not strictly needed for this script

class WAFBypassDetector:
    """Multi-stage detector for WAF bypasses"""

    def __init__(self):
        # These will be loaded from the pickled model, but their classes must be defined.
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest()
        self.models = {}
        self.ensemble = VotingClassifier(estimators=[]) # Placeholder, actual will be loaded
        self.is_trained = False # This will be True after loading a trained model

    def build_models(self):
        """Build ensemble - not used when loading a trained model, but kept for class compatibility"""
        print("Building ensemble models (this function is usually for training, loading pre-trained now)")
        # This method is primarily for training. When loading from pickle,
        # the self.ensemble and other attributes will be overwritten by the loaded state.

        # For successful deserialization, the classes themselves (XGBClassifier, etc.)
        # must be importable in the environment.
        self.anomaly_detector = IsolationForest(
            contamination=0.15,
            random_state=42,
            n_jobs=-1
        )

        self.models['xgb'] = XGBClassifier(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss'
        )

        self.models['lgb'] = LGBMClassifier(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbose=-1
        )

        self.models['cat'] = CatBoostClassifier(
            iterations=150,
            depth=6,
            learning_rate=0.1,
            random_state=42,
            verbose=0
        )

        self.models['rf'] = BalancedRandomForestClassifier(
            n_estimators=150,
            max_depth=8,
            random_state=42,
            n_jobs=-1
        )

        self.ensemble = VotingClassifier(
            estimators=[
                ('xgb', self.models['xgb']),
                ('lgb', self.models['lgb']),
                ('cat', self.models['cat']),
                ('rf', self.models['rf'])
            ],
            voting='soft',
            n_jobs=-1
        )

    def train(self, X, y):
        """Train ensemble - not used in this prediction-only script"""
        raise NotImplementedError("Training functionality is not available in this prediction script.")

    def predict(self, X):
        """Predict with ensemble"""
        if not self.is_trained:
            # If loading a pickled detector, self.is_trained should be set to True upon loading.
            # For robustness, we can assume it's trained if loaded successfully.
            pass # Or add a check if self.ensemble is not None or similar

        X_scaled = self.scaler.transform(X)

        # Anomaly detection
        anomaly_pred = self.anomaly_detector.predict(X_scaled)
        anomaly_flags = (anomaly_pred == -1).astype(int)

        # Ensemble prediction
        ensemble_pred = self.ensemble.predict(X_scaled)
        ensemble_proba = self.ensemble.predict_proba(X_scaled)[:, 1]

        # Combined decision
        final_pred = np.maximum(anomaly_flags, ensemble_pred)

        return final_pred, ensemble_proba

    def evaluate(self, X_test, y_test):
        """Evaluate model - not used in this prediction-only script"""
        raise NotImplementedError("Evaluation functionality is not available in this prediction script.")

# --- END WAFBypassDetector CLASS DEFINITION ---


# --- Kali Script Core Logic ---
print("Kali WAF Bypass Detection Utility")
print("---------------------------------")

# Define the expected columns from training data
# This list should match the columns of X_train from your training environment
X_train_columns = [
    'enc_url_encoding_count', 'enc_url_encoding_present', 'enc_unicode_count',
    'enc_unicode_present', 'enc_hex_encoding_count', 'enc_hex_encoding_present',
    'enc_hex_escape_count', 'enc_hex_escape_present', 'enc_octal_encoding_count',
    'enc_octal_encoding_present', 'enc_html_entity_count',
    'enc_html_entity_present', 'enc_double_encoding_count',
    'enc_double_encoding_present', 'enc_layers', 'enc_multi_layer',
    'obf_comment_injection_count', 'obf_comment_hash_count',
    'obf_whitespace_abuse_count', 'obf_null_bytes_count',
    'obf_null_bytes_hex_count', 'obf_concatenation_count',
    'obf_concat_keyword_count', 'payload_entropy', 'charset_mixed',
    'case_variation', 'kw_sqli_union', 'kw_obf_sqli_union', 'kw_sqli_select',
    'kw_obf_sqli_select', 'kw_sqli_insert', 'kw_obf_sqli_insert',
    'kw_sqli_delete', 'kw_obf_sqli_delete', 'kw_sqli_drop', 'kw_obf_sqli_drop',
    'kw_sqli_update', 'kw_obf_sqli_update', 'kw_sqli_exec', 'kw_obf_sqli_exec',
    'kw_sqli_execute', 'kw_obf_sqli_execute', 'kw_sqli_from', 'kw_obf_sqli_from',
    'kw_sqli_where', 'kw_obf_sqli_where', 'kw_xss_script', 'kw_obf_xss_script',
    'kw_xss_alert', 'kw_obf_xss_alert', 'kw_xss_onerror', 'kw_obf_xss_onerror',
    'kw_xss_onload', 'kw_obf_xss_onload', 'kw_xss_eval', 'kw_obf_xss_eval',
    'kw_xss_iframe', 'kw_obf_xss_iframe', 'kw_xss_svg', 'kw_obf_xss_svg',
    'kw_xss_img', 'kw_obf_xss_img', 'kw_xss_onclick', 'kw_obf_xss_onclick',
    'kw_xss_onmouseover', 'kw_obf_xss_onmouseover', 'kw_path_traversal_etc/passwd',
    'kw_obf_path_traversal_etc/passwd', 'kw_path_traversal_win.ini',
    'kw_obf_path_traversal_win.ini', 'kw_path_traversal_dotdot',
    'kw_obf_path_traversal_dotdot', 'kw_command_injection_cat',
    'kw_obf_command_injection_cat', 'kw_command_injection_ls',
    'kw_obf_command_injection_ls', 'kw_command_injection_wget',
    'kw_obf_command_injection_wget', 'kw_command_injection_curl',
    'kw_obf_command_injection_curl', 'kw_command_injection_bash',
    'kw_obf_command_injection_bash', 'path_dotdot_present', 'path_encoded_present',
    'length', 'word_count', 'special_char_ratio', 'digit_ratio', 'alpha_ratio',
    'char_60', 'char_62', 'char_34', 'char_39', 'char_59', 'char_47', 'char_92',
    'char_40', 'char_41', 'char_123', 'char_125', 'char_91', 'char_93'
]

# Global variables for models
detector = None
feature_extractor = None

def load_models():
    global detector, feature_extractor
    if detector is not None and feature_extractor is not None:
        return

    # Load the detector and feature extractor
    try:
        detector = joblib.load('waf_bypass_detector_complete.pkl')
        feature_extractor = joblib.load('waf_feature_extractor.pkl')
        detector.is_trained = True # Manually set to True as it's loaded
        print("Models loaded successfully: waf_bypass_detector_complete.pkl, waf_feature_extractor.pkl")
    except FileNotFoundError:
        print("Error: Model files not found. Make sure 'waf_bypass_detector_complete.pkl' and 'waf_feature_extractor.pkl' are in the same directory.")
        exit()
    except Exception as e:
        print(f"Error loading models: {e}")
        exit()

def predict_payload_kali(payload: str):
    """Predict whether a given payload is a WAF bypass attack or benign traffic."""

    print(f"\nAnalyzing payload: {payload}")

    # Ensure models are loaded
    if detector is None or feature_extractor is None:
        load_models()

    # Extract features
    features = feature_extractor.extract_all_features(payload)
    features_df = pd.DataFrame([features])

    # Align features_df columns with X_train_columns
    # Add missing columns with 0
    missing_cols = set(X_train_columns) - set(features_df.columns)
    for col in missing_cols:
        features_df[col] = 0

    # Ensure the order of columns is the same as during training
    features_df = features_df[X_train_columns]

    # Predict
    prediction, probability_array = detector.predict(features_df)
    # detector.predict returns prediction for each sample and probabilities for each class
    # We want the prediction (0 or 1) and the probability of being an attack (class 1)

    prediction_label = prediction[0] # 0 for benign, 1 for attack
    threat_probability = probability_array[0] # probability of being class 1 (attack)

    if prediction_label == 1:
        print(f"\n🚨 DETECTED: ATTACK/BYPASS | Confidence: {threat_probability*100:.2f}%")
    else:
        print(f"\n✅ BENIGN TRAFFIC | Confidence: {(1-threat_probability)*100:.2f}%")

    # Optional: print key features that contributed
    print("Key extracted features (non-zero):")
    for k, v in features.items():
        if v != 0 and k in features_df.columns and not k.startswith('char_'):
            print(f"  - {k}: {v}")

    return prediction_label, threat_probability

if __name__ == '__main__':
    load_models()
    print("\n--- Running Example Tests ---")
    # Example usage
    predict_payload_kali("GET /index.html HTTP/1.1") # Benign
    predict_payload_kali("admin' OR '1'='1' --") # SQLi
    predict_payload_kali("<script>alert('XSS')</script>") # XSS
    predict_payload_kali("GET /../../../etc/passwd HTTP/1.1") # Path Traversal
    predict_payload_kali("%253Cscript%253Ealert()%253C/script%253E") # Double Encoding Bypass
    predict_payload_kali("cat$u+/etc$u/passwd$u") # Command Injection
    predict_payload_kali("normal_user_input") # Another benign

    print("\n--- Kali Script Ready ---")
