
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)


client = MongoClient("mongodb://localhost:27017/")  # MongoDB URI
db = client['user_database']  # Database name
scores_collection = db['users']  # Collection to store scores

# Home route
@app.route("/")
def home():
    return render_template('game_portal.html')

# Route to handle difficulty selection and redirect to game options
@app.route("/select_difficulty", methods=['POST'])
def select_difficulty():
    name = request.form['name']
    age = request.form['age']
    difficulty = request.form['difficulty']
    return redirect(url_for(f"{difficulty}_games", name=name, age=age))

# Easy games selection route
@app.route("/easy_games/<name>/<age>")
def easy_games(name, age):
    return render_template('select_game.html', difficulty="easy", name=name, age=age, games=['tic_tac_toe', 'memory_game', 'rock_paper_scissors'])

# Moderate games selection route
@app.route("/moderate_games/<name>/<age>")
def moderate_games(name, age):
    return render_template('select_game.html', difficulty="moderate", name=name, age=age, games=['snake_game', 'red_square'])

# Hard games selection route
@app.route("/hard_games/<name>/<age>")
def hard_games(name, age):
    return render_template('select_game.html', difficulty="hard", name=name, age=age, games=['breakout', 'platform'])

# Game route based on selection
@app.route("/game/<difficulty>/<game>/<name>/<age>")
def game(difficulty, game, name, age):
    template_mapping = {
        'tic_tac_toe': 'tic_tac_toe.html',
        'memory_game': 'memory_game.html',
        'rock_paper_scissors': 'rock_paper_scissors.html',
        'snake_game': 'snake_game.html',
        'red_square': 'red_square.html',
        'breakout': 'breakout.html',
        'platform': 'platform.html'
    }
    template = template_mapping.get(game)
    if template:
        return render_template(template, name=name, age=age, difficulty=difficulty)
    else:
        return "Invalid game selection", 400

# Route to submit score to MongoDB
@app.route('/update_score', methods=['POST'])
def update_score():
    data = request.get_json()  # Parse JSON data from the request
    data['submitted_at'] = datetime.now()  # Add timestamp
    scores_collection.insert_one(data)  # Insert score data into MongoDB
    return jsonify({'message': 'Score updated successfully!'}), 200

# Route to display Easy level scores
@app.route('/dashboard/easy_scores')
def display_easy_scores():
    games = ['tic_tac_toe', 'memory_game', 'rock_paper_scissors']  # Easy level games
    results = scores_collection.find({'game': {'$in': games}}).sort('score', -1).limit(10)
    scores_list = format_scores(results)
    
    return render_template('easy_scores.html', scores=scores_list)

# Route to display Moderate level scores
@app.route('/dashboard/moderate_scores')
def display_moderate_scores():
    games = ['snake_game', 'red_square']  # Moderate level games
    results = scores_collection.find({'game': {'$in': games}}).sort('score', -1).limit(10)
    scores_list = format_scores(results)
    
    return render_template('moderate_scores.html', scores=scores_list)

# Route to display Hard level scores
@app.route('/dashboard/hard_scores')
def display_hard_scores():
    games = ['breakout', 'platform']  # Hard level games
    results = scores_collection.find({'game': {'$in': games}}).sort('score', -1).limit(10)
    scores_list = format_scores(results)
    
    return render_template('hard_scores.html', scores=scores_list)

# Helper function to format score results
def format_scores(results):
    scores_list = []
    for result in results:
        scores_list.append({
            'name': result.get('name', 'Unknown'),
            'age': result.get('age', 'Unknown'),
            'score': result.get('score', 0),
            'game': result.get('game', 'Unknown'),
            'submitted_at': result['submitted_at'].strftime('%Y-%m-%d %H:%M:%S')
        })
    return scores_list

# Debugging Helper Route to Print All Scores
@app.route('/debug/all_scores')
def debug_all_scores():
    all_scores = list(scores_collection.find())
    formatted_scores = format_scores(all_scores)
    return jsonify(formatted_scores)

# Main entry point
if __name__ == "__main__":
    app.run(debug=True, port=5001)
