from nltk import word_tokenize, pos_tag, map_tag
from nltk.stem import WordNetLemmatizer

univ_tags_primary = set(['NOUN', 'VERB', 'ADJ', 'ADV', 'PRON'])
univ_tags = univ_tags_primary.union(set(['DET', 'ADP', 'NUM', 'CONJ', 'PRT', '.', 'X']))

processes = [
	'parts_all',
	'tokens_adj',
	'tokens_adv',
	'tokens_all',
	'tokens_meaningful',
	'tokens_noun',
	'tokens_other',
	'tokens_pron',
	'tokens_verb'
	]

lemmatizer = WordNetLemmatizer()

def transform(doc, process):
	doc = pos_tag(word_tokenize(doc))
	doc = [(token, map_tag('en-ptb', 'universal', tag)) for token, tag in doc]
	if process == 'parts_all':
		doc = [tag for token, tag in doc]
	elif process == 'tokens_adj':
		tags = set(['ADJ'])
		doc = [token for token, tag in doc if tag in tags]
	elif process == 'tokens_adv':
		tags = set(['ADV'])
		doc = [token for token, tag in doc if tag in tags]
	elif process == 'tokens_all':
		tags = univ_tags
		doc = [token for token, tag in doc if tag in tags]
	elif process == 'tokens_meaningful':
		tags = univ_tags_primary - set(['VERB', 'ADV', 'PRON'])
		doc = [lemmatizer.lemmatize(token) for token, tag in doc if tag in tags]
	elif process == 'tokens_noun':
		tags = set(['NOUN'])
		doc = [token for token, tag in doc if tag in tags]
	elif process == 'tokens_other':
		tags = univ_tags - univ_tags_primary
		doc = [token for token, tag in doc if tag in tags]
	elif process == 'tokens_pron':
		tags = set(['PRON'])
		doc = [token for token, tag in doc if tag in tags]
	elif process == 'tokens_verb':
		tags = set(['VERB'])
		doc = [token for token, tag in doc if tag in tags]
	s = ''
	for i in range(0, len(doc)):
		s += doc[i]
		if i != len(doc) - 1:
			s += ' '
	doc = s
	return doc
