"""
Enhanced Flight Delay Prediction System with Advanced Recommendations
Production-Ready Agentic AI with Intelligent Recommendation Engine
"""

import sys
import os

# Fix encoding issues on Windows - IMPROVED VERSION
if sys.platform.startswith('win'):
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    except Exception as e:
        try:
            import codecs

            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
        except:
            print("Warning: UTF-8 encoding setup failed. Emojis may not display correctly.")
            os.environ['USE_ASCII_ONLY'] = '1'

import time
import json
import re
import logging
import signal
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
from pathlib import Path
from collections import defaultdict

try:
    import xgboost as xgb
    import pandas as pd
except ImportError:
    print("Warning: xgboost or pandas not installed. Install with: pip install xgboost pandas")

# Import your existing modules
try:
    from flight_api import get_flight_data
    from weather_api import get_weather_data
    from data_adapter import adapt_flight_data
    from feature_mapper import map_features_for_prediction
except ImportError:
    print("Warning: Some modules not found. Mock implementations will be used for demo.")


    def get_flight_data(flight_number):
        return None


    def get_weather_data(lat, lon):
        return None


    def adapt_flight_data(flight_data, origin_weather, dest_weather):
        return {}


    def map_features_for_prediction(data, features):
        return None


# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

@dataclass
class AgentConfig:
    """Configuration for Flight Delay Agent"""
    model_path: str = 'xgboost_flight_delay.json'
    check_interval_minutes: int = 30
    max_retries: int = 3
    api_timeout: int = 10
    cache_duration_minutes: int = 5
    max_monitored_flights: int = 10
    log_level: str = 'INFO'
    log_file: str = 'flight_agent.log'
    enable_cache: bool = True
    enable_recommendations: bool = True
    recommendation_min_confidence: float = 0.6

    @classmethod
    def from_file(cls, filepath: str) -> 'AgentConfig':
        """Load config from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except FileNotFoundError:
            logging.warning(f"Config file {filepath} not found, using defaults")
            return cls()

    def to_file(self, filepath: str):
        """Save config to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=2)


# ============================================================================
# RECOMMENDATION ENGINE
# ============================================================================

