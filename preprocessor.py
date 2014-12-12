import os, nltk
from nltk.downloader import Downloader
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize, pos_tag, map_tag

nltk_packages = [
	'punkt',
	'maxent_treebank_pos_tagger',
	'universal_tagset',
	'wordnet'
]
nltk_path = os.path.dirname(os.path.realpath(__file__)) + '/nltk'
nltk.data.path.append(nltk_path)
nltk_dl = Downloader(download_dir = nltk_path)
for package in nltk_packages:
	nltk_dl.download(package)

primary_tags = set(['NOUN', 'VERB', 'ADJ', 'ADV', 'PRON'])

processes = [
	'parts_all',
	'tokens_adj',
	'tokens_adv',
	'tokens_all',
	'tokens_dense',
	'tokens_noun',
	'tokens_other',
	'tokens_pron',
	'tokens_verb'
	]

expansions = {}
expansions["n't"] = 'not'
expansions["'m"] = 'am'
expansions["'re"] = 'are'
expansions["'ve"] = 'have'
expansions["'ll"] = 'will'

unexpandables = set(["'s", "'d"])

wnl = WordNetLemmatizer()

def map_token(token):
	if token in expansions:
		token = expansions[token]
	elif token in unexpandables:
		token = token.lstrip("'")
	token = token.lower()
	return token

def transform(doc):
	doc = word_tokenize(doc)
	for i in range(0, len(doc)):
		token = doc[i]
		token.rstrip("'")
		if not token in expansions and not token in unexpandables:
			token = token.lstrip("'")
		doc[i] = token
	doc = pos_tag(doc)
	doc = [(map_token(token), map_tag('en-ptb', 'universal', tag)) for token, tag in doc]
	doc_by_process = {}
	for process in processes:
		processed_doc = None
		if process == 'parts_all':
			processed_doc = [tag for token, tag in doc]
		elif process == 'tokens_all':
			processed_doc = [token for token, tag in doc]
		elif process == 'tokens_dense':
			tags = primary_tags - set(['VERB', 'ADV', 'PRON'])
			processed_doc = [wnl.lemmatize(token) for token, tag in doc if tag in tags]
		elif process == 'tokens_other':
			processed_doc = [token for token, tag in doc if tag not in primary_tags]
		else:
			tags = set([process.split('_')[1].upper()])
			processed_doc = [token for token, tag in doc if tag in tags]
		s = ''
		for i in range(0, len(processed_doc)):
			s += processed_doc[i]
			if i != len(processed_doc) - 1:
				s += ' '
		doc_by_process[process] = s
	return doc_by_process
