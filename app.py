from flask import Flask, render_template, request, session, redirect, url_for, flash
import json
import random
import logging

app = Flask(__name__)
# app.secret_key = 'your_secret_key'
app.secret_key = 'key_27_key'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Server Error: {error}, route: {request.url}")
    return render_template('500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"Page Not Found: {error}, route: {request.url}")
    return render_template('404.html'), 404


# Load vocab.json
with open('vocab.json', 'r', encoding='utf-8') as f:
    words = json.load(f)

def get_new_question(level):
    # if level is 20 get word from a different level 50% of the time
    if session['completed'] == True and random.random() < 0.5:
        level = random.randint(1, 19)   
    #change to a lower level 20% of the time
    elif random.random() < 0.2 and level > 1:
        #get a random number between 1 and the current level
        level = random.randint(1, level)
    print(level)    
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

    random.shuffle(choices)
    return word_entry['tajik'], choices, correct_answer

# Initialize the game state
@app.route('/')
def index():
    print("in index")
    return render_template('index.html')

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
                    flash('You moved to the next level!', 'accomplishment') 
            # Check if completed is true
            elif session['completed'] == True:
                # encourage the user not to stop
                # choose from 15 different encouragements
                encouragement = ['Fantastic!', 'Extend that streak!', 'You are crushing it!', 'Keep going to increase your streak!', 'You are a language champion', 'Look at your streak! Amazing!', 'Phenomenal!', 'You are on fire!', 'Bravo!!!', 'Keep up the great work!', 'Incredible progress', 'You are unstopable!', 'Keep shining!!', 'You are a language wizard!', 'You are an inspiration!']
                flash(random.choice(encouragement), 'encouragement')
            # Check if the streak is a multiple of 3 and the level is already 20
            elif session['streak'] > 0 and session['streak'] % 3 == 0 and session['level'] == 20:
                flash('Congratulations! You have completed all levels!', 'completion')
                # create variable completed is true
                session['completed'] = True
            
            # else encourage the user to keep going
            elif session['streak'] > 5:
                # encourage the user to keep going
                # choose from 15 different encouragements
                encouragement = ['Great job!', 'You are doing great!', 'Keep up the good work!', 'You are on a roll!', 'You are unstoppable!', 'You are a language master!', 'You are a language genius!', 'Amazing', 'Look at that streak!', 'You are a language whiz!', 'Go you!', 'Woohoo!!!', 'Wow ... just wow', 'Impressive!', 'You are a language superstar!']

                flash(random.choice(encouragement), 'encouragement')
                        
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