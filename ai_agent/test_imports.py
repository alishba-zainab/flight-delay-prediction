"""
Test script to verify agent imports
Run this in your flight-delay-predictor folder
"""

import sys
import os

print("=" * 80)
print("TESTING AGENT IMPORTS")
print("=" * 80)

print(f"\nCurrent directory: {os.getcwd()}")
print(f"Python version: {sys.version}")
print(f"\nPython path:")
for path in sys.path:
    print(f"  - {path}")

print("\n" + "=" * 80)
print("TESTING IMPORTS")
print("=" * 80)

# Test 1: Check if file exists
print("\n1. Checking if file exists...")
if os.path.exists("final_ai_agent.py"):
    print("   ✅ File exists!")
    file_size = os.path.getsize("final_ai_agent.py")
    print(f"   File size: {file_size:,} bytes")
else:
    print("   ❌ File NOT found!")

# Test 2: Try to import
print("\n2. Trying to import final_ai_agent...")
try:
    import final_ai_agent
    print("   ✅ Module imported successfully!")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")

# Test 3: Try to import specific classes
print("\n3. Trying to import FlightDelayAgent class...")
try:
    from final_ai_agent import FlightDelayAgent
    print("   ✅ FlightDelayAgent imported!")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")

print("\n4. Trying to import AgentConfig class...")
try:
    from final_ai_agent import AgentConfig
    print("   ✅ AgentConfig imported!")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")

print("\n5. Trying to import RecommendationEngine class...")
try:
    from final_ai_agent import RecommendationEngine
    print("   ✅ RecommendationEngine imported!")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")

# Test 6: Try to create AgentConfig
print("\n6. Trying to create AgentConfig instance...")
try:
    from final_ai_agent import AgentConfig
    config = AgentConfig()
    print("   ✅ AgentConfig created successfully!")
    print(f"   Model path: {config.model_path}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 7: Check for missing dependencies
print("\n7. Checking dependencies...")
dependencies = ['xgboost', 'pandas', 'flask', 'flask_cors']
for dep in dependencies:
    try:
        __import__(dep)
        print(f"   ✅ {dep} installed")
    except ImportError:
        print(f"   ❌ {dep} NOT installed")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)