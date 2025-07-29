import pandas as pd
import itertools
from collections import Counter


valid_guesses = pd.read_csv('valid_guesses.csv')
valid_solutions = pd.read_csv('valid_solutions.csv')

# common set

correct_letters = [None, None, None, None, None]
displaced_letters = [[], [], [], [], []]
all_displaced_letters = []
incorrect_letters = []
letter_value = dict()

def is_valid_answer(word):
    global correct_letters, displaced_letters, incorrect_letters, all_displaced_letters
    displaced_count = 0
    for idx, letter in enumerate(word):
        if letter in incorrect_letters: 
            # word contains a letter that was eliminated
            return False
        if letter in displaced_letters[idx]: 
            # word contains a letter in a spot that was eliminated
            return False
        if correct_letters[idx] != None and correct_letters[idx] != letter: 
            # if we know what letter is at the index of a correct answer, but different in the word 
            return False
        if letter in all_displaced_letters:
            displaced_count += 1

    return displaced_count >= len(all_displaced_letters)

def filter_searched_letters(word):
    global correct_letters, displaced_letters, incorrect_letters, all_displaced_letters
    ans = []
    for letter in word:
        if not letter in correct_letters and not letter in all_displaced_letters and not letter in incorrect_letters:
            ans.append(letter)
    return ans


def word_score(word):
    word_score = 0
    letters = []
    for letter in word:
        if not letter in letters:
            word_score += letter_value.get(letter, 0)
            letters.append(letter)
    return word_score

print(valid_solutions)
for round in range(6):
    print('Enter your guess:')
    guess = input()
    print('Enter the results as 5-digit long number composed of 0, 1, 2:')
    match = input() # 0 - wrong, 1 - wrong place, 2 - correct
    
    # add letters to common set
    for idx, m in enumerate(match):
        if m == '0':
            if not guess[idx] in incorrect_letters:
                incorrect_letters.append(guess[idx])
        if m == '1':
            if not guess[idx] in displaced_letters[idx] and not guess[idx] in correct_letters:
                displaced_letters[idx].append(guess[idx])
            if not guess[idx] in all_displaced_letters and not guess[idx] in correct_letters:
                all_displaced_letters.append(guess[idx])
        if m == '2':
            correct_letters[idx] = guess[idx]

    #print(valid_solutions[valid_solutions['word'].apply(is_valid_answer)])
    valid_solutions = valid_solutions[valid_solutions['word'].apply(is_valid_answer)]
    
    # based on available solutions, we want to find a word that would be able to eliminate most of them
    # we want to find a list of words that have letters that commonly appear in valid solutions, but not in our sets
    searched_letters = valid_solutions['word'].apply(filter_searched_letters).tolist()
    searched_letters = list(itertools.chain.from_iterable(searched_letters))
    letter_value = dict(sorted(dict(Counter(searched_letters)).items(), key=lambda x:x[1], reverse=True))

    print('letter occurences in possible solutions:')
    print(letter_value)
    valid_guesses['score'] = valid_guesses['word'].apply(word_score)

    print('best next guess for more data:')
    print(valid_guesses.sort_values(by='score', ascending=False)['word'].iloc[0])
    print('possible answers:')
    print(valid_solutions)

