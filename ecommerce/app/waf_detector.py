import joblib
import pandas as pd
import numpy as np
import re
import os
from collections import Counter
import warnings

import sys

# Suppress warnings
warnings.filterwarnings('ignore')

# Fix for pickle deserialization:
# The models were pickled in a script where the classes were defined in '__main__'.
# We need to alias the current module to '__main__' so pickle can find the classes.
# However, we must be careful not to break the actual __main__ if this is imported.
# A safer way is to inject the classes into sys.modules['__main__'] if they are missing.


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
            'comment_injection': r'/\\*.*\\*/|--', 
            'comment_hash': r'#',
            'whitespace_abuse': r'[\\s\\t\\r\\n]{3,}',
            'null_bytes': r'%00',
            'null_bytes_hex': r'\\x00',
            'concatenation': r'\\+|\\|\\|',
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

        self.special_patterns = {
            'path_dotdot': r'\\.\\./[\\/\\\\]',
            'path_encoded': r'%2e%2e',
        }

    def extract_encoding_features(self, payload: str) -> dict:
        features = {}
        for name, pattern in self.encoding_patterns.items():
            matches = re.findall(pattern, payload, re.IGNORECASE)
            features[f'enc_{name}_count'] = len(matches)
            features[f'enc_{name}_present'] = int(len(matches) > 0)

        total_encodings = sum(1 for k, v in features.items() if 'present' in k and v > 0)
        features['enc_layers'] = total_encodings
        features['enc_multi_layer'] = int(total_encodings >= 2)
        return features

    def extract_obfuscation_features(self, payload: str) -> dict:
        features = {}
        for name, pattern in self.obfuscation_patterns.items():
            matches = re.findall(pattern, payload, re.IGNORECASE)
            features[f'obf_{name}_count'] = len(matches)

        if payload:
            char_freq = Counter(payload)
            total = len(payload)
            entropy = -sum((c/total) * np.log2(c/total) for c in char_freq.values())
            features['payload_entropy'] = entropy
        else:
            features['payload_entropy'] = 0

        has_alpha = bool(re.search(r'[a-zA-Z]', payload))
        has_digit = bool(re.search(r'[0-9]', payload))
        has_special = bool(re.search(r'[^a-zA-Z0-9\\s]', payload))
        features['charset_mixed'] = int(sum([has_alpha, has_digit, has_special]) >= 2)

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
        features = {}
        payload_lower = payload.lower()

        for attack_type, keywords in self.attack_keywords.items():
            for keyword in keywords:
                features[f'kw_{attack_type}_{keyword}'] = int(keyword in payload_lower)
                escaped_keyword = ''.join(['\\' + c if not c.isalnum() else c for c in keyword])
                obfusc_pattern = '.*'.join(list(escaped_keyword))
                features[f'kw_obf_{attack_type}_{keyword}'] = int(
                    bool(re.search(obfusc_pattern, payload_lower, re.IGNORECASE))
                )

        features['path_dotdot_present'] = int(bool(re.search(r'\\.\\./[\\/\\\\]', payload)))
        features['path_encoded_present'] = int(bool(re.search(r'%2e%2e', payload, re.IGNORECASE)))
        return features

    def extract_structural_features(self, payload: str) -> dict:
        features = {}
        features['length'] = len(payload)
        features['word_count'] = len(re.findall(r'\\w+', payload))
        features['special_char_ratio'] = sum(not c.isalnum() for c in payload) / max(len(payload), 1)
        features['digit_ratio'] = sum(c.isdigit() for c in payload) / max(len(payload), 1)
        features['alpha_ratio'] = sum(c.isalpha() for c in payload) / max(len(payload), 1)

        special_chars = ['<', '>', '"', "'", ';', '/', '\\', '(', ')', '{', '}', '[', ']']
        for char in special_chars:
            features[f'char_{ord(char)}'] = payload.count(char)
        return features

    def extract_all_features(self, payload: str) -> dict:
        features = {}
        if pd.isna(payload):
            payload = ""
        payload = str(payload)

        features.update(self.extract_encoding_features(payload))
        features.update(self.extract_obfuscation_features(payload))
        features.update(self.extract_attack_keywords(payload))
        features.update(self.extract_structural_features(payload))
        return features

class WAFBypassDetector:
    """Multi-stage detector for WAF bypasses"""
    def __init__(self):
        self.scaler = None
        self.anomaly_detector = None
        self.ensemble = None
        self.is_trained = False

    def predict(self, X):
        if not self.is_trained:
            pass 

        X_scaled = self.scaler.transform(X)
        anomaly_pred = self.anomaly_detector.predict(X_scaled)
        anomaly_flags = (anomaly_pred == -1).astype(int)
        ensemble_pred = self.ensemble.predict(X_scaled)
        ensemble_proba = self.ensemble.predict_proba(X_scaled)[:, 1]
        final_pred = np.maximum(anomaly_flags, ensemble_pred)
        return final_pred, ensemble_proba

class WAFEngine:
    def __init__(self, model_dir='.'):
        self.model_dir = model_dir
        self.detector = None
        self.feature_extractor = None
        self.X_train_columns = [
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
        self.load_models()

    def load_models(self):
        try:
            det_path = os.path.join(self.model_dir, 'waf_bypass_detector_complete.pkl')
            feat_path = os.path.join(self.model_dir, 'waf_feature_extractor.pkl')

            # Explicit import so pickle resolves correctly
            # We need to inject these into __main__ because the model was pickled that way
            import sys
            import app.waf_detector as current_module
            
            if not hasattr(sys.modules['__main__'], 'WAFBypassDetector'):
                sys.modules['__main__'].WAFBypassDetector = current_module.WAFBypassDetector
            if not hasattr(sys.modules['__main__'], 'WAFBypassFeatureExtractor'):
                sys.modules['__main__'].WAFBypassFeatureExtractor = current_module.WAFBypassFeatureExtractor

            self.detector = joblib.load(det_path)
            self.feature_extractor = joblib.load(feat_path)

            if not isinstance(self.detector, WAFBypassDetector):
                raise TypeError("Loaded detector is not WAFBypassDetector")

            self.detector.is_trained = True
            print(f"[WAF] Models loaded successfully from {self.model_dir}", flush=True)

        except Exception as e:
            print(f"[WAF] Model loading failed: {e}", flush=True)
            self.detector = None
            self.feature_extractor = None

    def analyze(self, payload: str):
        if not self.detector or not self.feature_extractor:
            return {'is_attack': False, 'confidence': 0.0, 'error': 'Models not loaded'}

        try:
            features = self.feature_extractor.extract_all_features(payload)
            features_df = pd.DataFrame([features])

            missing_cols = set(self.X_train_columns) - set(features_df.columns)
            for col in missing_cols:
                features_df[col] = 0

            features_df = features_df[self.X_train_columns]
            
            prediction, probability_array = self.detector.predict(features_df)
            
            is_attack = bool(prediction[0] == 1)
            confidence = float(probability_array[0])
            
            return {
                'is_attack': is_attack,
                'confidence': confidence,
                'features': features
            }
        except Exception as e:
            print(f"WAF Analysis Error: {e}")
            return {'is_attack': False, 'confidence': 0.0, 'error': str(e)}
