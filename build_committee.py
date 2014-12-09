from preprocessor import processes, transform

quotes_file = open('data/db_v1_no_dupes.tsv')
quotes = [line.split('\t') for line in quotes_file.readlines()]
for process in processes:
	print process
	new_file = open('data/' + process + '.db_v1_no_dupes.tsv', 'a')
	for quote in quotes:
		s = transform(quote[1], process)
		if s != '':
			new_file.write(quote[0] + '\t' + s + '\n')
	new_file.close()
quotes_file.close()

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.svm import SVC, LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
import pickle

param_sets = [
	'tokens_meaningful.1.1.svc_rbf.0',
	'tokens_meaningful.1.1.nb.0',
	'tokens_meaningful.1.1.93nn.0',
	'parts_all.1.3.svc_lin.-1',
	'tokens_adj.1.1.svc_rbf.-1',
	'tokens_adv.1.1.svc_rbf.-1',
	'tokens_all.1.2.svc_lin.-1',
	'tokens_noun.1.1.svc_rbf.-1',
	'tokens_other.1.1.svc_rbf.-1',
	'tokens_pron.1.1.svc_rbf.-1',
	'tokens_verb.1.1.svc_rbf.-1'
]

prefs = ['IE', 'NS', 'FT', 'JP']

for param_set in param_sets:
	params = param_set.split('.')
	print 'building ' + str(params)
	lang_process = params[0]
	ngram_range = (int(params[1]), int(params[2]))
	clf_type = params[3]
	C = 10 ** int(params[4])
	quotes_file = open('data/' + lang_process + '.db_v1_no_dupes.tsv')
	quotes = [line.split('\t') for line in quotes_file.readlines()]
	quotes_file.close()
	for quote in quotes:
		quote[1] = quote[1].replace('\n', '')
	quotes_data = [quote[1] for quote in quotes]
	print 'train[0] = ' + quotes_data[0]
	for i in range(0, 4):
		quotes_target = [quote[0][i] for quote in quotes]
		cv = ('cv', CountVectorizer(ngram_range = ngram_range))
		xform = ('xform', TfidfTransformer())
		clf = None
		if clf_type == 'svc_rbf':
			clf = ('clf', SVC(kernel = 'rbf', C = C))
		elif clf_type == 'nb':
			clf = ('clf', MultinomialNB())
		elif clf_type == '93nn':
			clf = ('clf', KNeighborsClassifier(n_neighbors = 93))
		elif clf_type == 'svc_lin':
			clf = ('clf', LinearSVC(C = C))
		pipeline = Pipeline([cv, xform, clf])
		clf_name = param_set + '.' + prefs[i]
		print 'fitting ' + clf_name
		pipeline.fit(quotes_data, quotes_target)
		s = pickle.dumps(pipeline)
		clf_file = open('committee/' + clf_name + '.pkl', 'w')
		clf_file.write(s)
		clf_file.close()
