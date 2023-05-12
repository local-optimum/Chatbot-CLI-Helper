#!/usr/bin/env python3

import openai
from apikey import key
import sys
import subprocess
import re
import pyperclip

# Get the text following the bash command
command_output = ' '.join(sys.argv[1:])

# Save the command output as a variable
user_question = command_output

openai.api_key = key

# Define a function to send a question and get a response from OpenAI
def ask_question(question):
    # Define the chat conversation
    conversation = [
        {'role': 'system', 'content': 'You provide terminal prompts for Ubuntu linux users. Respond with a bash command only on one line with no explanatory text.'},
        {'role': 'user', 'content': question}
    ]

    # Send the chat conversation to OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )

    # Get the response from OpenAI API
    answer = response['choices'][0]['message']['content']

    return answer

def clean(sentence):
    backtick_pattern = r"`+(.*?)`+"  # Regular expression pattern to match backticks and content
    
    match = re.search(backtick_pattern, sentence)
    if match:
        return match.group(1).strip()
    else:
        return sentence



# Call the ask_question function with the user's question
response = ask_question(user_question)
pyperclip.copy(str(clean(response)))

# Print the response from OpenAI
print(clean(response))
print("Command copied to clipboard")



# Function to prompt the user and execute the command
def execute_command(command):
    # Prompt the user to execute the command
    choice = input(f"Do you want to run the command? (Y/n) ")

    if choice.lower() == "y":
        # Execute the command
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            # Handle any errors that occur during command execution
            print("Command execution failed.")
            print("Error:", e)
            return None
    else:
        print("Command execution skipped.")

# Get the command
# bash_command = clean(response)

# Prompt the user to execute the command
# execute_command(bash_command)