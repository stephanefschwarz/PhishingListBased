import pandas as pd
import numpy as np
import json

def command_parser():

	parser = argparse.ArgumentParser(description = __doc__)

	parser.add_argument('--labelstud', '-l', dest='labelstud', 
						required=True, help='Path for the labelstud json file.')

	parser.add_argument('--path_dest_txt', '-d', dest='path_dest_txt', 
						required=True, default=None, help='Spacy dataset txt format')

	parser.add_argument('--spacy_model', '-s', dest='spacy_model', 
						required=True, help='Path for the spacy model.')

	args = parser.parse_args()

	return args

def labelstud_to_spacy(path_to_json, path_dest_txt):

	"""	
	Converts labelstud file format (json) to spacy format (txt)


	Parameters
	----------
	path_to_json : str
	    path to the labelstud output file
	path_dest_txt : str
	    path to save the new file converted

	Returns
	-------
	list
	    list in the format to train a spacy model
	"""

	# path_to_json = '/content/drive/MyDrive/datasets_movile/result.json'
	# path_dest_txt = '/content/drive/MyDrive/datasets_movile/train_dataset_spacy.txt'

	with open(path_to_json) as json_file:
		file = json.load(json_file)

	train_data = []
	for sample in file:

		sms = sample['data']['messagetext']
		entities = []

		for entity in sample['completions'][0]['result']:

			start = entity['value']['start']
			end = entity['value']['end']
			label = entity['value']['labels'][0]

			entities.append((start, end, label))

		train_data.append((sms, {'entities':entities}))


	# Save model

	with open(path_dest_txt, 'w') as to_scapy:		
		json.dump(train_data, to_scapy)

	return train_data


def train_scapy_model(dataset, epochs, save=None):

	"""	
	Train scapy model using the new data file


	Parameters
	----------
	dataset : list
	    scapy dataset generaly it is a list
	epochs : ing
	    number of iteration to train the model
    save : str
    	path to save the trained model

	Returns
	-------
	spacy model
	    a trained spacy model
	"""

	blank_lang = spacy.blank('pt') # Creating a blank language class

	if 'ner' not in blank_lang.pipe_names:

		ner = blank_lang.create_pipe('ner')
		blank_lang.add_pipe(ner, last=True)

	# Add entity labels
	for _, annotations in dataset:
		for entity in annotations.get('entities'):
			ner.add_label(entity[2])

	# Disable other pipes during training
	other_pipes = [pipe for pipe in blank_lang.pipe_names if pipe != 'ner']
	# Train only NER
	with blank_lang.disable_pipes(*other_pipes):

		optimizer = blank_lang.begin_training()
		for epoch in range(epochs):

			random.shuffle(dataset)

			losses = {}

			for text, annotations in dataset:

				blank_lang.update([text], [annotations], 
								drop=0.2, sgd=optimizer, 
								losses=losses)

			if epoch%20==0:
			print('Epoch {} | loss: {}'.format(epoch, losses))

	if save != None:

		# save = '/content/drive/MyDrive/datasets_movile/phishing_NER'
		blank_lang.to_disk(save)

	return blank_lang


if __name__ == '__main__':

	args = command_parser()

	dataset = labelstud_to_spacy(args.labelstud, args.path_dest_txt)

	nlp = train_scapy_model(dataset, 100, args.spacy_model)