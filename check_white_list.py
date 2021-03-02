import spacy
import argparse
import tldextract
import numpy as np
import pandas as pd
from difflib import SequenceMatcher


'''
White list format: save in a PICKLE file using these header:

|key_words 						 |organization	 |site		   |
|bb, banco do brasil, card credit|Banco do Brasil|www.bb.com.br|
|apple, iphone, macbook			 |Apple          |www.apple.com|
'''

'''
to_test file format: save in a PICKLE file using these header:

|sms	     |site		   		  |
|SMS message'|'https://www.url.com|
|Apple lnc. Su lPhone 8 plus 64gb red perdido ha sido retenido en AppIe Store. Verifique caso:0012853 en https://www.icIoud.com.ar/g7yS'|'https://www.icIoud.com.ar/g7yS'|


'''

def command_parser():

	parser = argparse.ArgumentParser(description = __doc__)

	parser.add_argument('--white_list', '-w', dest='WHITE_LIST_PATH', 
						required=True, help='Path for the pickle white list.')

	parser.add_argument('--model_path', '-m', dest='model_path', 
						required=True, default=None, help='Spacy model path to detect key words from the sms.')

	parser.add_argument('--to_test', '-w', dest='to_test_file', 
						required=True, help='Path for the pickle to test file.')

	parser.add_argument('--output_file', '-o', dest='output_file', 
						required=False, help='Log file path.')

	args = parser.parse_args()

	return args


def check_white_list(sms, site):
	"""	
	Check the presence of a organization in the white list


	Parameters
	----------
	key_words : list of string
	    List of key words
	site : str
	    an URL

	Returns
	-------
	Boolean
	    True if the site is legitimate and false otherwise
	"""

	domain = get_url_domain(site)

	white_list = pd.read_pickle(WHITE_LIST_PATH)

	key_words = find_sms_key_words(sms, model_path)

	matches = white_list[white_list.key_words.apply(lambda key_words_white: find_key_word_matches(key_words, key_words_white))]

	if matches.empty:

		print('Matches not found\n')

		return 'Matches not found'

	domains = [get_url_domain(url) for url in matches.site]

	# Test first based on the URL domain
	if domain in domains:

		print('Legitimate site\n')

		return 'Legitimate site.'

	print('Potential phishing site\n')

	return 'Potential phishing site.'



def find_sms_key_words(sms, model_path):
	"""	
	Returns all key words found in the sms


	Parameters
	----------
	sms : str
	    the entire sms message

    model_path : str
	    the path to the trained sms model


	Returns
	-------
	list of strings
	    a list of key words
	"""

	nlp = spacy.load(model_path)

	key_words = [ent.text for ent in nlp(sms.lower()).ents]

	return key_words




def find_key_word_matches(key_words, white_list, use_similarity=True):
	"""	
	Returns true if any key_words is in the white list


	Parameters
	----------
	key_words : list of str
	    pandas lambda key_words for the apply method

    white_list : list of URLs
	    a list of knowing URLs

    use_similarity : boolean
	    if True, all the similar key words will be considered too


	Returns
	-------
	list of boolean
	    True where the key word was found
	"""

	# return any(key_word in white_list for key_word in key_words)
	return any(get_similarity(key_words, wl_key_word) for wl_key_word in white_list)



def get_url_domain(url):
	"""	
	Returns the URL domain


	Parameters
	----------
	url : str
	    an URL

	Returns
	-------
	string
	    the URL domain
	"""
	
	request = tldextract.extract(url)

	return request.domain


def get_similarity(sentence_a, sentence_b, threshold=0.59):

	"""	
	Returns if a list of key words (sentence_a) is similar to a key word (sentence_b)

	Parameters
	----------
	sentence_a : list of string
	    a list of string to compare with sentence_b

    sentence_b : string
    	another string to compare with sentence_a

	threshold : float [0, 1]
		similarity threshold, 0 when they are not similar
		closer to 1 it is similar

	Returns
	-------
	~float~
	   ~the similarity score between the sentences~
    boolean
    	True if there exists at least one similar key word

	"""
	for key in sentence_a:

		if SequenceMatcher(None, key, sentence_b).ratio() > threshold:

			return True

	return False

# ==========================================================
# ==========================================================

args = command_parser()

WHITE_LIST_PATH = args.WHITE_LIST_PATH
model_path = args.model_path


dataset = pd.read_pickle(args.to_test)
diagnosis = []


for idx, sample in dataset.iterrows():

	diagnosis.append(check_white_list(sample['sms'], sample['site']))

if args.output_file != None:

	dataset['diagnosis'] = diagnosis

	dataset.to_pickle(args.output_file)


"""
Run example

check_white_list('Apple lnc. Su lPhone 8 plus 64gb red perdido ha sido retenido en AppIe Store. Verifique caso:0012853 en https://www.icIoud.com.ar/g7yS', 'https://www.icIoud.com.ar/g7yS')
"""