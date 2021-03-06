from pickle import FALSE
import copy
from tqdm import tqdm
import time
import random

#Simple function to count number of a specific letter in a word
def num_of(a,word):
    total = 0
    for x in word:
        if x == a:
            total += 1
    return total

#Simple function to count number of a specific letter in a list
def num_of_list(a, listz):
    tot = 0
    for x in listz:
        if x == a:
            tot += 1
    return tot

#This function will calculate if a guess is possible to be the answer, given the constraints we allready know. It returns False if impossible, and True if possible
#known_place is a list of the letters we know and their place. There is a 0 instead of a letter, if we don't know what is in that position. EG: [0,"e",0,0,0]
#known is a list of the letters we do know, it includes those of known_place. It works with repeats. EG ["e","d","k"]
#not_in is  a list of letters we know are not in the answer.
#not_there is a list containing 5 lists. The first list shows what letters cannot be in the first letter of the answer. EG: [["a"],["r"],["i"],["s"],["e"]]
def is_possible(guess, known_place, known, not_in, not_there):
    for x in range(0,5):
        if guess[x] in not_in:
            return False
        if guess[x] in not_there[x]:
            return False
        if guess[x] != known_place[x] and known_place[x] != 0:
            return False
    for x in known:
        if x not in guess:
            return False
        num = num_of(x, known)
        if num == 2:
            if num_of(x,guess) < 2:
                return False
    return True

#This function will return the number of words the answer COULD be, given a set of constraints. 
def possible_option_counter(known_place, known, words, not_in, not_there):
    counter = 0
    for x in words:
        if is_possible(x, known_place, known, not_in,not_there):
            counter += 1
    return counter

#Given a guess you make, and what the REAL answer is. This will update known_place, known, not_in, temp_not_there to reflect the extra information we gain.
def new_info(guess, answer,known_place, known, not_in, temp_not_there):
    lcv = 0
    while lcv < 5:

        #If you guessed the right letter in the right place it updates the known_place
        if guess[lcv] == answer[lcv]:
            known_place[lcv] = guess[lcv]

        #If you guessed the right letter in the wrong place it updates known. If it is not allready there
        if guess[lcv] in answer and guess[lcv] not in known:
            known.append(guess[lcv])
        
        #This fixes the repeating problem, and will make sure you get two letters in known, if you should.
        if num_of(guess[lcv], answer) == 2 and num_of(guess[lcv], guess) == 2:
            num_known = num_of_list(guess[lcv], known)
            if num_known == 0:
               known.append(guess[lcv])
               known.append(guess[lcv])
            elif num_known == 1:
                known.append(guess[lcv])
        
        #Updates not_in for letters not in the real answer
        if guess[lcv] not in answer:
            not_in.append(guess[lcv])

        #Updates not_there, if you enter a letter in a place and it is not green, you know that letter is not there
        if known_place[lcv] == 0:
            temp_not_there[lcv].append(guess[lcv])
        lcv += 1


