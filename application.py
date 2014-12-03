import flask, pickle
# import numpy, scipy, sklearn, tweepy
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
 
application = flask.Flask(__name__)
 
@application.route('/')
def hello_world():
    return flask.render_template('index.html')

@application.route('/results', methods = ['POST'])
def classify():
	doc = flask.request.form['text']
	codes = ['ie', 'ns', 'ft', 'jp']
	results = ''
	for code in codes:
		classifier = pickle.loads(open(code+'.svc.opt.pkl').read())
		result = classifier.predict([doc])[0]
		results = results + result
	return results
 
if __name__ == '__main__':
	application.debug = True
	application.run(host='0.0.0.0')
