from flask import Flask, render_template, session, request, redirect, url_for
from flask_cors import CORS, cross_origin
import db_man as db


app = Flask(__name__)
app.config['SECRET_KEY'] = 'BECK@JEZ!MIKE'
CORS(app)


@app.before_request
def check_access():
    enforced_routes = ['def_root', 'ajax_handle']
    if request.endpoint in enforced_routes:
        if session.get('token') is not None and session.get('login_id') is not None:
            if db.Auth.check_token(session['login_id'], session['token']):
                return
            else:
                session['token'] = None

        return redirect(url_for('def_login'))


@app.route('/logout')
def def_logout():
    db.Auth.remove_token(session.get("token"))
    session.pop("token")
    session.pop("login_id")
    return redirect(url_for("def_login"))


@app.route('/login', methods=['GET', 'POST'])
def def_login():
    if request.method == "GET":
        get_res = db.Auth.do_login(session.get("username"), session.get("password"))
        if get_res is None or get_res is False:
            return render_template('login.html')
        return redirect(url_for('def_root'))

    res = db.Auth.do_login(request.form.get("username"), request.form.get("password"))
    if res is None:
        return render_template('login.html', msg="No Such Username")
    if res is False:
        return render_template('login.html', msg="Wrong Password")
    session['token'] = res[0]
    session['login_id'] = res[1]
    return redirect(url_for('def_root'))


@app.route('/')
@app.route('/week/<int:week>')
def def_root(week=None):
    return render_template("home.html", payload=db.Manage.load_dash(week))


@app.route('/ajax/<task>', methods=['GET', 'POST'])
def ajax_handle(task):
    if task == "get_teams":
        return {"teams": db.Manage.get_teams()}
    else:
        print("onto calling handler for task: ", task)
        return db.Manage.task_endpoint(task, request.get_json())            # call Handler


@app.route('/api/get_slots')
@app.route('/api/get_slots/<int:week>/')
@cross_origin()
def api_get_slots(week=None):
    return db.get_slots_data(week)


@app.route('/api/get_scores')
@app.route('/api/get_scores/<int:week>/')
@cross_origin()
def api_get_scores(week=None):
    return db.get_scores_data(week)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
