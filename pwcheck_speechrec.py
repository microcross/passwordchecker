import requests
import hashlib
import sys
import os
import speech_recognition as sr


def pwned_api_check(password):
    # hashes passwords before sending to haveibeenpwned leveraging SHA1 & K-Anonymity
    # sends first 5 char through API, preserves tail for later lookup
    sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    frist5_char, tail = sha1password[:5], sha1password[5:]
    response = request_api_data(frist5_char)

    return get_password_leaks_count(response, tail)

def request_api_data(query_char):
    # Provide password using SHA1 hash, only first 5 chars.
    # Receives back a list of hashes & counts where first 5 matched (but only excludes first 5 char from string for K-Anonymity)
    url = 'https://api.pwnedpasswords.com/range/' + query_char
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f'Error fetching: {res.status_code}, check API and try again')
    return response


def get_password_leaks_count(response, hash_to_check):
    # Splits all returned hashes and checks tail (hash_to_check) for match
    found_hashes = (line.split(':') for line in response.text.splitlines())
    for h, count in found_hashes:
        if h == hash_to_check:
            return count
    return 0


def pw_result(count, password):
    # Prints results of the password checker for user
    if count:
        print(f'\'{password}\' was found {count} times. I recommend you change this password anywhere you\'ve used it.')
    else:
        print(f'\'{password}\' was not found. Safe for now!')


def recognize_speech(recognizer, microphone):
    """Speech to text from `microphone`.

    Returns a dictionary:
    "success": a bool showing if the API request was successful
    "error":   This contains a string of any error that occurs
                with the API or recognizing input. 'None' if no error
    "transcription": `None` if error occurs,
               otherwise a string containing the APIs transcribed text
    """
    # checks the types of the recognizer and microphone
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Say something!")
        audio = recognizer.listen(source)
        print("Got it! Processing...")

    # response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # provide response and errors if any
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response

# OPTIONAL SPEECH VERSION
# This version of the code allows the user choose between speech-to-text or manual entry
# If manual, user can input as many passwords as they'd like to check
# Their inputs are put into a file which is then read to extract and test each password iteratively
# The file is deleted at the end of the program prevent exposed passwords
# Or if they choose speech-to-text they can check one PW at a time (and see what the program thinks it hears)
def main():
    print("\n**********************************************************************************************************************\n"
          "* Welcome to the password checker. You will be prompted to enter any password that you'd like to check against the   *\n"
          "* database maintained by haveibeenpwned.com. If you don't want to trust this program with your passwords (and you    *\n"
          "* you shouldn't trust anyone with them) then use examples like 'password', 'test', '123', etc.                       *\n"
          "* Everything sent via the API is encrypted using SHA1 and K-Anonymity.                                               *\n"
          "* All entries will be deleted upon program completion.                                                               *\n"
          "**********************************************************************************************************************\n")
    speech_bol = input("You can either use speech-to-text or manually type your responses. Type Y for speech-to-text or N for manual entry: ")

    if speech_bol.lower() == 'n':
        file = open('user_input_pw.txt', 'w+')
        while True:
            pw = input("Please type a password to check and then press enter. You can keep adding more until you type 'done' when finished: ")
            if pw.lower() == 'done':
                file.close()
                break
            else:
                file.write(f'{pw}\n')

        file = open('user_input_pw.txt', 'r')
        lines = file.read().splitlines()

        for password in lines:
            count = pwned_api_check(password)
            pw_result(count, password)
        os.remove('user_input_pw.txt')
        return "Password check is complete and password inputs have been deleted."

    elif speech_bol.lower() == 'y' :
        print('Starting Speech Recognition')
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        pw = recognize_speech(recognizer, microphone)
        if pw['transcription']:
            print(f"You said: {pw['transcription']}")
        if not pw['success']:
            print("I couldn't understand that. Please restart\n")
        
        # if there was an error, stop the program
        if pw['error']:
          print(f"ERROR: {pw['error']}")

        count = pwned_api_check(pw["transcription"])
        pw_result(count, pw["transcription"])

        return "Password check is complete and password inputs have been deleted."

    else:
        print('Your response was not recognized. Please restart the program.')



if __name__ == '__main__':
    sys.exit(main())