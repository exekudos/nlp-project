The python file "sense_match.py" is in the project directory. It takes one command line argument that is the query word for which roleset and ontology matching has to be done.

Pre-requisite:
  - PyTrips
  - jsontrips
  - Propbank XML files
  - SpaCy

The propbank frame XML files that were used for testing are kept in the folder "propbank_frames" in the project directory. More XML frames from the propbank repository can be added from the following link:
https://github.com/propbank/propbank-frames/

Install spacy from pip using:
	pip install spacy

Install the corpus for spacy "en_core_web_md" using:
	python -m spacy download en_core_web_md

Syntax for running the sense matching file:
	python sense_match.py <query_word>
eg: python sense_match.py organize

The python file "role_match.py" should be in the project directory.

This file takes in 3 command line arguments 
  - The propbank word (sing)
  - Propbank Sense (sing.01)
  - TRIPS Sense (SING)

It is run as follows :
 
	python role_match.py sing sing.01 SING
