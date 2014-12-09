import flask, random, socket, tweepy
# import pickle, numpy, scipy, sklearn
from pickle import loads as pkl_load
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
import random, os
 
application = flask.Flask(__name__)

params = {}

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
personalities_description = {}
quotes = {}

for line in open("quotes_known_only.tsv", 'r'):
	line = line.split('\t')
	key = line[1]
	quote = line[0]
	if key in quotes.keys():
		quotes[key].append(quote)
	else:
		quotes[key] = []
		quotes[key].append(quote)

for line in open("PersonalitiesDescription.tsv", "r"):
	line = line.split('\t')
	key = line[0]
	description = line[1]
	url = line[2].strip()
	personalities_description[key] = (description, url)

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
	doc = flask.request.form['text']
	if len(doc) > 100000:
		doc = doc[:100000]
	result = ''
	for pref in prefs:
		clf = classifiers[pref]['svc']['text']
		result += clf.predict([doc])[0]
	x = 1
	description = personalities_description[result][0]
	description_url = personalities_description[result][1]
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

	if name1 not in quotes.keys():
		quote1 = ''
	else:
		rand4 = random.randint(0, len(quotes[name1])-1)
		quote1 = '"' + quotes[name1][rand4] + '"'
	
	if name2 not in quotes.keys():
		quote2 = ''
	else:
		rand5 = random.randint(0, len(quotes[name2])-1)
		quote2 = '"' + quotes[name2][rand5] + '"'
	
	if name3 not in quotes.keys():
		quote3 = ''
	else:
		rand6 = random.randint(0, len(quotes[name3])-1)
		quote3 = '"' + quotes[name3][rand6] + '"'

	return flask.render_template('results.html', result=result, name1=name1, url1=url1, name2=name2, url2=url2, name3=name3, url3=url3,
		description=description, description_url=description_url, quote1=quote1, quote2=quote2, quote3=quote3)
 
@application.route('/twitter-results', methods = ['POST'])
def classify_tweets():
	handle = flask.request.form['handle']
	if len(handle) > 15 or len(handle) == 0:
		return flask.render_template('index.html', handle_placeholder = 'Twitter handle')
    
	parameter = random.choice(['1'])
	param = params[parameter]
	consumer_key = param[0]
	print param[0]
	consumer_secret = param[1]
	print param[1]
	access_key = param[2]
	print param[2]
	access_secret = param[3]
	print param[3]
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)
    	
	tweets = []

	checkifExists = api.search_users(handle)
	if not checkifExists:
		return flask.render_template('index.html', handle_placeholder = 'User not found')
	else:
		fetchedTweets = api.user_timeline(screen_name = handle, count = 100)
		tweets.extend(fetchedTweets)

	if not tweets:
		return flask.render_template('index.html', handle_placeholder = 'No tweets for user')

	textFromTweets = []
	for t in tweets:
		textFromTweets.append(t.text)

	length = len(textFromTweets)

	result = ''
	resultList = []
	characterDict = {}

	for pref in prefs:
		clf = classifiers[pref]['svc']['tweet']
		result += str(clf.predict(textFromTweets))

	icount = list(result).count('I')
	ecount = list(result).count('E')
	ncount = list(result).count('N')
	scount = list(result).count('S')
	fcount = list(result).count('F')
	tcount = list(result).count('T')
	jcount = list(result).count('J')
	pcount = list(result).count('P')

	personalityStr = ''
	if icount > ecount:
		personalityStr += 'I'
	elif icount == ecount:
		personalityStr += '*'
	else:
		personalityStr += 'E'

	if ncount > scount:
		personalityStr += 'N'
	elif ncount == scount:
		personalityStr += '*'
	else:
		personalityStr += 'S'

	if fcount > tcount:
		personalityStr += 'F'
	elif fcount == tcount:
		personalityStr += '*'
	else:
		personalityStr += 'T'

	if jcount > pcount:
		personalityStr += 'J'
	elif jcount == pcount:
		personalityStr += '*'
	else:
		personalityStr += 'P'

	result = personalityStr

	x = 1
	description = personalities_description[result][0]
	description_url = personalities_description[result][1]
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
        
	if name1 not in quotes.keys():
		quote1 = ''
	else:
		rand4 = random.randint(0, len(quotes[name1])-1)
		quote1 = '"' + quotes[name1][rand4] + '"'

	if name2 not in quotes.keys():
		quote2 = ''
	else:
		rand5 = random.randint(0, len(quotes[name2])-1)
		quote2 = '"' + quotes[name2][rand5] + '"'

	if name3 not in quotes.keys():
		quote3 = ''
	else:
		rand6 = random.randint(0, len(quotes[name3])-1)
		quote3 = '"' + quotes[name3][rand6] + '"'


#return flask.render_template('twitterResults.html', result=result)
	return flask.render_template('twitterResults.html', result=result, name1=name1, url1=url1, name2=name2, url2=url2, name3=name3, url3=url3,
                             description=description, description_url=description_url, quote1=quote1, quote2=quote2, quote3=quote3, icount=icount, ecount=ecount, ncount=ncount, scount=scount, fcount=fcount, tcount=tcount, jcount=jcount, pcount=pcount)
#	return 'Coming soon!'
#return personalityStr

if __name__ == '__main__':
	with open("keys.txt", "rb") as f:
		count = 1
		for line in f:
			params[str(count)] = line.split('.')
			count += 1
	application.debug = True
	application.run(host='0.0.0.0')
else:
	param1 = os.environ.get('PARAM1').split('.')
	params['1'] = param1
