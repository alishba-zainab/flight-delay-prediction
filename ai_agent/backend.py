"""
Flask Backend API for Flight Delay Prediction System - FIXED VERSION
Connects React frontend with Python agent
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sys
import os
import re
import logging

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Import your flight delay agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from final_ai_agent import FlightDelayAgent, AgentConfig, RecommendationEngine
    from flight_api import get_flight_data
    from weather_api import get_weather_data
    from data_adapter import adapt_flight_data
    from feature_mapper import map_features_for_prediction

    agent_modules_loaded = True
    print("✅ Agent modules imported successfully")
except ImportError as e:
    print(f"⚠️  Warning: Could not import modules: {e}")
    print("📋 Running in MOCK MODE - using test data")
    agent_modules_loaded = False


    # FIXED: Complete AgentConfig for mock mode
    class AgentConfig:
        def __init__(self):
            self.model_path = 'xgboost_flight_delay.json'
            self.check_interval_minutes = 30
            self.max_retries = 3
            self.api_timeout = 10
            self.cache_duration_minutes = 5
            self.max_monitored_flights = 10
            self.log_level = 'INFO'
            self.log_file = 'flight_agent.log'
            self.enable_cache = True
            self.enable_recommendations = True
            self.recommendation_min_confidence = 0.6


    # FIXED: Complete MockAgent with all required attributes and methods
    class MockRecommendationEngine:
        """Mock recommendation engine"""

        def generate_recommendations(self, flight_data, prediction_result, weather_data):
            """Generate mock recommendations"""
            delay_prob = prediction_result.get('delay_probability', 0.5)

            recommendations = [
                {
                    'type': 'INFO',
                    'category': 'Status',
                    'priority': 2,
                    'title': 'Mock Mode Active',
                    'message': 'Running in test mode. Real recommendations unavailable.',
                    'actionable': False
                }
            ]

            if delay_prob > 0.6:
                recommendations.append({
                    'type': 'WARNING',
                    'category': 'Monitoring',
                    'priority': 1,
                    'title': 'High Delay Risk',
                    'message': 'This flight has elevated delay probability.',
                    'actionable': True,
                    'action': 'Monitor flight status closely'
                })

            return recommendations

        def get_delay_mitigation_strategies(self, delay_prob):
            """Get mock mitigation strategies"""
            return [
                {
                    'title': 'Monitor Status',
                    'description': 'Check flight status regularly',
                    'effectiveness': 'HIGH'
                }
            ]

        def get_proactive_tips(self):
            """Get mock proactive tips"""
            return [
                "✈️ Check in online 24 hours before departure",
                "📱 Download airline app for updates",
                "⏰ Arrive at airport early"
            ]


    class MockAgent:
        """FIXED: Complete mock agent with all required attributes"""

        def __init__(self, config=None):
            self.config = config or AgentConfig()

            # FIXED: Add all required attributes
            self.prediction_history = []
            self.monitored_flights = []
            self.recommendation_engine = MockRecommendationEngine()

            # FIXED: Add logger
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)

            self.logger.info("✅ Mock agent initialized")

        def perceive(self, flight_number):
            """Mock flight data"""
            import random

            # Generate realistic mock data
            airlines = ['American Airlines', 'Delta', 'United', 'Southwest']
            airports = [
                ('JFK', 40.6413, -73.7781),
                ('LAX', 33.9416, -118.4085),
                ('ORD', 41.9742, -87.9073),
                ('DFW', 32.8998, -97.0403)
            ]

            origin = random.choice(airports)
            dest = random.choice([a for a in airports if a != origin])

            return {
                'flight_data': {
                    'airline': random.choice(airlines),
                    'origin': origin[0],
                    'destination': dest[0],
                    'departure_latitude': origin[1],
                    'departure_longitude': origin[2],
                    'arrival_latitude': dest[1],
                    'arrival_longitude': dest[2]
                },
                'origin_weather': {
                    'temperature_c': random.randint(15, 30),
                    'humidity_percent': random.randint(40, 80),
                    'pressure_hPa': random.randint(980, 1020)
                },
                'complete_data': {
                    'month': datetime.now().month,
                    'day_of_month': datetime.now().day,
                    'crs_dep_time': random.randint(600, 2200),
                    'distance': random.randint(500, 3000),
                    'temperature_c': random.randint(15, 30),
                    'humidity_percent': random.randint(40, 80),
                    'pressure_hPa': random.randint(980, 1020)
                },
                'timestamp': datetime.now()
            }

        def reason(self, perceived_data):
            """Mock prediction"""
            import random
            delay_prob = random.uniform(0.15, 0.85)

            if abs(delay_prob - 0.5) > 0.3:
                confidence = 'HIGH'
            elif abs(delay_prob - 0.5) > 0.15:
                confidence = 'MODERATE'
            else:
                confidence = 'LOW'

            return {
                'prediction': 'DELAYED' if delay_prob > 0.5 else 'ON_TIME',
                'delay_probability': delay_prob,
                'on_time_probability': 1 - delay_prob,
                'confidence': confidence,
                'timestamp': datetime.now()
            }

        # FIXED: Add missing methods
        def add_flight(self, flight_number):
            """Add flight to monitoring list"""
            if any(f['flight_number'] == flight_number for f in self.monitored_flights):
                return False

            if len(self.monitored_flights) >= self.config.max_monitored_flights:
                return False

            self.monitored_flights.append({
                'flight_number': flight_number,
                'added_at': datetime.now(),
                'last_checked': None,
                'check_count': 0,
                'last_prediction': None,
                'error_count': 0
            })
            return True

        def remove_flight(self, flight_number):
            """Remove flight from monitoring list"""
            initial_count = len(self.monitored_flights)
            self.monitored_flights = [f for f in self.monitored_flights if f['flight_number'] != flight_number]
            return len(self.monitored_flights) < initial_count


    FlightDelayAgent = MockAgent

# Configuration from environment variables
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
API_PORT = int(os.getenv('API_PORT', '5000'))
API_HOST = os.getenv('API_HOST', '0.0.0.0' if DEBUG_MODE else '127.0.0.1')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001').split(',')

app = Flask(__name__)

# FIXED: Configure CORS from environment variables
CORS(app, resources={
    r"/api/*": {
        "origins": CORS_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})


# FIXED: Add utility functions
def validate_flight_number(flight_number):
    """
    Validate flight number format

    Args:
        flight_number (str): Flight number to validate

    Returns:
        bool: True if valid format
    """
    if not flight_number:
        return False

    # Pattern: 2-3 letters + 1-4 digits (e.g., AA100, DL1234, UAL456)
    pattern = r'^[A-Z]{1,3}[0-9]{1,4}$'
    return re.match(pattern, flight_number.strip().upper()) is not None


def safe_log_error(agent, message, exc_info=True):
    """
    Safely log errors even if logger doesn't exist

    Args:
        agent: Agent instance
        message (str): Error message
        exc_info (bool): Include exception info
    """
    if hasattr(agent, 'logger') and agent.logger:
        agent.logger.error(message, exc_info=exc_info)
    else:
        print(f"ERROR: {message}")
        if exc_info:
            import traceback
            traceback.print_exc()


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist. Check /api/health for available endpoints.'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please try again later.'
    }), 500


# Initialize the agent
try:
    config = AgentConfig()
    agent = FlightDelayAgent(config=config)
    print("✅ Flight Delay Agent initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize agent: {e}")
    agent = None


@app.route('/')
def index():
    """Root endpoint - API information"""
    return jsonify({
        'name': 'Flight Delay Prediction API',
        'version': '1.0.0',
        'status': 'running',
        'mode': 'mock' if not agent_modules_loaded else 'production',
        'endpoints': {
            'health': '/api/health',
            'test': '/api/test',
            'predict': '/api/predict',
            'recommendations': '/api/recommendations',
            'proactive_tips': '/api/proactive-tips',
            'history': '/api/history',
            'monitor_add': '/api/monitor/add',
            'monitor_remove': '/api/monitor/remove',
            'monitor_list': '/api/monitor/list'
        },
        'documentation': 'See REACT_FRONTEND_SETUP.md for full API documentation'
    })


@app.route('/favicon.ico')
def favicon():
    """Favicon handler to prevent 404 errors"""
    return '', 204


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'agent_ready': agent is not None,
        'mode': 'mock' if not agent_modules_loaded else 'production',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint"""
    return jsonify({
        'success': True,
        'message': 'Backend API is working correctly!',
        'mode': 'mock' if not agent_modules_loaded else 'production',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/predict', methods=['POST'])
def predict_flight():
    """
    Predict flight delay

    Request body:
    {
        "flight_number": "AA100"
    }

    Response:
    {
        "success": true,
        "data": {
            "flight_number": "AA100",
            "airline": "American Airlines",
            "route": "LAX → JFK",
            "departure_time": "14:30",
            "date": "12/24/2025",
            "delay_probability": 0.68,
            "confidence": "HIGH",
            "weather": {
                "temperature": 18,
                "humidity": 65,
                "pressure": 1013
            },
            "distance": 2475
        }
    }
    """
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Agent not initialized'
        }), 500

    try:
        data = request.json

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400

        flight_number = data.get('flight_number', '').strip().upper()

        if not flight_number:
            return jsonify({
                'success': False,
                'error': 'Flight number is required'
            }), 400

        # FIXED: Validate flight number format
        if not validate_flight_number(flight_number):
            return jsonify({
                'success': False,
                'error': 'Invalid flight number format. Expected format: AA100, DL123, etc.'
            }), 400

        # Use agent's perceive and reason methods
        perceived_data = agent.perceive(flight_number)

        if not perceived_data:
            return jsonify({
                'success': False,
                'error': 'Could not retrieve flight data. Flight may not exist or data is unavailable.'
            }), 404

        reasoning_result = agent.reason(perceived_data)

        if not reasoning_result:
            return jsonify({
                'success': False,
                'error': 'Could not analyze flight data'
            }), 500

        # Extract data for response
        flight_data = perceived_data['flight_data']
        complete_data = perceived_data['complete_data']
        origin_weather = perceived_data['origin_weather']

        response_data = {
            'flight_number': flight_number,
            'airline': flight_data.get('airline', 'Unknown'),
            'origin': flight_data.get('origin', 'N/A'),
            'destination': flight_data.get('destination', 'N/A'),
            'route': f"{flight_data.get('origin', 'N/A')} → {flight_data.get('destination', 'N/A')}",
            'departure_time': f"{complete_data.get('crs_dep_time', 0) // 100:02d}:{complete_data.get('crs_dep_time', 0) % 100:02d}",
            'date': f"{complete_data.get('month', 'N/A')}/{complete_data.get('day_of_month', 'N/A')}",
            'delay_probability': reasoning_result['delay_probability'],
            'on_time_probability': reasoning_result['on_time_probability'],
            'confidence': reasoning_result['confidence'],
            'prediction': reasoning_result['prediction'],
            'weather': {
                'temperature': complete_data.get('temperature_c', 'N/A'),
                'humidity': complete_data.get('humidity_percent', 'N/A'),
                'pressure': complete_data.get('pressure_hPa', 'N/A')
            },
            'distance': complete_data.get('distance', 'N/A'),
            'mode': 'mock' if not agent_modules_loaded else 'production'
        }

        # Add to history
        agent.prediction_history.append({
            'flight_number': flight_number,
            'timestamp': perceived_data['timestamp'],
            'prediction': reasoning_result['prediction'],
            'probability': reasoning_result['delay_probability'],
            'confidence': reasoning_result['confidence'],
            'action_taken': 'API_PREDICTION',
            'flight_info': flight_data
        })

        return jsonify({
            'success': True,
            'data': response_data
        })

    except Exception as e:
        # FIXED: Use safe logging
        safe_log_error(agent, f"Error in predict endpoint: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """
    Get recommendations for a flight

    Request body:
    {
        "flight_number": "AA100"
    }

    Response:
    {
        "success": true,
        "recommendations": [...]
    }
    """
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Agent not initialized'
        }), 500

    try:
        data = request.json

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400

        flight_number = data.get('flight_number', '').strip().upper()

        if not flight_number:
            return jsonify({
                'success': False,
                'error': 'Flight number is required'
            }), 400

        # FIXED: Validate flight number format
        if not validate_flight_number(flight_number):
            return jsonify({
                'success': False,
                'error': 'Invalid flight number format'
            }), 400

        # Get flight data
        perceived_data = agent.perceive(flight_number)

        if not perceived_data:
            return jsonify({
                'success': False,
                'error': 'Could not retrieve flight data'
            }), 404

        reasoning_result = agent.reason(perceived_data)

        if not reasoning_result:
            return jsonify({
                'success': False,
                'error': 'Could not analyze flight data'
            }), 500

        # FIXED: Safe access to recommendation_engine
        if hasattr(agent, 'recommendation_engine'):
            # Generate recommendations
            recommendations = agent.recommendation_engine.generate_recommendations(
                perceived_data['flight_data'],
                reasoning_result,
                perceived_data['origin_weather']
            )

            # Get mitigation strategies
            strategies = []
            if reasoning_result['delay_probability'] >= 0.4:
                strategies = agent.recommendation_engine.get_delay_mitigation_strategies(
                    reasoning_result['delay_probability']
                )
        else:
            # Fallback if recommendation engine not available
            recommendations = [{
                'type': 'INFO',
                'category': 'Status',
                'priority': 3,
                'title': 'Recommendations Unavailable',
                'message': 'Recommendation engine not available in current mode',
                'actionable': False
            }]
            strategies = []

        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'strategies': strategies
        })

    except Exception as e:
        # FIXED: Use safe logging
        safe_log_error(agent, f"Error in recommendations endpoint: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/proactive-tips', methods=['GET'])
def get_proactive_tips():
    """
    Get general proactive travel tips

    Response:
    {
        "success": true,
        "tips": ["tip1", "tip2", ...]
    }
    """
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Agent not initialized'
        }), 500

    try:
        # FIXED: Safe access to recommendation_engine
        if hasattr(agent, 'recommendation_engine'):
            tips = agent.recommendation_engine.get_proactive_tips()
        else:
            tips = [
                "✈️ Check in online 24 hours before departure",
                "📱 Download airline app for updates",
                "⏰ Arrive at airport early",
                "🎫 Save boarding pass screenshots",
                "🔋 Bring portable chargers"
            ]

        return jsonify({
            'success': True,
            'tips': tips
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Get prediction history

    Response:
    {
        "success": true,
        "history": [...]
    }
    """
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Agent not initialized'
        }), 500

    try:
        # FIXED: Safe access to prediction_history
        if hasattr(agent, 'prediction_history'):
            # Get last 20 predictions
            history = agent.prediction_history[-20:]
        else:
            history = []

        # Format for frontend
        formatted_history = []
        for pred in history:
            formatted_history.append({
                'flight_number': pred['flight_number'],
                'timestamp': pred['timestamp'].isoformat() if hasattr(pred['timestamp'], 'isoformat') else str(
                    pred['timestamp']),
                'prediction': pred['prediction'],
                'probability': pred['probability'],
                'confidence': pred['confidence']
            })

        return jsonify({
            'success': True,
            'history': formatted_history
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/monitor/add', methods=['POST'])
def add_to_monitor():
    """
    Add flight to monitoring list

    Request body:
    {
        "flight_number": "AA100"
    }
    """
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Agent not initialized'
        }), 500

    try:
        data = request.json

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400

        flight_number = data.get('flight_number', '').strip().upper()

        if not flight_number:
            return jsonify({
                'success': False,
                'error': 'Flight number is required'
            }), 400

        # FIXED: Validate flight number format
        if not validate_flight_number(flight_number):
            return jsonify({
                'success': False,
                'error': 'Invalid flight number format'
            }), 400

        # FIXED: Safe method call
        if hasattr(agent, 'add_flight'):
            success = agent.add_flight(flight_number)
        else:
            return jsonify({
                'success': False,
                'error': 'Monitoring not available in current mode'
            }), 503

        return jsonify({
            'success': success,
            'message': f'Flight {flight_number} added to monitoring' if success else f'Flight {flight_number} already being monitored'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/monitor/remove', methods=['POST'])
def remove_from_monitor():
    """
    Remove flight from monitoring list

    Request body:
    {
        "flight_number": "AA100"
    }
    """
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Agent not initialized'
        }), 500

    try:
        data = request.json

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400

        flight_number = data.get('flight_number', '').strip().upper()

        if not flight_number:
            return jsonify({
                'success': False,
                'error': 'Flight number is required'
            }), 400

        # FIXED: Safe method call
        if hasattr(agent, 'remove_flight'):
            success = agent.remove_flight(flight_number)
        else:
            return jsonify({
                'success': False,
                'error': 'Monitoring not available in current mode'
            }), 503

        return jsonify({
            'success': success,
            'message': f'Flight {flight_number} removed from monitoring' if success else f'Flight {flight_number} was not being monitored'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/monitor/list', methods=['GET'])
def list_monitored():
    """
    Get list of monitored flights

    Response:
    {
        "success": true,
        "flights": [...]
    }
    """
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Agent not initialized'
        }), 500

    try:
        # FIXED: Safe access to monitored_flights
        if hasattr(agent, 'monitored_flights'):
            flights = []
            for flight in agent.monitored_flights:
                flights.append({
                    'flight_number': flight['flight_number'],
                    'added_at': flight['added_at'].isoformat() if hasattr(flight['added_at'], 'isoformat') else str(
                        flight['added_at']),
                    'check_count': flight.get('check_count', 0),
                    'last_checked': flight.get('last_checked').isoformat() if flight.get('last_checked') and hasattr(
                        flight.get('last_checked'), 'isoformat') else None,
                    'last_prediction': flight.get('last_prediction')
                })
        else:
            flights = []

        return jsonify({
            'success': True,
            'flights': flights
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🚀 Starting Flight Delay Prediction API Server")
    print("=" * 80)
    print(f"\n📋 Mode: {'MOCK (Test Data)' if not agent_modules_loaded else 'PRODUCTION (Real Data)'}")
    print(f"🔧 Debug: {'Enabled' if DEBUG_MODE else 'Disabled'}")
    print(f"🌐 Host: {API_HOST}")
    print(f"🔌 Port: {API_PORT}")
    print("\n📋 Available Endpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/test                - Test endpoint")
    print("  POST /api/predict             - Predict flight delay")
    print("  POST /api/recommendations     - Get recommendations")
    print("  GET  /api/proactive-tips      - Get travel tips")
    print("  GET  /api/history             - Get prediction history")
    print("  POST /api/monitor/add         - Add flight to monitoring")
    print("  POST /api/monitor/remove      - Remove flight from monitoring")
    print("  GET  /api/monitor/list        - List monitored flights")
    print(f"\n🌐 Server running on http://{API_HOST}:{API_PORT}")
    print("=" * 80 + "\n")

    # FIXED: Use proper production settings
    if DEBUG_MODE:
        print("⚠️  WARNING: Running in DEBUG mode - not suitable for production!")
        print("   Set DEBUG_MODE=False in environment variables for production\n")

    app.run(debug=DEBUG_MODE, host=API_HOST, port=API_PORT)