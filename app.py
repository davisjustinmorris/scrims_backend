from flask import Flask, render_template, session, request, make_response
from flask_cors import CORS, cross_origin
import db_man as db


app = Flask(__name__)
app.config['SECRET_KEY'] = 'BECK@JEZ!MIKE'
CORS(app)


@app.before_request
def check_access():
    pass


@app.route('/login')
def def_login():
    return ''


@app.route('/team_list')
def team_list():
    return render_template('teams.html', payload=db.Manage.get_teams())


@app.route('/')
@app.route('/week/<int:week>')
def def_root(week=None):
    return render_template("home.html", payload=db.Manage.load_dash(week))


@app.route('/ajax/<task>')
def ajax_handle(task):
    if task == "get_teams":
        return {"teams": db.Manage.get_teams()}

    return "say what!?"


@app.route('/api/get_slots')
@app.route('/api/get_slots/<int:week>/')
@cross_origin()
def api_get_slots(week=None):
    res = db.get_slots_data(week)
    print(res)
    return res


@app.route('/api/get_scores')
@app.route('/api/get_scores/<int:week>/')
@cross_origin()
def api_get_scores(week=None):
    res = db.get_scores_data(week)
    print(res)
    return res


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
