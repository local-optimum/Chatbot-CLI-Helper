#!/usr/bin/env python3

import openai
import sys
import re
import subprocess
import getpass
import json
import os

# Get the text following the bash command
command_output = ' '.join(sys.argv[1:])

# Save the command output as a variable
user_question = command_output

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


#API key check
API_KEY_FILE = 'api_key.json'
if os.environ.get("SNAP_USER_COMMON"):
    API_KEY_FILE = os.path.join(os.environ['SNAP_USER_COMMON'], 'api_key.json')
else:
    API_KEY_FILE = 'api_key.json'

#Prompt the user for their OpenAI API key
def get_api_key():
    print("To use this tool, you need to have an OpenAI API key. Create one at https://platform.openai.com/account/api-keys")
    while True:
        api_key = getpass.getpass('Enter your OpenAI API key: ')
        # Validate the API key by making a test request
        openai.api_key = api_key
        try:
            response = ask_question(user_question)
            # API key is valid, save it to a file
            with open(API_KEY_FILE, 'w') as f:
                json.dump({'api_key': api_key}, f)
            return api_key
        except openai.error.AuthenticationError:
            print("The API key provided is not recognized. Please try again.")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return None

#Load an API key that has already been submitted
def load_api_key():
    try:
        with open(API_KEY_FILE, 'r') as f:
            data = json.load(f)
            return data['api_key']
    except (FileNotFoundError, KeyError):
        return None

#Primary query being run
# Use the API key to make your OpenAI queries here
def run_query():
    api_key = load_api_key()
    if api_key is None:
        api_key = get_api_key()

    if api_key is None:
        print("API key not provided or valid. Exiting...")
        return

    # Use the API key to make your OpenAI queries here
    openai.api_key = api_key
    try:
        response = ask_question(user_question)

        # Print a tidied version of the response
        print(clean(response))

        # Save the output of the cleaned response
        output = str(clean(response))

        # Copy the output to the clipboard using xclip
        subprocess.run(['echo', output], stdout=subprocess.PIPE, shell=True)
        subprocess.run(['xclip', '-selection', 'clipboard'], input=output.encode('utf-8'), check=True)

        print("Command copied to clipboard")
    except openai.error.AuthenticationError:
        print("The API key has returned an authentication error. Replacing the API key file.")
        get_api_key()
        run_query()
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        
#Run the file!
run_query()
