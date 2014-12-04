import flask
# import pickle, numpy, scipy, sklearn, tweepy
from pickle import loads as pkl_load
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
 
application = flask.Flask(__name__)

prefs = ['ie', 'ns', 'ft', 'jp']
clf_types = ['svc', 'nb', 'knn']
doc_types = ['text', 'tweet']
classifiers = {}

for pref in prefs:
	classifiers[pref] = {}
	for clf_type in clf_types:
		classifiers[pref][clf_type] = {}
		for doc_type in doc_types:
			classifiers[pref][clf_type][doc_type] = None
			try:
				fname = pref + '.' + clf_type + '.' + doc_type + '.pkl'
				clf = pkl_load(open(fname).read())
				classifiers[pref][clf_type][doc_type] = clf
			except IOError:
				pass

personalities = {}

with open("Personalities.tsv", "rb") as f:
    for line in f:
        line = line.split('\t')
        key = line[1]
        values = [line[0], line[2].strip()]
        if key in personalities.keys():
            personalities[key] += [[values]]
        else:
            personalities[key] = [[values]]

 
@application.route('/')
def hello_world():
    return flask.render_template('index.html')

@application.route('/results', methods = ['POST'])
def classify():
	doc = flask.request.form['text']
	result = ''
	for pref in prefs:
		clf = classifiers[pref]['svc']['text']
		result += clf.predict([doc])[0]
    people = personalities[result]
    length = len(people)
    rand1 = random.randint(0, length/3)
    rand2 = random.randint(length/3+1, 2*length/3)
    rand3 = random.randint(2*length/3+1, length-1)
    name1 = people[rand1][0]
    pickurl1 = people[rand1][1]
    name2 = people[rand2][0]
    pickurl2 = people[rand2][1]
    name3 = people[rand3][0]
    pickurl3 = people[rand3][1]
	return flask.render_template('results.html', result=result, name1=name1, name2=name2, name3=name3, pickurl1=pickurl1, pickurl2=pickurl2, pickurl3=pickurl3)
 
if __name__ == '__main__':
	application.debug = True
	application.run(host='0.0.0.0')
