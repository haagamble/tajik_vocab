from flask import Flask, render_template, request, session, redirect, url_for, flash
import json
import random

app = Flask(__name__)
# app.secret_key = 'your_secret_key'
app.secret_key = 'key_25_key'

# Load vocab.json
with open('vocab.json', 'r', encoding='utf-8') as f:
    words = json.load(f)

def get_new_question(level):
    # Get a random word entry for the current level
    level_words = words[str(level)]
    # print(level_words)
    word_entry = random.choice(level_words)
    correct_answer = word_entry['english']
    #get type of word of word_entry
    word_type = word_entry['type']

    # Generate choices including the correct answer and 3 random incorrect answers with the same tyep
    choices = [correct_answer] + random.sample(
        [entry['english'] for entry in level_words if entry != word_entry and entry['type'] == word_type], 3
    )   

    # Generate choices including the correct answer and 3 random incorrect answers
    # choices = [correct_answer] + random.sample(
    #     [entry['english'] for entry in level_words if entry != word_entry], 3
    # )
    random.shuffle(choices)
    return word_entry['tajik'], choices, correct_answer

# Initialize the game state
@app.route('/')
def index():
    print("in index")
    return render_template('index.html')
    # Initialize score and streak if not already in session
    # if 'score' not in session:
    #     session['score'] = 0
    # if 'streak' not in session:
    #     session['streak'] = 0
    # if 'level' not in session:
    #     session['level'] = 1
    # if 'completed' not in session:
    #     session['completed'] = False

 
    
    # Render the template with the current game state
    # return render_template('index.html', word=word, choices=choices, correct_answer=correct_answer, level=session['level'], score=session['score'], streak=session['streak'])

@app.route('/tajik-vocab', methods=['POST', 'GET'])
def tajik_vocab():
    # If GET request, initialize the game state and get the first question

    if request.method == 'GET':
        if 'score' not in session:
            session['score'] = 0
            session['streak'] = 0
            session['level'] = 1
            session['completed'] = False
        word, choices, correct_answer = get_new_question(session['level'])
        return render_template('vocab.html', word=word, choices=choices, correct_answer=correct_answer, level=session['level'], score=session['score'], streak=session['streak'])
    
    # If POST request, check the user's answer and update the game state
    if request.method == 'POST':
    
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
                if session['level'] < 20:
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
            
        
        # Redirect back to the same route route to get a new question
        return redirect(url_for('tajik_vocab'))

if __name__ == '__main__':
    app.run(debug=True)