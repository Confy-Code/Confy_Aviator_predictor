from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
from datetime import datetime, timedelta
import joblib
import pandas as pd
import numpy as np
from collections import deque


# Configuration and Initialization
MODEL_PATH = r"C:\Users\user\Avi_Trainer.pkl"
DATABASE_PATH = r"E:\DOWNLOAD 1\Aviator_tracker1.accdb"
HISTORY_WINDOW_SIZE = 2000
PREDICTION_WINDOW = 200

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load trained model
try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully. Expected features:")
    print(model.feature_names_in_)
except Exception as e:
    print(f"Error loading model: {str(e)}")
    model = None

# Database connection
conn_str = (
    r'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};'
    r'DBQ={};'.format(DATABASE_PATH)
)

# Data buffers for rolling calculations
history_buffers = {
    'multipliers': deque(maxlen=HISTORY_WINDOW_SIZE),
    'timestamps': deque(maxlen=HISTORY_WINDOW_SIZE),
    'won_bets': deque(maxlen=HISTORY_WINDOW_SIZE),
    'player_count': deque(maxlen=HISTORY_WINDOW_SIZE),
    'bad_bets': deque(maxlen=HISTORY_WINDOW_SIZE),
    'total_bets': deque(maxlen=HISTORY_WINDOW_SIZE),
    'cashouts': deque(maxlen=HISTORY_WINDOW_SIZE)
}

def get_recent_data(num_records=PREDICTION_WINDOW):
    #Fetch recent game records from database
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            query = f"""
               SELECT TOP {num_records}
                    [Multiplier], [CashoutVALUE], [WonBets],
                    [BadBets], [TotalBets], [LosersCount], [Timestamp]
                FROM [MultiplierData]
                ORDER BY [Timestamp] DESC
            """
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            records = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return records[::-1]  # Return in chronological order
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

def update_history_buffers(data):
    """Update all history buffers with new game data"""
    history_buffers['multipliers'].append(data['multiplier'])
    history_buffers['timestamps'].append(datetime.now())
    history_buffers['won_bets'].append(data['won_bets'])
    history_buffers['player_count'].append(data['player_count'])
    history_buffers['bad_bets'].append(data['bad_bets'])
    history_buffers['total_bets'].append(data['total_bets'])
    history_buffers['cashouts'].append(data['cashout'])

def calculate_features():
    """Calculate all features in exact model training order"""
    now = datetime.now()
    window_size = min(PREDICTION_WINDOW, len(history_buffers['multipliers']))
    
    # Get recent data for window-based calculations
    recent_data = get_recent_data(window_size) if window_size > 0 else []
    
    # Base features
    features = {
        'CashoutVALUE': np.median(history_buffers['cashouts']) if history_buffers['cashouts'] else 0,
        'WonBets': np.mean(history_buffers['won_bets']) if history_buffers['won_bets'] else 0,
        'BadBets': np.mean(history_buffers['bad_bets']) if history_buffers['bad_bets'] else 0,
        'TotalBets': np.mean(history_buffers['total_bets']) if history_buffers['total_bets'] else 0,
        'LosersCount': np.mean(history_buffers['player_count']) if history_buffers['player_count'] else 0,
        'hour': now.hour,
        'minute': now.minute,
        'second': now.second,
        'hour_sin': np.sin(2 * np.pi * now.hour / 24),
        'hour_cos': np.cos(2 * np.pi * now.hour / 24),
        'WinRate': (history_buffers['won_bets'][-1] / history_buffers['player_count'][-1]) 
                  if history_buffers['player_count'] else 0,
        'BadRate': 1 - (history_buffers['won_bets'][-1] / history_buffers['player_count'][-1]) 
                  if history_buffers['player_count'] else 0,
    }
    
    # Rolling statistics
    rolling_features = {
        'rolling_win_mean': np.mean(list(history_buffers['won_bets'])[-window_size:]) if window_size > 0 else 0,
        'rolling_loss_std': np.std(list(history_buffers['player_count'])[-window_size:]) if window_size > 1 else 0,
        'rolling_win_max': max(list(history_buffers['won_bets'])[-window_size:]) if window_size > 0 else 0,
        'rolling_loss_max': max(list(history_buffers['player_count'])[-window_size:]) if window_size > 0 else 0,
        'rolling_win_median': np.median(list(history_buffers['won_bets'])[-window_size:]) if window_size > 0 else 0,
        'rolling_loss_median': np.median(list(history_buffers['player_count'])[-window_size:]) if window_size > 0 else 0,
    }
    
    features.update(rolling_features)
    
    # Return only features the model expects, in correct order
    return {k: features[k] for k in model.feature_names_in_} if model else {}

