# Flight Delay Prediction System

## Overview

The Flight Delay Prediction System is an AI-powered web application that predicts whether a flight is likely to be delayed before departure. The system analyzes historical flight records along with real-time weather conditions to provide accurate delay predictions, estimated delay duration, and helpful recommendations for passengers.

This project was developed as part of the Artificial Intelligence course.

## Features

- Predicts flight delays before departure
- Estimates delay duration
- Retrieves real-time weather information
- Explains the factors affecting predictions
- Provides travel recommendations for passengers
- Interactive React-based user interface

## Technology Stack

### Frontend
- React.js

### Backend
- Flask (Python)

### Machine Learning
- XGBoost
- CatBoost
- Random Forest
- LightGBM
- Artificial Neural Network (ANN)

### Libraries
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn
- XGBoost
- CatBoost
- LightGBM

### API
- OpenWeatherMap API

## Project Structure

```
FlightDelayPrediction/
│
├── frontend/
├── backend/
├── models/
├── dataset/
├── feature_engineering.py
├── get_weather.py
├── app.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository.

```bash
git clone <repository-url>
```

2. Navigate to the project folder.

```bash
cd FlightDelayPrediction
```

3. Install the required Python packages.

```bash
pip install -r requirements.txt
```

4. Configure your OpenWeatherMap API key.

5. Start the backend server.

```bash
python app.py
```

6. Start the frontend.

```bash
npm install
npm start
```

## How It Works

1. The user enters a flight number.
2. Historical flight information is retrieved.
3. Current weather data is fetched using the weather API.
4. Data is cleaned and transformed into model features.
5. The trained machine learning model predicts whether the flight will be delayed.
6. The prediction, estimated delay, explanation, and recommendations are displayed to the user.

## Future Enhancements

- Support for more airlines
- Live flight tracking
- Mobile application
- Improved prediction accuracy
- Additional weather parameters

## Contributors

- Alishba Zainab
- Fatima Kashif

## License

This project was developed for academic purposes.
