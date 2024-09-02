from flask import Flask, render_template, request, session, redirect, url_for, flash
import json
import random
import logging
from datetime import datetime

app = Flask(__name__)
#app.secret_key = 'your_secret_key'

# set key for testing
app.secret_key = 'sept1_10_15'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure session variables are initialized
def initialize_session_variables():
    if 'completed' not in session:
        session['completed'] = False
        logger.info("Session variable 'completed' initialized") 
    if 'score' not in session:
        session['score'] = 0
        logger.info("Session variable 'score' initialized")
    if 'streak' not in session:
        session['streak'] = 0
        logger.info("Session variable 'streak' initialized")
    if 'highest_streak' not in session:
        session['highest_streak'] = 0
        logger.info("Session variable 'highest_streak' initialized")
    if 'level' not in session:
        session['level'] = 1
        logger.info("Session variable 'level' initialized")

def reset_game_if_new_day():
    # Get today's date
    today = datetime.now().date()
    # Get the last played date from the session
    last_played_str = session.get('last_played')

    if last_played_str:
        try:
            last_played = datetime.strptime(last_played_str, '%Y-%m-%d').date()
        except ValueError:
            # Handle the case where the date format is incorrect
            last_played = None
    else:
        last_played = None
    
    # Check if the last played date is not today
    if last_played is None or last_played != today:
        # Reset the game state
        session['score'] = 0
        session['streak'] = 0
        session['highest_streak'] = 0
        session['level'] = 1
        session['completed'] = False
        session['previous_words'] = []
        session['question_answered'] = False
        # Update the last played date as a string
        session['last_played'] = today.strftime('%Y-%m-%d')
    
    
    logger.info(f"Last played date: {session['last_played']}")
    logger.info(f"Today's date: {today}")    


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
    # Initialize previous words list in session if it doesn't exist
    if 'previous_words' not in session:
        session['previous_words'] = []

    # if level is 20 get word from a different level 50% of the time
    if session['completed'] == True and random.random() < 0.5:
        level = random.randint(1, 19)   
    #change to a lower level 20% of the time
    elif random.random() < 0.2 and level > 1:
        #get a random number between 1 and the current level
        level = random.randint(1, level)
    print("level: ", level)    
    # Get a random word entry for the current level
    level_words = words[str(level)]
    # print(level_words)
    # Ensure the new word is not in the previous words list
    word_entry = random.choice(level_words)
    while word_entry['english'] in session['previous_words']:
        word_entry = random.choice(level_words)

    correct_answer = word_entry['english']
    #get type of word of word_entry
    word_type = word_entry['type']

    # Update the previous words list, keeping size to 10
    session['previous_words'].append(correct_answer)
    if len(session['previous_words']) > 10:
        session['previous_words'].pop(0)
    # print(session['previous_words'])

    # Save the updated session
    session.modified = True

    # Generate choices including the correct answer and 3 random incorrect answers with the same tyep
    choices = [correct_answer] + random.sample(
        [entry['english'] for entry in level_words if entry != word_entry and entry['type'] == word_type], 3
    )   

    random.shuffle(choices)
    return word_entry['tajik'], choices, correct_answer

# Initialize the game state
@app.route('/')
def index():
    # print("in index")
    reset_game_if_new_day()
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/tajik-vocab', methods=['POST', 'GET'])
def tajik_vocab():
    # Reset the game state if it is a new day
    reset_game_if_new_day()
    # Initialize session variables if there is no session
    if not session:
        initialize_session_variables()
    #logger.info(f"Game state: {session}")

    # see how user got to page
    referer = request.headers.get("Referer")
    logger.info(f"User came from: {referer}")  
    # log if it is post or get request
    logger.info(f"Request method: {request.method}")

    # If GET request, initialize the game state and get the first question
    if request.method == 'GET':
        # Check if the user is being redirected
        # checks if the session contains a key named 'redirected' with a value of True
        if session.get('redirected', False):
            session['redirected'] = False
        else:
            # set streak to zero
            session['streak'] = 0

        word, choices, correct_answer = get_new_question(session['level'])
        return render_template('vocab.html', word=word, choices=choices, correct_answer=correct_answer, level=session['level'], score=session['score'], streak=session['streak'], highest_streak=session['highest_streak'])
    
    # If POST request, check the user's answer and update the game state
    if request.method == 'POST':
        # print(request.form)
    
        user_answer = request.form['answer']
        correct_answer = request.form['correct_answer']
        word = request.form['word']

        if 'completed' not in session:
            session['completed'] = False
        
        # Check if the user's answer is correct
        if user_answer == correct_answer:
            session['streak'] += 1
            if session['streak'] > session['highest_streak']:
                session['highest_streak'] = session['streak']
            session['score'] += 1
            flash('Correct!', 'success')
            print("streak", session['streak'])
            print("highest streak", session['highest_streak'])

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
            # Give correct answer in a flash in the form english: tajik
            flash(f'Incorrect. {word} : {correct_answer}', 'danger')
           
        # Set the session variable to indicate that the user has answered a question
        session['answered_question'] = True
        # Set the session variable to indicate that the user is being redirected
        session['redirected'] = True
        # Redirect back to the same route route to get a new question
        return redirect(url_for('tajik_vocab'))

if __name__ == '__main__':
    app.run(debug=True)