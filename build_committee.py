from preprocessor import processes, transform

if __name__ == '__main__':
	quotes_file = open('data/db_v1_no_dupes.tsv')
	quotes = [line.split('\t') for line in quotes_file.readlines()]
	processed_files = {}
	for process in processes:
		processed_files[process] = open('data/db_v1_no_dupes.' + process + '.tsv', 'w')
	for quote in quotes:
		quote_by_process = transform(quote[1])
		for process in processes:
			s = quote_by_process[process]
			if s != '':
				processed_files[process].write(quote[0] + '\t' + s + '\n')
	for process in processes:
		processed_files[process].close()
	quotes_file.close()

import pickle, numpy, time, warnings
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.svm import SVC, LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV

warnings.simplefilter('ignore', RuntimeWarning)

param_sets = [
	'svc_rbf_weighted.tokens_all',
	'svc_rbf_weighted.parts_all',
	'svc_rbf_weighted.tokens_dense',
	'nb_weighted.tokens_all',
	'nb_weighted.parts_all',
	'nb_weighted.tokens_dense',
	'93nn_weighted.tokens_all',
	'93nn_weighted.parts_all',
	'93nn_weighted.tokens_dense'
]

prefs = ['IE', 'NS', 'FT', 'JP']

priors = {}
priors['IE'] = [0.507, 0.493]
priors['NS'] = [0.267, 0.733]
priors['FT'] = [0.598, 0.402]
priors['JP'] = [0.541, 0.459]

classes = []
for pref in prefs:
	for c in pref:
		classes.append(c)

class_to_int = {}
for pref in prefs:
	class_to_int[pref[0]] = 0
	class_to_int[pref[1]] = 1

int_to_class = {}
for pref in prefs:
	int_to_class[pref] = {}
	int_to_class[pref][0] = pref[0]
	int_to_class[pref][1] = pref[1]

def analyzer(doc):
	return doc.split()

if __name__ == '__main__':
	for param_set in param_sets:
		params = param_set.split('.')
		print '>> building ' + str(params) + ' <<'
		clf_type = params[0]
		lang_process = params[1]
		quotes_file = open('data/db_v1_no_dupes.' + lang_process + '.tsv')
		quotes = [line.split('\t') for line in quotes_file.readlines()]
		quotes_file.close()
		for quote in quotes:
			quote[1] = quote[1].replace('\n', '')
		quotes_data = [quote[1] for quote in quotes]
		print 'data[0] = ' + quotes_data[0]
		print '--'
		for i in range(0, 4):
			clf_name = param_set + '.' + prefs[i]
			print 'training ' + clf_name
			start_time = time.time()
			quotes_target = [class_to_int[quote[0][i]] for quote in quotes]
			search_params = {}
			vect = ('vect', CountVectorizer(analyzer = analyzer))
			search_params['vect__ngram_range'] = [(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]
			tfidf = ('tfidf', TfidfTransformer())
			clf = None
			if clf_type == 'svc_rbf_weighted':
				clf = ('clf', SVC(kernel = 'rbf', class_weight = 'auto'))
				search_params['clf__C'] = [0.001, 0.001, 0.1, 1, 10, 100, 1000]
				search_params['clf__gamma'] = [0.001, 0.001, 0.1, 1, 10, 100, 1000]
			elif clf_type == 'nb_weighted':
				clf = ('clf', MultinomialNB(class_prior = priors[prefs[i]]))
				search_params['clf__alpha'] = [0.0, 0.25, 0.5, 0.75, 1.0]
			elif clf_type == '93nn_weighted':
				clf = ('clf', KNeighborsClassifier(n_neighbors = 93, weights = 'distance'))
			pipeline = Pipeline([vect, tfidf, clf])
			pipeline = GridSearchCV(pipeline, search_params, n_jobs = 4)
			pipeline.fit(quotes_data, quotes_target)
			quotes_prediction = pipeline.predict(quotes_data)
			print 'done!  accuracy = ' + str(numpy.mean(quotes_prediction == quotes_target))
			end_time = time.time()
			print 'elapsed: ' + str(end_time - start_time) + ' s'
			if i != 3:
				print '--'
			s = pickle.dumps(pipeline)
			clf_file = open('committee/' + clf_name + '.pkl', 'w')
			clf_file.write(s)
			clf_file.close()