def predict_next_round():
    """Generate prediction with dynamic adjustments and prediction range"""
    if not model:
        print("Prediction unavailable - insufficient data")
        return None

    try:
        # Build features
        features = calculate_features()
        predict_data = pd.DataFrame([features], columns=model.feature_names_in_)

        # Base prediction from model
        base_pred = model.predict(predict_data)[0]

        # Dynamic adjustments based on recent trends
        adjustment = 1.0
        if len(history_buffers['multipliers']) > 5:
            last_5 = list(history_buffers['multipliers'])[-5:]
            last_5_avg = np.mean(last_5)

            if last_5_avg > 2.0:  # Hot streak
                adjustment *= 1.2
            elif last_5_avg < 1.3:  # Cold streak
                adjustment *= 0.8

        final_pred = base_pred * adjustment
        final_pred = min(max(final_pred, 1.1), 10.0)

        # Define prediction range using model RMSE
        MODEL_RMSE = 5.4237
        lower = max(1.0, final_pred - MODEL_RMSE)
        upper = final_pred + MODEL_RMSE

        # Round nicely
        final_pred = round(final_pred, 2)
        lower = round(lower, 2)
        upper = round(upper, 2)

        print(f"Predicted: {final_pred}x (Range: {lower}x - {upper}x)")

        return final_pred, (lower, upper)

    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return None


@app.route('/api/multipliers', methods=['POST'])
def handle_game_result():
    #Process game results and return predictions
    try:
        data = request.json
        
        # Validate and parse input
        try:
            game_data = {
                'multiplier': float(data['multiplier']),
                'player_count': int(data['player_count'].replace(',', '')),
                'bad_bets': int(data['bets_count'].split('/')[0]),
                'total_bets': int(data['bets_count'].split('/')[1]),
                'cashout': float(data['cashout_value'].replace(',', '')) if data['cashout_value'] else 0.0
            }
            game_data['won_bets'] = game_data['total_bets'] - game_data['bad_bets']
            print(f"Received: {game_data['multiplier']}")
        except (ValueError, KeyError, IndexError) as e:
            return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
        
        # Update history and database
        prediction = predict_next_round()
        update_history_buffers(game_data)
        #print("reaching db")
        save_to_database(game_data)
        
        # Generate and return prediction
        
        return jsonify({
            "status": "success",
            "prediction": prediction,
            "actual": game_data['multiplier']
        }), 200
        
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def save_to_database(game_data):
    """Save game result to database"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO [MultiplierData] (
                    [Multiplier], [CashoutVALUE], [WonBets],
                    [BadBets], [TotalBets], [LosersCount], [Timestamp]
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                game_data['multiplier'],
                game_data['cashout'],
                game_data['won_bets'],
                game_data['bad_bets'],
                game_data['total_bets'],
                game_data['player_count'],
                datetime.now()
            ))
            conn.commit()
            print('database working duh!')
    except Exception as e:
        print(f"Database save error: {str(e)}")

def initialize_data():
    """Load initial historical data"""
    if not history_buffers['multipliers']:
        print("Loading initial game data...")
        for record in get_recent_data(PREDICTION_WINDOW):
            history_buffers['multipliers'].append(float(record['Multiplier']))
            history_buffers['timestamps'].append(record['Timestamp'])
            history_buffers['won_bets'].append(int(record['WonBets']))
            history_buffers['player_count'].append(int(record['LosersCount']))
            history_buffers['bad_bets'].append(int(record['BadBets']))
            history_buffers['total_bets'].append(int(record['TotalBets']))
            history_buffers['cashouts'].append(float(record['CashoutVALUE']))

if __name__ == '__main__':
    initialize_data()
    
    # Set up periodic prediction updates
    #scheduler = BackgroundScheduler()
    #scheduler.add_job(predict_next_round, 'interval', seconds=30)
    #scheduler.start()
    
    #print("Aviator Prediction API started")
    app.run(host='0.0.0.0', port=5000)