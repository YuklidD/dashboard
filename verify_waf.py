import sys
import os
import logging

# Add app directory to path
sys.path.append(os.path.join(os.getcwd(), 'ecommerce', 'app'))

# Mock environment variables
os.environ['MODEL_DIR'] = os.path.join(os.getcwd(), 'ecommerce', 'models')

try:
    from ecommerce.app.waf_detector import WAFEngine
    
    print("Initializing WAF Engine...")
    waf = WAFEngine(model_dir=os.environ['MODEL_DIR'])
    
    if not waf.detector:
        print("FAILED: Model could not be loaded.")
        sys.exit(1)
        
    print("SUCCESS: Model loaded.")
    
    # Test Cases
    payloads = [
        ("Hello World", False),
        ("SELECT * FROM users", True),
        ("<script>alert(1)</script>", True),
        ("admin' OR '1'='1", True),
        ("/etc/passwd", True),
        ("Just a normal search query", False)
    ]
    
    print("\nRunning Predictions:")
    print("-" * 50)
    print(f"{'Payload':<30} | {'Expected':<10} | {'Actual':<10} | {'Confidence':<10}")
    print("-" * 50)
    
    for payload, expected in payloads:
        result = waf.analyze(payload)
        is_attack = result['is_attack']
        confidence = result.get('confidence', 0.0)
        
        status = "PASS" if is_attack == expected else "FAIL"
        print(f"{payload[:27]:<30} ... | {str(expected):<10} | {str(is_attack):<10} | {confidence:.4f}")

except ImportError as e:
    print(f"ImportError: {e}")
    print("Please ensure requirements are installed: pip install -r ecommerce/requirements.txt")
except Exception as e:
    print(f"An error occurred: {e}")
