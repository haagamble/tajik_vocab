from flask import Flask, render_template, request, session, redirect, url_for, flash
import json
import random

app = Flask(__name__)
# app.secret_key = 'your_secret_key'
app.secret_key = 'sixth_key'

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

    # Check if the streak is a multiple of 3 and increase the level
    # This is repeated in check-answer route
    # if session['streak'] > 0 and session['streak'] % 3 == 0:
    #     session['level'] += 1
    
    # Get a new question for the current level
    word, choices, correct_answer = get_new_question(session['level'])
    
    # Render the template with the current game state
    return render_template('index.html', word=word, choices=choices, correct_answer=correct_answer, level=session['level'], score=session['score'], streak=session['streak'])

@app.route('/check-answer', methods=['POST'])
def check_answer():
    user_answer = request.form['answer']
    correct_answer = request.form['correct_answer']
    
    # Check if the user's answer is correct
    if user_answer == correct_answer:
        session['streak'] += 1
        session['score'] += 1
        flash('Correct!', 'success')
        
        # Check if level is 20 and streak is more than 31
        if session['level'] == 20 and session['streak'] > 30:
            flash('Keep going to get a longer streak!', 'success')
        else:
            # Move to the next level if the streak is a multiple of 3
            if session['streak'] % 3 == 0:
                if session['level'] == 20 and session['streak'] <= 30:
                    flash('Congratulations! You have completed all levels!', 'success')
                else:
                    flash('You moved to the next level!', 'success')
                    session['level'] += 1
            
    else:
        # set the streak to 0 if the answer is incorrect
        # decrease level by 1 if the streak is 0
        session['streak'] = 0
        if session['level'] > 1:
            session['level'] -= 1
        flash('Incorrect.', 'danger')
        
    
    # Redirect back to the index route to get a new question
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)