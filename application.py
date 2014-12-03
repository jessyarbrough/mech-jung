import flask, numpy, scipy, sklearn, tweepy
 
application = flask.Flask(__name__)

#Set application.debug=true to enable tracebacks on Beanstalk log output. 
#Make sure to remove this line before deploying to production.
application.debug=True
 
@application.route('/')
def hello_world():
    return flask.render_template('index.html')
 
if __name__ == '__main__':
    application.run(host='0.0.0.0')
