from flask import Flask, render_template, request, session, redirect, url_for, flash
import json
import random

app = Flask(__name__)
# app.secret_key = 'your_secret_key'
app.secret_key = 'key_24_key'

# Load vocab.json
with open('vocab.json', 'r', encoding='utf-8') as f:
    words = json.load(f)

def get_new_question(level):
    # Get a random word entry for the current level
    level_words = words[str(level)]
    word_entry = random.choice(level_words)
    correct_answer = word_entry['english']
    
    # Generate choices including the correct answer and 3 random incorrect answers
    choices = [correct_answer] + random.sample(
        [entry['english'] for entry in level_words if entry != word_entry], 3
    )
    random.shuffle(choices)
    return word_entry['tajik'], choices, correct_answer

# Initialize the game state
@app.route('/')
def index():
    # Initialize score and streak if not already in session
    if 'score' not in session:
        session['score'] = 0
    if 'streak' not in session:
        session['streak'] = 0
    if 'level' not in session:
        session['level'] = 1
    if 'completed' not in session:
        session['completed'] = False

    # Get a new question for the current level
    word, choices, correct_answer = get_new_question(session['level'])
    
    # Render the template with the current game state
    return render_template('index.html', word=word, choices=choices, correct_answer=correct_answer, level=session['level'], score=session['score'], streak=session['streak'])

@app.route('/check-answer', methods=['POST'])
def check_answer():
    user_answer = request.form['answer']
    correct_answer = request.form['correct_answer']

    if 'completed' not in session:
        session['completed'] = False
    
    # Check if the user's answer is correct
    if user_answer == correct_answer:
        session['streak'] += 1
        session['score'] += 1
        flash('Correct!', 'success')

        # Check if the streak is a multiple of 3 and increase the level unless it is already 20
        if session['streak'] > 0 and session['streak'] % 3 == 0 and session['level'] < 20:
            session['level'] += 1
            flash('You moved to the next level!', 'success') 
        # Check if completed is true
        elif session['completed'] == True:
            flash('Keep going to increase your streak!', 'success')   
        # Check if the streak is a multiple of 3 and the level is already 20
        elif session['streak'] > 0 and session['streak'] % 3 == 0 and session['level'] == 20:
            flash('Congratulations! You have completed all levels!', 'success')
            # create variable completed is true
            session['completed'] = True
        
        # else encourage the user to keep going
        else:
            flash('You are doing great!', 'success')
     
    else:
        # set the streak to 0 if the answer is incorrect
        # decrease level by 1 unless level is at 1
        # set completed to false
        session['streak'] = 0
        if session['level'] > 1:
            session['level'] -= 1
        session['completed'] = False
        flash('Incorrect.', 'danger')
        
    
    # Redirect back to the index route to get a new question
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)