# passwordchecker
Simple Python program that checks passwords against the Have I Been Pwned database. Includes speech recognition option.

This program uses the Have I been Pwned API to check any string input against the database of hacked passwords. It uses SHA1 hashing and K-Anonymity when sending queries and receiving results. 

The speech recognition option uses the library SpeechRecognition and its built-in Google Speech API. Note that the default API key is the test key and not intended for production. Please register a personal API key (limit to 50 queries/day) for production use. 

REQUIRED LIBRARIES

You will need to install the following libraries: 

For a Mac:

pip install requests

pip install SpeechRecognition

brew install portaudio

pip install pyaudio

There are a number of known complications between SpeechRecognition and PyAudio. Info on the library and troubleshooting here: https://pypi.org/project/SpeechRecognition/

If you encounter problems with portaudio or pyaudio try running 'brew doctor' in your terminal and/or updating Xcode. 
