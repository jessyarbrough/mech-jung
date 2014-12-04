import flask, random, socket
# import pickle, numpy, scipy, sklearn, tweepy
from pickle import loads as pkl_load
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
 
application = flask.Flask(__name__)

err_nedry = 'na uh uh, say the magic word'

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
PersonalitiesDescription = {}

for line in open("PersonalitiesDescription.tsv", "r"):
	line = line.split('\t')
	key = line[0]
	description = line[1]
	url = line[2].strip()
	PersonalitiesDescription[key] = (description, url)

with open("Personalities.tsv", "rb") as f:
    for line in f:
        line = line.split('\t')
        key = line[1]
        values = [line[0], line[2].strip()]
        if key in personalities.keys():
            personalities[key] += [[values]]
        else:
            personalities[key] = [[values]]

def is_local_req(remote_addr):
	remote_addr = str(remote_addr)
	local_addr = str(socket.gethostbyname(socket.gethostname()))
	remote_addr = remote_addr.split('.')
	local_addr = local_addr.split('.')
	return remote_addr[0] == local_addr[0] and remote_addr[1] == local_addr[1]

@application.route('/')
def hello_world():
    return flask.render_template('index.html')

@application.route('/results', methods = ['POST'])
def classify():
	if not is_local_req(flask.request.remote_addr):
		return err_nedry
	doc = flask.request.form['text']
	result = ''
	for pref in prefs:
		clf = classifiers[pref]['svc']['text']
		result += clf.predict([doc])[0]
	x = 1
	description = PersonalitiesDescription[result][0]
	description_url = PersonalitiesDescription[result][1]
	people = personalities[result]
	length = len(people)
	rand1 = random.randint(0, length/3)
	rand2 = random.randint(length/3+1, 2*length/3)
	rand3 = random.randint(2*length/3+1, length-1)
	print people[rand1][0][0]
	name1 = people[rand1][0][0]
	url1 = "http://www.celebritytypes.com/" + people[rand1][0][1]
	print url1
	name2 = people[rand2][0][0]
	url2 = "http://www.celebritytypes.com/" + people[rand2][0][1]
	name3 = people[rand3][0][0]
	url3 = "http://www.celebritytypes.com/" + people[rand3][0][1]
	return flask.render_template('results.html', result=result, name1=name1, url1=url1, name2=name2, url2=url2, name3=name3, url3=url3, description=description, description_url=description_url)
 
@application.route('/twitter-results', methods = ['POST'])
def classify_tweets():
	if not is_local_req(flask.request.remote_addr):
		return err_nedry
	return 'Coming soon!'

if __name__ == '__main__':
	application.debug = True
	application.run(host='0.0.0.0')
