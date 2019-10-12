from flask import Flask, jsonify
from models import *

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# store all filtered data as list of dict
filtered_surveys = []

@app.route("/")
def index():
    return "hello world"



@app.route("/survey")
def get_surveys():
    # get all surveys from db
    surveys = Surveys.query.all()
    print(surveys)
    # filter surveys
    for survey in surveys:
        filtered_surveys.append({
            "id": survey.id,
            "name": survey.name,
            "description": survey.description,
            "questions": [{"question": {"body": survey.body, "note": survey.note}}],
            "start_data": survey.start_data,
            "end_data": survey.end_data
        })

    return jsonify(filtered_surveys);



@app.route("/survey", methods=["POST"])
def post_survey():

    # uncomment if you want to test with static data as if it coming from post request

    # name = "Mohamed"
    # description = "Course survey"
    # body = "A survey for online courses ..."
    # note = "This is survey you should fill"
    # start_data = "11/10/2019"
    # end_data = "20/10/2019"


    # get json data from post request
    data = request.json

    # create new survey with data from the request
    survey = Surveys(name=data["name"], description=data["description"], body=data["body"], note=data["note"], start_data=data["start_data"], end_data=data["end_data"])

    # insert survey into db
    db.session.add(survey)

    # commit changes
    db.session.commit()



@app.route('/api/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if User.query.filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = User(username = username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username }), 201, {'Location': url_for('get_user', id = user.id, _external = True)}


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })



@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True



def main():
    db.create_all()