class RecommendationEngine:
    """
    Intelligent recommendation system for flight delay mitigation
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.airline_reliability = defaultdict(list)
        self.route_statistics = defaultdict(list)
        self.time_slot_statistics = defaultdict(list)

    def generate_recommendations(self, flight_data: Dict, prediction_result: Dict,
                                 weather_data: Dict) -> List[Dict]:
        """
        Generate intelligent recommendations based on prediction

        Args:
            flight_data: Flight information
            prediction_result: ML prediction results
            weather_data: Weather conditions

        Returns:
            List of recommendations with priority and actionability
        """
        recommendations = []

        delay_prob = prediction_result['delay_probability']
        confidence = prediction_result['confidence']

        # Only generate recommendations for high-confidence predictions
        if confidence == 'LOW':
            recommendations.append({
                'type': 'INFO',
                'category': 'Prediction Quality',
                'priority': 3,
                'title': 'Low Confidence Prediction',
                'message': 'Prediction confidence is low. Consider checking again closer to departure.',
                'actionable': False
            })
            return recommendations

        # High delay risk recommendations
        if delay_prob >= 0.75:
            recommendations.extend(self._get_high_risk_recommendations(
                flight_data, prediction_result, weather_data
            ))

        # Moderate delay risk recommendations
        elif delay_prob >= 0.45:
            recommendations.extend(self._get_moderate_risk_recommendations(
                flight_data, prediction_result, weather_data
            ))

        # Low delay risk recommendations
        else:
            recommendations.extend(self._get_low_risk_recommendations(
                flight_data, prediction_result, weather_data
            ))

        # Weather-based recommendations
        recommendations.extend(self._get_weather_recommendations(
            weather_data, flight_data
        ))

        # Time-based recommendations
        recommendations.extend(self._get_time_based_recommendations(
            flight_data, delay_prob
        ))

        # Alternative flight suggestions
        if delay_prob >= 0.65:
            recommendations.extend(self._get_alternative_flight_recommendations(
                flight_data, delay_prob
            ))

        # Sort by priority (1 = highest)
        recommendations.sort(key=lambda x: x['priority'])

        return recommendations

    def _get_high_risk_recommendations(self, flight_data: Dict,
                                       prediction_result: Dict,
                                       weather_data: Dict) -> List[Dict]:
        """Recommendations for high delay risk"""
        recs = []

        recs.append({
            'type': 'CRITICAL',
            'category': 'Rebooking',
            'priority': 1,
            'title': 'Consider Rebooking',
            'message': 'This flight has very high delay probability. Consider rebooking to an earlier or alternative flight.',
            'actionable': True,
            'action': 'Search for alternative flights on the same route'
        })

        recs.append({
            'type': 'ALERT',
            'category': 'Travel Planning',
            'priority': 1,
            'title': 'Allow Extra Time',
            'message': 'If you must take this flight, arrive at airport early and have contingency plans for connections.',
            'actionable': True,
            'action': 'Adjust your schedule to accommodate potential delays'
        })

        recs.append({
            'type': 'ALERT',
            'category': 'Connections',
            'priority': 1,
            'title': 'Connection Risk',
            'message': 'If you have a tight connection, consider rebooking with a longer layover.',
            'actionable': True,
            'action': 'Contact airline to rebook connection flights'
        })

        recs.append({
            'type': 'INFO',
            'category': 'Insurance',
            'priority': 2,
            'title': 'Travel Insurance',
            'message': 'Consider purchasing travel insurance if you haven\'t already.',
            'actionable': True,
            'action': 'Review travel insurance options'
        })

        return recs

    def _get_moderate_risk_recommendations(self, flight_data: Dict,
                                           prediction_result: Dict,
                                           weather_data: Dict) -> List[Dict]:
        """Recommendations for moderate delay risk"""
        recs = []

        recs.append({
            'type': 'WARNING',
            'category': 'Monitoring',
            'priority': 2,
            'title': 'Monitor Closely',
            'message': 'Keep checking flight status regularly. Set up airline app notifications.',
            'actionable': True,
            'action': 'Download airline app and enable push notifications'
        })

        recs.append({
            'type': 'INFO',
            'category': 'Check-in',
            'priority': 2,
            'title': 'Early Check-in',
            'message': 'Check in as early as possible to have priority in case of rebooking.',
            'actionable': True,
            'action': 'Check in online 24 hours before departure'
        })

        recs.append({
            'type': 'INFO',
            'category': 'Airport',
            'priority': 3,
            'title': 'Arrive Early',
            'message': 'Consider arriving at the airport 30 minutes earlier than usual.',
            'actionable': True,
            'action': 'Adjust your airport arrival time'
        })

        return recs

    def _get_low_risk_recommendations(self, flight_data: Dict,
                                      prediction_result: Dict,
                                      weather_data: Dict) -> List[Dict]:
        """Recommendations for low delay risk"""
        recs = []

        recs.append({
            'type': 'SUCCESS',
            'category': 'Status',
            'priority': 3,
            'title': 'Flight Looks Good',
            'message': 'Your flight has low delay probability. Standard arrival time recommended.',
            'actionable': False
        })

        recs.append({
            'type': 'INFO',
            'category': 'Monitoring',
            'priority': 3,
            'title': 'Routine Check',
            'message': 'Check flight status 2-3 hours before departure as a routine precaution.',
            'actionable': True,
            'action': 'Set reminder to check status before leaving'
        })

        return recs

    def _get_weather_recommendations(self, weather_data: Dict,
                                     flight_data: Dict) -> List[Dict]:
        """Weather-specific recommendations"""
        recs = []

        if not weather_data:
            return recs

        # Check temperature (extreme cold/heat can cause delays)
        temp = weather_data.get('temperature_c', 20)
        if temp < -10:
            recs.append({
                'type': 'WARNING',
                'category': 'Weather',
                'priority': 2,
                'title': 'Extreme Cold Weather',
                'message': f'Origin temperature is {temp}°C. De-icing procedures may cause delays.',
                'actionable': True,
                'action': 'Allow extra time for weather-related procedures'
            })
        elif temp > 38:
            recs.append({
                'type': 'WARNING',
                'category': 'Weather',
                'priority': 2,
                'title': 'Extreme Heat',
                'message': f'Origin temperature is {temp}°C. Heat-related operational delays possible.',
                'actionable': True,
                'action': 'Stay hydrated and monitor flight status'
            })

        # Check humidity (fog risk)
        humidity = weather_data.get('humidity_percent', 50)
        if humidity > 90 and temp < 15:
            recs.append({
                'type': 'INFO',
                'category': 'Weather',
                'priority': 2,
                'title': 'Fog Risk',
                'message': 'High humidity with low temperature may cause fog and visibility issues.',
                'actionable': True,
                'action': 'Monitor weather conditions and flight status'
            })

        # Check pressure (storm indicator)
        pressure = weather_data.get('pressure_hPa', 1013)
        if pressure < 980:
            recs.append({
                'type': 'WARNING',
                'category': 'Weather',
                'priority': 1,
                'title': 'Low Pressure System',
                'message': 'Low atmospheric pressure detected. Potential for storm activity.',
                'actionable': True,
                'action': 'Check weather forecasts and consider earlier flights'
            })

        return recs

    def _get_time_based_recommendations(self, flight_data: Dict,
                                        delay_prob: float) -> List[Dict]:
        """Time-of-day specific recommendations"""
        recs = []

        dep_time = flight_data.get('crs_dep_time', 0)
        hour = dep_time // 100 if dep_time else 12

        # Early morning flights (5 AM - 7 AM)
        if 5 <= hour < 7:
            if delay_prob < 0.4:
                recs.append({
                    'type': 'SUCCESS',
                    'category': 'Time Advantage',
                    'priority': 3,
                    'title': 'Early Morning Advantage',
                    'message': 'Early morning flights typically have fewer delays due to less air traffic.',
                    'actionable': False
                })

        # Late evening flights (9 PM - midnight)
        elif hour >= 21 or hour < 1:
            if delay_prob > 0.5:
                recs.append({
                    'type': 'INFO',
                    'category': 'Time Factor',
                    'priority': 2,
                    'title': 'Cascading Delays',
                    'message': 'Late flights are more prone to delays accumulated throughout the day.',
                    'actionable': True,
                    'action': 'Consider booking earlier flights in the future'
                })

        # Peak travel times (7 AM - 9 AM, 5 PM - 7 PM)
        elif (7 <= hour < 9) or (17 <= hour < 19):
            recs.append({
                'type': 'INFO',
                'category': 'Time Factor',
                'priority': 3,
                'title': 'Peak Travel Time',
                'message': 'This is a peak travel time. Airport may be busier than usual.',
                'actionable': True,
                'action': 'Arrive at airport early to account for crowds'
            })

        return recs

    def _get_alternative_flight_recommendations(self, flight_data: Dict,
                                                delay_prob: float) -> List[Dict]:
        """Suggest alternative strategies"""
        recs = []

        airline = flight_data.get('airline', '')
        origin = flight_data.get('origin', '')
        dest = flight_data.get('destination', '')

        recs.append({
            'type': 'INFO',
            'category': 'Alternatives',
            'priority': 2,
            'title': 'Check Other Airlines',
            'message': f'Search for flights on other airlines operating the {origin}-{dest} route.',
            'actionable': True,
            'action': f'Compare flights from different carriers on {origin} to {dest}'
        })

        recs.append({
            'type': 'INFO',
            'category': 'Alternatives',
            'priority': 2,
            'title': 'Earlier Flights',
            'message': 'Earlier flights on the same day typically have lower delay probability.',
            'actionable': True,
            'action': 'Search for earlier departure times'
        })

        # Suggest connecting flights for long delays
        if delay_prob > 0.80:
            recs.append({
                'type': 'INFO',
                'category': 'Alternatives',
                'priority': 2,
                'title': 'Consider Connections',
                'message': 'A connecting flight through a major hub might be more reliable.',
                'actionable': True,
                'action': f'Search for connecting flights via major hubs'
            })

        return recs

    def get_proactive_tips(self) -> List[str]:
        """Get general proactive travel tips"""
        return [
            "✈️ Always check in online 24 hours before departure for priority boarding",
            "📱 Download your airline's mobile app for real-time updates",
            "🎫 Take screenshots of boarding passes in case of connectivity issues",
            "⏰ Set multiple alarms for early morning flights",
            "🔋 Bring portable chargers to stay connected during delays",
            "🍽️ Eat before the airport - airport food is expensive",
            "💺 Know your passenger rights for compensation on long delays",
            "📞 Save airline customer service number in your contacts",
            "🧳 Pack essentials in carry-on in case of baggage delays",
            "🗺️ Research airport layout in advance for quick connections"
        ]

    def get_delay_mitigation_strategies(self, delay_prob: float) -> List[Dict]:
        """Get strategies to mitigate delay impact"""
        strategies = []

        if delay_prob >= 0.7:
            strategies.append({
                'title': 'Proactive Rebooking',
                'description': 'Call airline before delay is announced to get ahead of rebooking queue',
                'effectiveness': 'HIGH'
            })
            strategies.append({
                'title': 'Airport Lounge Access',
                'description': 'Purchase day pass to airport lounge for comfortable delay waiting',
                'effectiveness': 'MEDIUM'
            })
            strategies.append({
                'title': 'Hotel Backup',
                'description': 'Research nearby airport hotels with cancellation flexibility',
                'effectiveness': 'HIGH'
            })

        if delay_prob >= 0.5:
            strategies.append({
                'title': 'Flexible Timing',
                'description': 'Build buffer time into your schedule for meetings/events',
                'effectiveness': 'HIGH'
            })
            strategies.append({
                'title': 'Travel Insurance',
                'description': 'Ensure travel insurance covers delays and missed connections',
                'effectiveness': 'MEDIUM'
            })

        strategies.append({
            'title': 'Status Monitoring',
            'description': 'Set up automated flight status alerts via SMS/email',
            'effectiveness': 'HIGH'
        })

        return strategies


# ============================================================================
# INTENT PATTERNS (Enhanced with Recommendations)
# ============================================================================

INTENT_PATTERNS = {
    'greeting': {
        'patterns': ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening', 'howdy',
                     'hola'],
        'priority': 1,
        'requires_flight': False
    },
    'help': {
        'patterns': ['help', 'what can you do', 'capabilities', 'features', 'how to use', 'guide', 'instructions',
                     'commands'],
        'priority': 2,
        'requires_flight': False
    },
    'check_flight': {
        'patterns': ['check', 'predict', 'status', 'delay', 'delayed', 'will it be delayed', 'is it delayed', 'analyze',
                     'tell me about', 'information', 'gonna be late'],
        'priority': 3,
        'requires_flight': True
    },
    'get_recommendations': {
        'patterns': ['recommend', 'recommendation', 'suggest', 'advice', 'what should i do', 'tips', 'help me',
                     'guidance'],
        'priority': 3,
        'requires_flight': True
    },
    'alternatives': {
        'patterns': ['alternative', 'other flights', 'different flight', 'better option', 'other options'],
        'priority': 3,
        'requires_flight': True
    },
    'proactive_tips': {
        'patterns': ['tips', 'best practices', 'advice', 'suggestions', 'how to prepare', 'what to bring'],
        'priority': 2,
        'requires_flight': False
    },
    'add_flight': {
        'patterns': ['monitor', 'watch', 'track', 'add', 'follow', 'keep eye on', 'observe'],
        'priority': 3,
        'requires_flight': True
    },
    'remove_flight': {
        'patterns': ['remove', 'stop', 'untrack', 'delete', 'unmonitor', 'cancel', 'forget'],
        'priority': 3,
        'requires_flight': True
    },
    'list_flights': {
        'patterns': ['list', 'show', 'display', 'monitored', 'watching', 'my flights', 'what flights', 'which flights'],
        'priority': 2,
        'requires_flight': False
    },
    'start_monitoring': {
        'patterns': ['start', 'begin', 'run', 'autonomous', 'auto', 'continuous', 'keep checking'],
        'priority': 2,
        'requires_flight': False
    },
    'report': {
        'patterns': ['report', 'summary', 'statistics', 'stats', 'performance', 'history', 'results', 'analytics'],
        'priority': 2,
        'requires_flight': False
    },
    'thanks': {
        'patterns': ['thank', 'thanks', 'appreciate', 'awesome', 'great', 'perfect', 'excellent'],
        'priority': 1,
        'requires_flight': False
    },
    'exit': {
        'patterns': ['exit', 'quit', 'bye', 'goodbye', 'see you', 'later', 'done', 'close'],
        'priority': 1,
        'requires_flight': False
    }
}


# ============================================================================
# MAIN AGENT CLASS (Enhanced)
# ============================================================================

class FlightDelayAgent:
    """
    Production-Ready Flight Delay Prediction Agent
    With intelligent recommendations and proactive guidance
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize agent with configuration"""
        self.config = config or AgentConfig()

        # Setup logging
        self._setup_logging()

        self.logger.info("=" * 80)
        self.logger.info("INITIALIZING ENHANCED FLIGHT DELAY PREDICTION AGENT")
        self.logger.info("=" * 80)

        # Feature list for ML model
        self.feature_list = self._get_feature_list()

        # Load ML model
        self._load_model()

        # Initialize recommendation engine
        self.recommendation_engine = RecommendationEngine(self.config)

        # Agent state
        self.monitored_flights: List[Dict] = []
        self.prediction_history: List[Dict] = []
        self.conversation_context: List[str] = []

        # Monitoring control
        self.running = False
        self.stop_event = threading.Event()
        self.monitoring_thread: Optional[threading.Thread] = None

        # Caching
        self.cache: Dict[str, Dict] = {}
        self.cache_duration = timedelta(minutes=self.config.cache_duration_minutes)

        # Intent patterns
        self.intent_patterns = INTENT_PATTERNS

        self.logger.info("✅ Agent initialized with recommendation engine")

    def _setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, self.config.log_level))
        self.logger.handlers = []

        file_handler = logging.FileHandler(
            self.config.log_file,
            encoding='utf-8',
            errors='replace'
        )
        file_handler.setLevel(getattr(logging, self.config.log_level))
        file_handler.setFormatter(logging.Formatter(log_format))
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        self.logger.addHandler(console_handler)

    def _get_feature_list(self) -> List[str]:
        """Get feature list for ML model"""
        return [
            "month", "day_of_month", "day_of_week", "op_carrier_fl_num",
            "crs_dep_time", "dep_time", "crs_arr_time", "arr_time",
            "crs_elapsed_time", "actual_elapsed_time", "distance",
            "temperature_c", "humidity_percent", "pressure_hPa",
            "op_unique_carrier_AA", "op_unique_carrier_AS", "op_unique_carrier_B6",
            "op_unique_carrier_DL", "op_unique_carrier_MQ", "op_unique_carrier_NK",
            "op_unique_carrier_OO", "op_unique_carrier_UA", "op_unique_carrier_WN",
            "op_unique_carrier_YX", "origin_ATL", "origin_CLT", "origin_DEN",
            "origin_DFW", "origin_LAS", "origin_LAX", "origin_LGA", "origin_MCO",
            "origin_ORD", "origin_PHX", "dest_ATL", "dest_CLT", "dest_DEN",
            "dest_DFW", "dest_LAS", "dest_LAX", "dest_LGA", "dest_MCO",
            "dest_ORD", "dest_PHX"
        ]

    def _load_model(self):
        """Load XGBoost model with error handling"""
        try:
            if not Path(self.config.model_path).exists():
                raise FileNotFoundError(f"Model file not found: {self.config.model_path}")

            self.model = xgb.Booster()
            self.model.load_model(self.config.model_path)
            self.logger.info(f"✅ Model loaded from {self.config.model_path}")
        except Exception as e:
            self.logger.error(f"❌ Failed to load model: {e}")
            raise

    # ========================================================================
    # NLU METHODS (Same as before)
    # ========================================================================

    def extract_flight_number(self, text: str) -> Optional[str]:
        """Extract flight number from text"""
        text_upper = text.upper()
        patterns = [
            r'\b([A-Z]{2,3}\d{1,4})\b',
            r'\b([A-Z]{2,3})\s*(\d{1,4})\b',
            r'flight\s*([A-Z]{2,3})\s*(\d{1,4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text_upper)
            if match:
                if len(match.groups()) == 1:
                    return match.group(1)
                else:
                    return match.group(1) + match.group(2)
        return None

    def _calculate_intent_score(self, text: str, patterns: List[str]) -> float:
        """Calculate intent match score"""
        score = 0.0
        words = text.split()

        for pattern in patterns:
            if pattern in text:
                score += 2.0
            elif any(word in pattern.split() for word in words):
                score += 1.0

        return score

    def understand_intent(self, user_input: str) -> Tuple[str, Optional[str]]:
        """Understand user intent"""
        text = user_input.lower().strip()

        self.conversation_context.append(text)
        if len(self.conversation_context) > 5:
            self.conversation_context.pop(0)

        flight_num = self.extract_flight_number(user_input)

        scores = {}
        for intent_name, intent_config in self.intent_patterns.items():
            score = self._calculate_intent_score(text, intent_config['patterns'])
            if score > 0:
                scores[intent_name] = score * intent_config.get('priority', 1)

        if scores:
            best_intent = max(scores, key=scores.get)
            if self.intent_patterns[best_intent].get('requires_flight'):
                return (best_intent, flight_num) if flight_num else ('need_flight_number', None)
            return (best_intent, flight_num)

        if flight_num and len(text.split()) <= 2:
            return ('check_flight', flight_num)

        return ('unclear', text)

    # ========================================================================
    # VALIDATION UTILITIES
    # ========================================================================

    def _validate_flight_data(self, data: Dict) -> bool:
        """Validate flight data structure"""
        if not data:
            return False
        required_fields = ['departure_latitude', 'departure_longitude', 'arrival_latitude', 'arrival_longitude',
                           'origin', 'destination', 'airline']
        return all(field in data for field in required_fields)

    def _validate_coordinates(self, lat: Any, lon: Any) -> bool:
        """Validate geographic coordinates"""
        try:
            lat_f, lon_f = float(lat), float(lon)
            return -90 <= lat_f <= 90 and -180 <= lon_f <= 180
        except (TypeError, ValueError):
            return False

    # ========================================================================
    # PERCEPTION (Data Gathering) - Same as before
    # ========================================================================

    def perceive(self, flight_number: str) -> Optional[Dict]:
        """Gather data from environment with caching"""
        self.logger.info(f"👁️  [PERCEIVE] Gathering data for {flight_number}")

        if self.config.enable_cache:
            cached_data = self._get_from_cache(flight_number)
            if cached_data:
                print("📦 Using cached data")
                return cached_data

        for attempt in range(self.config.max_retries):
            try:
                flight_data = get_flight_data(flight_number)

                if not self._validate_flight_data(flight_data):
                    raise ValueError("Invalid flight data structure")

                if not self._validate_coordinates(
                        flight_data.get('departure_latitude'),
                        flight_data.get('departure_longitude')
                ):
                    raise ValueError("Invalid departure coordinates")

                if not self._validate_coordinates(
                        flight_data.get('arrival_latitude'),
                        flight_data.get('arrival_longitude')
                ):
                    raise ValueError("Invalid arrival coordinates")

                origin_weather = get_weather_data(
                    flight_data['departure_latitude'],
                    flight_data['departure_longitude']
                )

                dest_weather = get_weather_data(
                    flight_data['arrival_latitude'],
                    flight_data['arrival_longitude']
                )

                complete_data = adapt_flight_data(flight_data, origin_weather, dest_weather)

                result = {
                    'flight_data': flight_data,
                    'origin_weather': origin_weather,
                    'dest_weather': dest_weather,
                    'complete_data': complete_data,
                    'timestamp': datetime.now()
                }

                if self.config.enable_cache:
                    self._add_to_cache(flight_number, result)

                self.logger.info("✅ Data gathered successfully")
                print("✅ Data collected successfully")
                return result

            except (ConnectionError, TimeoutError) as e:
                wait_time = 2 ** attempt
                self.logger.warning(f"⚠️  Attempt {attempt + 1}/{self.config.max_retries} failed: {e}")

                if attempt < self.config.max_retries - 1:
                    print(f"⚠️  Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"❌ All retries exhausted for {flight_number}")
                    print(f"❌ Could not retrieve data after {self.config.max_retries} attempts")
                    return None
            except Exception as e:
                self.logger.error(f"❌ Unexpected error: {e}", exc_info=True)
                print(f"❌ Error: {e}")
                return None

        return None

    def _get_from_cache(self, flight_number: str) -> Optional[Dict]:
        """Get data from cache if available"""
        cache_key = f"{flight_number}_{datetime.now().strftime('%Y%m%d%H')}"

        if cache_key in self.cache:
            entry = self.cache[cache_key]
            age = datetime.now() - entry['timestamp']

            if age < self.cache_duration:
                return entry['data']
            else:
                del self.cache[cache_key]
        return None

    def _add_to_cache(self, flight_number: str, data: Dict):
        """Add data to cache"""
        cache_key = f"{flight_number}_{datetime.now().strftime('%Y%m%d%H')}"
        self.cache[cache_key] = {'data': data, 'timestamp': datetime.now()}
        self._clean_cache()

    def _clean_cache(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = [key for key, entry in self.cache.items() if now - entry['timestamp'] > self.cache_duration]
        for key in expired_keys:
            del self.cache[key]

    # ========================================================================
    # REASONING (Prediction) - Same as before
    # ========================================================================

    def reason(self, perceived_data: Dict) -> Optional[Dict]:
        """Analyze data and make prediction"""
        self.logger.info("🧠 [REASON] Analyzing with ML model")
        print("🧠 [REASONING] Analyzing with AI model...")

        try:
            features_df = map_features_for_prediction(perceived_data['complete_data'], self.feature_list)

            if features_df is None:
                raise ValueError("Feature mapping failed")

            dmatrix = xgb.DMatrix(features_df)
            delay_probability = float(self.model.predict(dmatrix)[0])

            prediction = 'DELAYED' if delay_probability > 0.5 else 'ON_TIME'

            if abs(delay_probability - 0.5) > 0.3:
                confidence = 'HIGH'
            elif abs(delay_probability - 0.5) > 0.15:
                confidence = 'MODERATE'
            else:
                confidence = 'LOW'

            result = {
                'prediction': prediction,
                'delay_probability': delay_probability,
                'on_time_probability': 1 - delay_probability,
                'confidence': confidence,
                'features': perceived_data['complete_data'],
                'timestamp': datetime.now()
            }

            self.logger.info(f"✅ Prediction: {prediction} (prob={delay_probability:.2%}, conf={confidence})")
            print(f"✅ Prediction: {prediction} (Confidence: {confidence})")

            return result
        except Exception as e:
            self.logger.error(f"❌ Reasoning failed: {e}", exc_info=True)
            print(f"❌ Prediction failed: {e}")
            return None

    # ========================================================================
    # ACTION WITH RECOMMENDATIONS (ENHANCED)
    # ========================================================================

    def act(self, flight_number: str, perceived_data: Dict, reasoning_result: Dict) -> str:
        """Take action based on prediction with recommendations"""
        self.logger.info("⚡ [ACT] Generating recommendation")

        prob = reasoning_result['delay_probability']
        prediction = reasoning_result['prediction']
        confidence = reasoning_result['confidence']

        flight_info = perceived_data['flight_data']
        complete = perceived_data['complete_data']
        origin_weather = perceived_data['origin_weather']

        # Display results
        print(f"\n{'=' * 80}")
        print("✈️  FLIGHT ANALYSIS RESULTS")
        print(f"{'=' * 80}")
        print(f"Flight: {flight_info.get('airline', 'N/A')} {flight_number}")
        print(f"Route: {flight_info.get('origin', 'N/A')} → {flight_info.get('destination', 'N/A')}")
        print(f"Distance: {complete.get('distance', 'N/A')} miles")

        dep_time = complete.get('crs_dep_time', 0)
        print(f"Departure: {dep_time // 100:02d}:{dep_time % 100:02d}")
        print(f"Date: {complete.get('month', 'N/A')}/{complete.get('day_of_month', 'N/A')}")
        print(f"Weather: {complete.get('temperature_c', 'N/A')}°C, {complete.get('humidity_percent', 'N/A')}% humidity")
        print(f"{'=' * 80}")

        # Risk assessment
        if prob >= 0.85:
            print("🚨 CRITICAL: Very High Delay Risk")
            print(f"📊 Delay Probability: {prob:.1%}")
            print(f"🎯 Confidence: {confidence}")
            action_taken = "CRITICAL_ALERT"
        elif prob >= 0.65:
            print("⚠️  WARNING: Moderate Delay Risk")
            print(f"📊 Delay Probability: {prob:.1%}")
            print(f"🎯 Confidence: {confidence}")
            action_taken = "WARNING"
        elif prob >= 0.40:
            print("⚡ CAUTION: Slight Delay Risk")
            print(f"📊 Delay Probability: {prob:.1%}")
            print(f"🎯 Confidence: {confidence}")
            action_taken = "CAUTION"
        else:
            print("✅ GOOD NEWS: Flight Likely On Time")
            print(f"📊 On-Time Probability: {(1 - prob):.1%}")
            print(f"🎯 Confidence: {confidence}")
            action_taken = "NO_ACTION_NEEDED"

        print(f"{'=' * 80}")

        # Show hint about recommendations
        if self.config.enable_recommendations and prob >= 0.4:
            print(f"\n💡 Want personalized recommendations? Ask me:")
            print(f"   'What should I do about {flight_number}?' or 'Give me advice'")

        print()

        # Update monitored flight info
        for flight in self.monitored_flights:
            if flight['flight_number'] == flight_number:
                flight['last_checked'] = datetime.now()
                flight['check_count'] = flight.get('check_count', 0) + 1
                flight['last_prediction'] = reasoning_result
                flight['error_count'] = 0

        # Add to history
        self.prediction_history.append({
            'flight_number': flight_number,
            'timestamp': datetime.now(),
            'prediction': prediction,
            'probability': prob,
            'confidence': confidence,
            'action_taken': action_taken,
            'flight_info': flight_info
        })

        self.logger.info(f"Action taken: {action_taken}")

        return action_taken

    # ========================================================================
    # FLIGHT MANAGEMENT (Same as before)
    # ========================================================================

    def add_flight(self, flight_number: str) -> bool:
        """Add flight to monitoring list"""
        if any(f['flight_number'] == flight_number for f in self.monitored_flights):
            print(f"\n✅ Already monitoring {flight_number}")
            return False

        if len(self.monitored_flights) >= self.config.max_monitored_flights:
            print(f"\n⚠️  Maximum of {self.config.max_monitored_flights} flights reached")
            return False

        self.monitored_flights.append({
            'flight_number': flight_number,
            'added_at': datetime.now(),
            'last_checked': None,
            'check_count': 0,
            'last_prediction': None,
            'error_count': 0
        })

        print(f"\n✅ Now monitoring: {flight_number}")
        print(f"💡 Total monitored: {len(self.monitored_flights)}/{self.config.max_monitored_flights}")
        return True

    def remove_flight(self, flight_number: str) -> bool:
        """Remove flight from monitoring list"""
        initial_count = len(self.monitored_flights)
        self.monitored_flights = [f for f in self.monitored_flights if f['flight_number'] != flight_number]

        if len(self.monitored_flights) < initial_count:
            print(f"\n✅ Stopped monitoring: {flight_number}")
            return True
        else:
            print(f"\n⚠️  {flight_number} wasn't being monitored")
            return False

    def list_monitored_flights(self):
        """Display list of monitored flights"""
        print(f"\n{'=' * 80}")
        print(f"MONITORED FLIGHTS ({len(self.monitored_flights)}/{self.config.max_monitored_flights})")
        print(f"{'=' * 80}")

        if not self.monitored_flights:
            print("\nNo flights currently being monitored.")
            print("\n💡 To monitor a flight:")
            print("  • Say: 'monitor AA100'")
            print("  • Or: 'track DL123'")
        else:
            for i, flight in enumerate(self.monitored_flights, 1):
                print(f"\n{i}. ✈️  {flight['flight_number']}")
                print(f"   Added: {flight['added_at'].strftime('%Y-%m-%d %H:%M')}")
                print(f"   Checks: {flight.get('check_count', 0)}")

                if flight.get('last_checked'):
                    print(f"   Last: {flight['last_checked'].strftime('%H:%M:%S')}")

                    if flight.get('last_prediction'):
                        pred = flight['last_prediction']
                        print(f"   Result: {pred['prediction']} ({pred['delay_probability']:.1%})")

                if flight.get('error_count', 0) > 0:
                    print(f"   ⚠️  Errors: {flight['error_count']}")

        print(f"{'=' * 80}\n")

    def check_single_flight(self, flight_number: str):
        """Check a single flight through full agent cycle"""
        print(f"\n{'=' * 80}")
        print(f"ANALYZING FLIGHT: {flight_number}")
        print(f"{'=' * 80}\n")

        perceived_data = self.perceive(flight_number)

        if not perceived_data:
            print("\n❌ Could not retrieve flight information")
            print("\n💡 This could mean:")
            print("  • Flight number doesn't exist")
            print("  • Flight data not available")
            print("  • API connection issue")
            return

        reasoning_result = self.reason(perceived_data)

        if not reasoning_result:
            print("\n❌ Could not analyze flight data")
            return

        self.act(flight_number, perceived_data, reasoning_result)

    # ========================================================================
    # NEW RECOMMENDATION FEATURES
    # ========================================================================

    def show_recommendations_for_flight(self, flight_number: str):
        """Show detailed recommendations for a specific flight"""
        # First get the data
        perceived_data = self.perceive(flight_number)
        if not perceived_data:
            print("\n❌ Could not retrieve flight information")
            return

        reasoning_result = self.reason(perceived_data)
        if not reasoning_result:
            print("\n❌ Could not analyze flight data")
            return

        # Generate recommendations
        recommendations = self.recommendation_engine.generate_recommendations(
            perceived_data['flight_data'],
            reasoning_result,
            perceived_data['origin_weather']
        )

        # Display detailed recommendations
        print(f"\n{'=' * 80}")
        print(f"DETAILED RECOMMENDATIONS FOR FLIGHT {flight_number}")
        print(f"{'=' * 80}\n")

        if not recommendations:
            print("No specific recommendations at this time.")
            return

        for i, rec in enumerate(recommendations, 1):
            icon = {
                'CRITICAL': '🚨',
                'ALERT': '⚠️',
                'WARNING': '⚡',
                'INFO': '💡',
                'SUCCESS': '✅'
            }.get(rec['type'], '•')

            print(f"{i}. {icon} {rec['title']}")
            print(f"   Category: {rec['category']}")
            print(f"   Priority: {'High' if rec['priority'] == 1 else 'Medium' if rec['priority'] == 2 else 'Low'}")
            print(f"   {rec['message']}")

            if rec.get('actionable'):
                print(f"   ✓ Actionable: Yes")
                if rec.get('action'):
                    print(f"   ➤ Suggested Action: {rec['action']}")
            else:
                print(f"   ✓ Actionable: No (Informational)")
            print()

        # Show mitigation strategies
        prob = reasoning_result['delay_probability']
        if prob >= 0.4:
            strategies = self.recommendation_engine.get_delay_mitigation_strategies(prob)
            if strategies:
                print(f"{'=' * 80}")
                print("DELAY MITIGATION STRATEGIES")
                print(f"{'=' * 80}\n")

                for strategy in strategies:
                    effectiveness = strategy['effectiveness']
                    icon = '🟢' if effectiveness == 'HIGH' else '🟡' if effectiveness == 'MEDIUM' else '🔴'

                    print(f"{icon} {strategy['title']} (Effectiveness: {effectiveness})")
                    print(f"   {strategy['description']}\n")

        print(f"{'=' * 80}\n")

    def show_proactive_tips(self):
        """Show general proactive travel tips"""
        tips = self.recommendation_engine.get_proactive_tips()

        print(f"\n{'=' * 80}")
        print("PROACTIVE TRAVEL TIPS")
        print(f"{'=' * 80}\n")

        for tip in tips:
            print(f"  {tip}")

        print(f"\n{'=' * 80}\n")

    # ========================================================================
    # MONITORING (Same as before with minor enhancements)
    # ========================================================================

    def _process_single_flight(self, flight_info: Dict):
        """Process a single flight in monitoring loop"""
        flight_number = flight_info['flight_number']

        try:
            perceived_data = self.perceive(flight_number)
            if perceived_data:
                reasoning_result = self.reason(perceived_data)
                if reasoning_result:
                    self.act(flight_number, perceived_data, reasoning_result)
                    flight_info['error_count'] = 0
        except Exception as e:
            self.logger.error(f"Error processing {flight_number}: {e}", exc_info=True)
            print(f"❌ Error processing {flight_number}: {e}")

            flight_info['error_count'] = flight_info.get('error_count', 0) + 1

            if flight_info['error_count'] > 5:
                print(f"⚠️  Removing {flight_number} due to repeated errors")
                self.remove_flight(flight_number)

    def run_autonomous(self, interval_minutes: Optional[int] = None):
        """Run autonomous monitoring loop"""
        if interval_minutes is None:
            interval_minutes = self.config.check_interval_minutes

        self.running = True
        self.stop_event.clear()

        def signal_handler(sig, frame):
            self.stop_gracefully()

        signal.signal(signal.SIGINT, signal_handler)

        self.logger.info(f"Starting autonomous monitoring (interval: {interval_minutes}m)")
        print(f"\n🚀 Autonomous monitoring started (every {interval_minutes} minutes)")
        print("   Press Ctrl+C to stop\n")

        try:
            while self.running and not self.stop_event.is_set():
                cycle_start = datetime.now()

                print(f"\n{'🔄' * 40}")
                print(f"MONITORING CYCLE - {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Flights: {len(self.monitored_flights)}")
                print(f"{'🔄' * 40}\n")

                for flight_info in self.monitored_flights[:]:
                    if self.stop_event.is_set():
                        break
                    self._process_single_flight(flight_info)
                    time.sleep(1)

                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                sleep_time = max(0, (interval_minutes * 60) - cycle_duration)

                if sleep_time > 0 and self.running and not self.stop_event.is_set():
                    next_check = datetime.now() + timedelta(seconds=sleep_time)
                    print(f"\n💤 Next check: {next_check.strftime('%H:%M:%S')}")

                    for _ in range(int(sleep_time)):
                        if self.stop_event.is_set():
                            break
                        time.sleep(1)
        finally:
            self.running = False
            print("\n📊 Monitoring stopped. Generating report...")
            self.generate_report()

    def stop_gracefully(self):
        """Stop monitoring gracefully"""
        print("🛑 Stopping monitoring gracefully...")
        self.running = False
        self.stop_event.set()

    # ========================================================================
    # REPORTING (Same as before)
    # ========================================================================

    def generate_report(self):
        """Generate comprehensive performance report"""
        print(f"\n{'📊' * 40}")
        print("PERFORMANCE REPORT")
        print(f"{'📊' * 40}\n")

        if not self.prediction_history:
            print("No predictions made yet")
            return

        total = len(self.prediction_history)
        delayed = sum(1 for p in self.prediction_history if p['prediction'] == 'DELAYED')
        avg_prob = sum(p['probability'] for p in self.prediction_history) / total
        high_conf = sum(1 for p in self.prediction_history if p['confidence'] == 'HIGH')

        print(f"📈 Total Predictions: {total}")
        print(f"🔴 Predicted Delays: {delayed} ({delayed / total:.1%})")
        print(f"🟢 Predicted On-Time: {total - delayed} ({(total - delayed) / total:.1%})")
        print(f"📊 Average Delay Probability: {avg_prob:.1%}")
        print(f"🎯 High Confidence: {high_conf} ({high_conf / total:.1%})")
        print(f"\n✈️  Currently Monitoring: {len(self.monitored_flights)} flight(s)")

        if self.monitored_flights:
            print("\n" + "=" * 80)
            print("MONITORED FLIGHTS SUMMARY")
            print("=" * 80)

            for flight in self.monitored_flights:
                print(f"\n✈️  {flight['flight_number']}")
                print(f"   Checks: {flight.get('check_count', 0)}")
                print(f"   Added: {flight['added_at'].strftime('%Y-%m-%d %H:%M')}")

                if flight.get('last_checked'):
                    print(f"   Last Check: {flight['last_checked'].strftime('%Y-%m-%d %H:%M:%S')}")

                if flight.get('last_prediction'):
                    pred = flight['last_prediction']
                    print(
                        f"   Last Result: {pred['prediction']} ({pred['delay_probability']:.1%}, {pred['confidence']})")

        if len(self.prediction_history) > 0:
            print("\n" + "=" * 80)
            print("RECENT PREDICTIONS (Last 5)")
            print("=" * 80)

            for i, pred in enumerate(reversed(self.prediction_history[-5:]), 1):
                print(f"\n{i}. {pred['flight_number']} - {pred['timestamp'].strftime('%H:%M:%S')}")
                print(f"   Result: {pred['prediction']} ({pred['probability']:.1%})")
                print(f"   Confidence: {pred['confidence']}")

        print(f"\n{'📊' * 40}\n")

    # ========================================================================
    # CONVERSATIONAL RESPONSES (Enhanced)
    # ========================================================================

    def respond_to_greeting(self):
        """Friendly greeting response"""
        import random

        greetings = [
            "👋 Hello! Great to see you!",
            "👋 Hi there! How can I help you today?",
            "👋 Hey! Ready to help with flight predictions!",
            "👋 Hello! What flight would you like to check?"
        ]

        print("\n" + "=" * 80)
        print(random.choice(greetings))
        print("=" * 80)
        print("\n💡 I can predict flight delays with AI!")
        print("   (Ask me for recommendations if you need advice)")
        print("\nJust tell me:")
        print("  • A flight number (e.g., 'AA100')")
        print("  • Or ask: 'Will AA100 be delayed?'")
        print("  • Or ask: 'What should I do about AA100?' for advice")
        print("=" * 80 + "\n")

    def respond_to_help(self):
        """Comprehensive help message"""
        print("\n" + "=" * 80)
        print("📚 WHAT I CAN DO FOR YOU")
        print("=" * 80)
        print("\n🎯 My Capabilities:")
        print("  1. Predict if flights will be delayed (AI-powered)")
        print("  2. Provide personalized recommendations (when requested)")
        print("  3. Suggest alternative flights and timing options")
        print("  4. Monitor multiple flights automatically")
        print("  5. Give proactive travel tips and best practices")
        print("  6. Provide weather-based insights")
        print("\n💬 Ways to Talk to Me:")
        print("\n  Predictions:")
        print("    • 'Will AA100 be delayed?'")
        print("    • 'Check flight DL123'")
        print("    • 'Analyze UA456'")
        print("\n  Get Recommendations (Only When You Ask):")
        print("    • 'What should I do about AA100?'")
        print("    • 'Give me advice for flight DL123'")
        print("    • 'Suggest alternatives for AA100'")
        print("    • 'Give me travel tips'")
        print("\n  Monitoring:")
        print("    • 'Monitor AA100'")
        print("    • 'List my flights'")
        print("    • 'Start monitoring'")
        print("\n  Reports:")
        print("    • 'Generate report'")
        print("    • 'Show statistics'")
        print("\n✨ I understand natural conversation and context!")
        print("=" * 80 + "\n")

    def respond_to_thanks(self):
        """Respond to thanks"""
        import random
        responses = [
            "😊 You're welcome! Happy to help with your travel!",
            "😊 My pleasure! Safe travels!",
            "😊 Glad I could help! Let me know if you need more recommendations!",
            "😊 Anytime! Hope your flight goes smoothly!"
        ]
        print("\n" + random.choice(responses) + "\n")

    def respond_to_need_flight_number(self):
        """Ask for flight number"""
        print("\n" + "=" * 80)
        print("✈️  Which flight should I analyze?")
        print("=" * 80)
        print("\nPlease tell me a flight number.")
        print("\nExamples:")
        print("  • AA100")
        print("  • Delta 123")
        print("  • United 456")
        print("\nJust type the flight number or say 'cancel' to go back.")
        print("=" * 80 + "\n")

    def respond_to_unclear(self, original_text: str) -> Tuple[str, Optional[str]]:
        """Handle unclear input"""
        print("\n" + "=" * 80)
        print("🤔 I'm trying to understand...")
        print("=" * 80)

        flight_num = self.extract_flight_number(original_text)

        if flight_num:
            print(f"\n💡 I found flight number: {flight_num}")
            print(f"   Would you like me to check this flight? (yes/no)")
            return ('confirm_flight', flight_num)
        else:
            print("\n💡 I can help you with:")
            print("  • Flight delay predictions")
            print("  • Personalized recommendations")
            print("  • Alternative flight suggestions")
            print("  • Travel tips and advice")
            print("\nTry:")
            print("  • Type a flight number: 'AA100'")
            print("  • Ask: 'What should I do about DL123?'")
            print("  • Say: 'Give me travel tips'")
            print("  • Say 'help' for more options")

        print("=" * 80 + "\n")
        return ('unclear', None)

    # ========================================================================
    # CONVERSATIONAL INTERFACE (Enhanced)
    # ========================================================================

    def conversational_interface(self):
        """Main conversational interface with recommendations"""
        print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║    FLIGHT DELAY PREDICTION - WITH SMART RECOMMENDATIONS       ║
    ║                                                                ║
    ║      Intelligent • Personalized • On-Demand • Actionable      ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
        """)

        print("💬 Talk to me naturally! I understand:")
        print("   • Predictions: 'Will AA100 be delayed?'")
        print("   • Recommendations: 'What should I do about AA100?' (when you need advice)")
        print("   • Tips: 'Give me travel advice'")
        print("   • And much more!\n")
        print("=" * 80 + "\n")

        # Keywords that trigger recommendations
        recommendation_keywords = [
            'recommend', 'recommendation', 'recommendations',
            'suggest', 'suggestion', 'suggestions',
            'advice', 'advise', 'tip', 'tips',
            'what should i do', 'what do i do', 'what can i do',
            'help me with', 'guide', 'guidance',
            'alternative', 'alternatives', 'option', 'options',
            'best practices', 'how to prepare'
        ]

        pending_confirmation = None

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                user_input_lower = user_input.lower()

                # Check if message contains recommendation keywords
                contains_recommendation_keyword = any(
                    keyword in user_input_lower
                    for keyword in recommendation_keywords
                )

                # Handle confirmations
                if pending_confirmation:
                    if user_input.lower() in ['yes', 'y', 'yeah', 'yep', 'sure', 'ok', 'okay']:
                        intent_type, data = pending_confirmation
                        pending_confirmation = None
                        if intent_type == 'check_flight':
                            self.check_single_flight(data)
                        continue
                    elif user_input.lower() in ['no', 'n', 'nope', 'cancel', 'nevermind']:
                        print("\n✅ Cancelled. What else can I help with?\n")
                        pending_confirmation = None
                        continue

                # Extract flight number from message
                flight_num_in_message = self.extract_flight_number(user_input)

                # If message contains recommendation keywords AND a flight number, show recommendations
                if contains_recommendation_keyword and flight_num_in_message:
                    print(f"\n🎯 I'll show you recommendations for flight {flight_num_in_message}!\n")
                    self.show_recommendations_for_flight(flight_num_in_message)
                    continue

                # If message contains recommendation keywords but NO flight number
                if contains_recommendation_keyword and not flight_num_in_message:
                    # Check if they're asking for general tips
                    if any(word in user_input_lower for word in
                           ['tip', 'tips', 'best practices', 'how to prepare', 'general']):
                        self.show_proactive_tips()
                        continue
                    else:
                        # Ask which flight they want recommendations for
                        print("\n💡 I'd love to give you recommendations!")
                        print("Which flight would you like advice about?")
                        print("(Or say 'general tips' for travel best practices)\n")
                        continue

                # Normal intent processing
                intent, data = self.understand_intent(user_input)

                # Handle intents
                if intent == 'greeting':
                    self.respond_to_greeting()

                elif intent == 'help':
                    self.respond_to_help()

                elif intent == 'check_flight':
                    self.check_single_flight(data)

                elif intent == 'get_recommendations':
                    if data:
                        self.show_recommendations_for_flight(data)
                    else:
                        self.respond_to_need_flight_number()

                elif intent == 'proactive_tips':
                    self.show_proactive_tips()

                elif intent == 'alternatives':
                    if data:
                        self.show_recommendations_for_flight(data)
                    else:
                        self.respond_to_need_flight_number()

                elif intent == 'add_flight':
                    self.add_flight(data)

                elif intent == 'remove_flight':
                    self.remove_flight(data)

                elif intent == 'list_flights':
                    self.list_monitored_flights()

                elif intent == 'start_monitoring':
                    if not self.monitored_flights:
                        print("\n⚠️  No flights to monitor yet!")
                        print("💡 Add flights first:")
                        print("   Say: 'monitor AA100'")
                    else:
                        interval = input("\n⏱️  Check interval (minutes, default 30): ").strip()
                        interval = int(interval) if interval.isdigit() else 30
                        self.run_autonomous(interval)

                elif intent == 'report':
                    self.generate_report()

                elif intent == 'thanks':
                    self.respond_to_thanks()

                elif intent == 'need_flight_number':
                    self.respond_to_need_flight_number()

                elif intent == 'exit':
                    print("\n👋 Goodbye! Safe travels!")
                    if self.prediction_history:
                        print("\n📊 Here's your final report:")
                        self.generate_report()
                    break

                elif intent == 'unclear':
                    result = self.respond_to_unclear(data)
                    if result[0] == 'confirm_flight':
                        pending_confirmation = ('check_flight', result[1])

                elif intent == 'confirm_flight':
                    pending_confirmation = ('check_flight', data)

            except KeyboardInterrupt:
                print("\n\n🛑 Interrupted by user")
                self.stop_gracefully()
                break

            except Exception as e:
                self.logger.error(f"Error in conversational interface: {e}", exc_info=True)
                print(f"\n❌ Unexpected error: {e}")
                print("💡 Please try again or type 'help'\n")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    print("\n" + "🚀" * 40)
    print("Starting Enhanced Flight Delay Prediction Agent")
    print("With Intelligent Recommendations")
    print("🚀" * 40 + "\n")

    config_path = "agent_config.json"

    if Path(config_path).exists():
        print(f"📋 Loading configuration from {config_path}")
        config = AgentConfig.from_file(config_path)
    else:
        print("📋 Using default configuration")
        config = AgentConfig()
        config.to_file(config_path)
        print(f"💾 Saved default config to {config_path}")

    try:
        agent = FlightDelayAgent(config=config)
        agent.conversational_interface()
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        print("Please check the logs for details")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())