#This function should calculate and return the best guess you can make. It will loop through all the possible guesses you can make, and then loop through all of the answers that it could be.
#With each guess, and answer you learn new information. This information is then used to calculate how many potential posssible words the answer could be, if we were had that specific answer 
#and guess. An example of this would be guess=mould, real_answer = could. We learn it ends with ould, but is not mould. The potential answers are still could, would, hould so that gets a score of 3
#We don't know the real answer, so it does this for every single possible answer. if it is could, 3, if the real answer is mould=0, real_answer= leave then we get like 400. (because we don't learn much)
#For each possible answer we get a number. Then it adds all these numbers together to get a score for that specific guess. The lowest guess wins. And is the best answer. 
def go(known_place,known,not_in, not_there, five_letter_words):

    #Sets the best_word, and the best_word_score to something dumb. It should replace these first time with a real guess. 
    best_word = "BADBAD"
    best_word_score = 100000000000
    words_copy = copy.deepcopy(five_letter_words)

    #Here, we are looping through all of the guesses that you could make. It only will guess something if it could be the correct answer, with the information that we have. 
    for guess in (words_copy):
        if is_possible(guess, known_place, known,not_in, not_there):

            #The answers_still_possible vairble is the most important one. It keeps track of all of the answers that are possible from each guess, and answer. 
            answers_still_possible = 0
            
            #tqdm will just make the bar chart. The shuffle here, is for optimization so it won't have to calculate ALL of the potential answers,
            #after 500 it can estimate how bad a guess is, and then exit the loop early
            random.shuffle(five_letter_words) 
            shuffled_words = tqdm(five_letter_words)
            lcv = 0

            #This loops through all of the words,  and enters the inner loop if the answer, is possible to be the answer. We do not care if the potential answer cannot be the answer
            for potential_answer in shuffled_words:
                if is_possible(potential_answer, known_place, known,not_in, not_there):

                    #simply deepcopies these information we have available, so it can be updated with new_info. The information we have, will change based on the answer, so 
                    #if they were not deep copied, changing the potential answer would ruin everything.
                    temp_known_place = copy.deepcopy(known_place)
                    temp_known = copy.deepcopy(known)
                    temp_not_in = copy.deepcopy(not_in)
                    temp_not_there = copy.deepcopy(not_there)
                    new_info(guess, potential_answer, temp_known_place, temp_known,temp_not_in, temp_not_there)

                    #Given information we gain from a guess, there is still multiple answers it could be. This will find all of these, add them together and add it to 
                    #answers_still_possible. To get a perfect number, we need to go through every possible potential answer that exists. 
                    answers_still_possible += possible_option_counter(temp_known_place, temp_known, five_letter_words,temp_not_in,temp_not_there)

                    #Sets the description for the bar chart. It is dynamic
                    shuffled_words.set_description("{}={} BEST: {}={}".format(guess, answers_still_possible, best_word, round(best_word_score)))

                    #If answers_still_possible > the best one we have, we know it is a bad guess so we exit
                    #If we estimate that its a bad guess after 500 different random answers its probably a bad guess so we give up.
                    if answers_still_possible > best_word_score or (lcv == early_fin_check and answers_still_possible > best_word_score * (num_of_words/early_fin_check) * early_fin_confidence):
                        answers_still_possible = 100000000
                        break
                lcv += 1
            
            #Here, we are updating the best_word_score if it is in fact the best word. The best word should have the least number of potential answers.
            if answers_still_possible < best_word_score:
                best_word_score = answers_still_possible
                best_word = guess
    return best_word

#This vairable stores how many potential answers you need to see before it will try to exit early. Should be over 100. 
early_fin_check = 500

#This vairable stores how far OVER the best score you have to be to exit early MUST BE OVER 1. 
early_fin_confidence = 1.3

#You can choose which wordlist to use. They are both in text files
#The num_of_words is used in the early finish
inputs = input("Enter a to use the list of answers for wordle (2000 words), Enter e for all words you can enter (10,000): ")
if inputs == "E":
    f = open('wordlewords.txt','r')
    num_of_words = 2315
else:
    f = open('wordle_only_answers_list.txt','r')
    num_of_words = 10000
temp = f.readlines()
f.close()
five_letter_words = [word.strip() for word in temp]

#You can choose which word to start with
print("(in order) The best words to start with are:")
print("soare, raise, alter, arise, ")
print("")
starts = input("Enter the word you want to start with: ")
done_words = [starts]
not_there = [[],[],[],[],[]]
known_place_list = [0,0,0,0,0]

while True:
    #Enters information we know
    known_place = input("Example (0ea00). Enter the letters that you know the place of. Use a 0 inplace of unknown letters: ")
    known = input("Enter the letters that you know in any order: ")
    not_in = input("Enter the letters that are not in in any order: ")
    print(" ")

    #Turns the infromation we know into the right format of lists
    known_place_list = []
    for x in known_place:
        if x == "0":
            known_place_list.append(0)
        else:
            known_place_list.append(x)
    
    if 0 not in known_place_list:
        break

    known_list = []
    for x in known:
        known_list.append(x)
    not_in_list = []
    for x in not_in:
        not_in_list.append(x)

    #Here, we update the not_there list. Which is slightly different than the others
    recent_word = done_words[-1]
    lcv = 0
    for x in recent_word:
        if known_place_list[lcv] == 0:
            not_there[lcv].append(recent_word[lcv])
        lcv += 1
    print("not there", not_there)
    time.sleep(2)

    #Finds the best word and tells you
    BW = go(known_place_list,known_list,not_in_list, not_there,five_letter_words)
    done_words.append(BW)
    print("THE BEST WORD TO USE IS: ",BW)
    print("")