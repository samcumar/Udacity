# IPND Stage 2 Final Project

# You've built a Mad-Libs game with some help from Sean.
# Now you'll work on your own game to practice your skills and demonstrate what you've learned.

# For this project, you'll be building a Fill-in-the-Blanks quiz.
# Your quiz will prompt a user with a paragraph containing several blanks.
# The user should then be asked to fill in each blank appropriately to complete the paragraph.
# This can be used as a study tool to help you remember important vocabulary!

# Note: Your game will have to accept user input so, like the Mad Libs generator,
# you won't be able to run it using Sublime's `Build` feature.
# Instead you'll need to run the program in Terminal or IDLE.
# Refer to Work Session 5 if you need a refresher on how to do this.

# To help you get started, we've provided a sample paragraph that you can use when testing your code.
# Your game should consist of 3 or more levels, so you should add your own paragraphs as well!

sample = '''A ___1___ is created with the def keyword. You specify the inputs a ___1___ takes by
adding ___2___ separated by commas between the parentheses. ___1___s by default return ___3___ if you
don't specify the value to return. ___2___ can be standard data types such as string, number, dictionary,
tuple, and ___4___ or can be more complicated such as objects and lambda functions.'''

# The answer for ___1___ is 'function'. Can you figure out the others?

# We've also given you a file called fill-in-the-blanks.pyc which is a working version of the project.
# A .pyc file is a Python file that has been translated into "byte code".
# This means the code will run the same as the original .py file, but when you open it
# it won't look like Python code! But you can run it just like a regular Python file
# to see how your code should behave.

# Hint: It might help to think about how this project relates to the Mad Libs generator you built with Sean.
# In the Mad Libs generator, you take a paragraph and replace all instances of NOUN and VERB.
# How can you adapt that design to work with numbered blanks?

# If you need help, you can sign up for a 1 on 1 coaching appointment: https://calendly.com/ipnd1-1/20min/

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# The list "sub" contains all the blank variables that are to be substituted in this game. For each
# level, there is a string and the answer. The answer is a dictionary that contains key/value pair.
sub = ["___1___","___2___","___3___","___4___","___5___","___6___","___7___","___8___","___9___","___10___"]

string_1 = """___1___ stands for HyperText Markup Language. ___2___ stands for Cascading Style Sheets.
___3___ stands for Document Object Model. It is made of ___1___ elements in a tree-like structure and describes
how the ___1___ document is accessed by the ___4___"""
ans_1 = {"___1___": "HTML","___2___": "CSS","___3___": "DOM","___4___": "browser"}

string_2 = """The ___1___ matters as to which CSS ___2___ takes ___3___. ___4___s matter! If one
selector is more ___4___ than the others, then it takes ___3___."""
ans_2 = {"___1___": "order","___2___":"styling","___3___":"precedance","___4___": "specific"}

string_3 = """A ___1___ is created with the def keyword. You specify the inputs a ___1___ takes by
adding ___2___ separated by commas between the parentheses. ___1___s by default return ___3___ if you
don't specify the value to return. ___2___ can be standard data types such as string, number, dictionary,
tuple, and ___4___ or can be more complicated such as objects and lambda functions."""
ans_3 = {"___1___": "function","___2___": "arguments","___3___": "None","___4___": "list"}

string_4 = """___1___ means changing the value of an object. ___2___s support ___1___.
This is the second main difference between strings and ___2___s. Strings are ___3___. Lists are ___4___.
The key difference between ___4___ and ___3___ objects, is that once an object is ___4___,
you have to worry about other ___5___s that might refer to the same object.
You can change the value of that object and it affects not just ___5___ you think you changed,
but other ___5___s that refer to the same object as well.
"""
ans_4 = {"___1___": "Mutation","___2___": "list","___3___": "immutable","___4___": "mutable","___5___":"variable"}

# the list "level_list" is a list of lists where each element in the list is in the format of [level,string,answer]
# Global variables
first_level = 1
second_level = 2
third_level = 3
fourth_level = 4
level_pos = 0
string_pos = 1
ans_pos = 2
level_list = [[first_level,string_1,ans_1],[second_level,string_2,ans_2],[third_level,string_3,ans_3],[fourth_level,string_4,ans_4]]

# Global variable relating to the length of the list "level_list"
length_level_list = len(level_list)

# "word_in_pos" function is used to extract a blank value if it's contained within a string. The code is taken
# from the Mad-Libs generator.
def word_in_pos(word,variable):
    for pos in variable:
        if pos in word:
            return pos
    return None

# The function of "list_var_in_string" is that it takes in a string
def list_var_in_string(list):
    rep_blank = []
    for word in list:
        wordrep = word_in_pos(word,sub)
        if wordrep != None:
            if wordrep not in rep_blank:
                rep_blank.append(wordrep)
    return rep_blank

# Function "turns" determines the number of turns it takes to guess each blank value.
# Input into the function is the level chosen by the user and it returns the number of turns
# allowed to guess each blank value.
def turns(level):
    num_turns=1
    index = length_level_list
    while index > 0:
        index = index - 1
        num_turns += 2
        if level_list[index][level_pos] == level:
            return num_turns

# "display_levels" function lists out the levels available to play. The output of this function
# is a list of available levels to play.
def display_levels():
    length = length_level_list
    listoflevel = []
    print "These are the different levels of difficulty you can play: "
    for a in range(length):
        print level_list[a][level_pos]
        listoflevel.append(level_list[a][level_pos])
    print "Where " + str(level_list[0][level_pos]) + " is the easiest level and " + str(level_list[length_level_list-1][level_pos]) + " is the hardest level"
    return listoflevel

# The function "game_level" is where the main gameplay occurs. It returns back the
# completed string.
def game_level(string,ans,level):
    list_of_string = string.split()
    list_blank = list_var_in_string(list_of_string)
    for blank in list_blank:
        num_turns = turns(level)
        while num_turns > 0:
            print string,"\n"
            print "You have " + str(num_turns) + " turns left to guess"
            input = raw_input("What is the value for " + blank + ":")
            if input.lower() == ans[blank].lower():
                print "Correct!"
                string = string.replace(blank,ans[blank])
                num_turns = 0
            else:
                num_turns = num_turns - 1
                if num_turns == 0:
                    print "You've lost"
                    exit()
                print "Incorrect!! Try Again......"
    print "\n", "Congratulations! You've completed the sentence!", "\n"
    return string

# The function "play_game" calls the function "game_level". It determines the level and based on the level,
# it uses the list "level_list" to help determine the string and answer to use. This is used as input to the
# function "game_level".
def play_game():
    print "\n","Let's play the Fill-in-the-Blanks game"
    while True:
        which_level = display_levels()
        choice = "Enter level of difficulty to play ... or 0 to exit: "
        level = int(raw_input(choice))
        if level == 0:
            print "Exiting game"
            exit()
        while level not in which_level:
            level = int(raw_input(choice))
            if level == 0:
                print "Exiting game"
                exit()
        string = level_list[level-1][string_pos]
        ans = level_list[level-1][ans_pos]
        print game_level(string,ans,level)
        print "\n","Let's go again if you dare!!!"

play_game()
