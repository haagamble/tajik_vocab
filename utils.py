# utils.py
from flask import session
from datetime import datetime
import logging
import random

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
    if 'language' not in session:
        session['language'] = 'taj_to_eng'
        logger.info("Session variable 'language' initialized")

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
        # Reset the game state with these default values
        session['score'] = 0
        session['streak'] = 0
        session['highest_streak'] = 0
        session['level'] = 1
        session['completed'] = False
        session['previous_words'] = []
        session['question_answered'] = False
        session['translation_direction'] = 'taj_to_eng'
        # Update the last played date as a string
        session['last_played'] = today.strftime('%Y-%m-%d')
    
    # logger.info(f"Last played date: {session['last_played']}")
    # logger.info(f"Today's date: {today}")   

def get_new_question(level, trdir, words):
    #try to get the word from the level and type and 3 other random choices
    max_retries = 10 # Maximum number of retries to get a new word
    for attempt in range(max_retries):
        try:
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
            # print("level: ", level)    
            # Get a random word entry for the current level
            level_words = words[str(level)]
            # print(level_words)
            # Ensure the new word is not in the previous words list
            
            word_entry = random.choice(level_words)
            while word_entry['english'] in session['previous_words']:
                word_entry = random.choice(level_words)

            # if language is taj_to_eng get the tajik word
            if trdir == 'eng_to_taj':
                word = word_entry['english']
                correct_answer = word_entry['tajik']
                language = 'tajik'
            else:
                word = word_entry['tajik']
                correct_answer = word_entry['english']
                language = 'english'

            #get type of word of word_entry
            word_type = word_entry['type']

            # Generate choices including the correct answer and 3 random incorrect answers with the same type
            possible_choices = [entry[language] for entry in level_words if entry != word_entry and word_entry['type'] == word_type]
            if len(possible_choices) < 3:
                logger.error(f"Not enough choices available for word type {word_type} at level {level}")
                continue
            choices = [correct_answer] + random.sample(possible_choices, 3)
            random.shuffle(choices)

            # Update the previous words list, keeping size to 10
            session['previous_words'].append(correct_answer)
            if len(session['previous_words']) > 10:
                session['previous_words'].pop(0)
            # print(session['previous_words'])

            # Save the updated session
            session.modified = True

            return word, choices, correct_answer
        
        except Exception as e:
            # Log the error and try again
            logger.error(f"Error getting new question: {e}: {correct_answer}")
            continue

    # If all retries fail, return None for all values
    logger.error("Max retries reached, returning None for new question")
    return None, None, None
