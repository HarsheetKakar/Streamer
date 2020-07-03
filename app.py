from streamer import create_app, STATIC_FOLDER, db
from streamer.models import load_user, User, Video, Show, Season

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from flask import render_template, request, url_for, send_file, Response, redirect
from flask_login import current_user, login_user, logout_user, login_required

import glob
import os
import re
import sys
import time
import pprint
import mimetypes

from datetime import datetime

MB = 1 << 20
BUFF_SIZE = 10 * MB

app = create_app()


@app.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return render_template('index.html', shows=Show.query.all())
    else:
        return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        user = User.query.filter_by(email=request.form['email']).first()
        if(not user or not user.check_password(request.form['password'])):
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for("index"))
    return render_template('login.html')


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if(request.method == 'POST'):
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        user = User(email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/show/<int:id>/', methods=['GET'])
@login_required
def show(id):
    show = Show.query.filter_by(id=id).first()
    return render_template('show.html', show=show, title=show.name)


@app.route('/season/<int:id>/', methods=['GET'])
@login_required
def season(id):
    season = Season.query.filter_by(id=id).first()
    return render_template('season.html', season=season, title=f"{season.show.name} > {season.name}")


@app.route('/player/<int:id>/', methods=['GET'])
@login_required
def player(id):
    video = Video.query.filter_by(id=id).first()
    return render_template('player.html', video=video, title=f"{video.season.show.name} > {video.season.name} > {video.name}")


def partial_response(path, start, end=None):
    file_size = os.path.getsize(path)

    # Determine (end, length)
    if end is None:
        end = start + BUFF_SIZE - 1
    end = min(end, file_size - 1)
    end = min(end, start + BUFF_SIZE - 1)
    length = end - start + 1

    # Read file
    with open(path, 'rb') as fd:
        fd.seek(start)
        bytes = fd.read(length)
    assert len(bytes) == length

    response = Response(
        bytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, end, file_size,
        ),
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    return response


def get_range(request):
    range = request.headers.get('Range')
    m = re.match('bytes=(?P<start>\d+)-(?P<end>\d+)?', range)
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None


@app.route("/video/<int:id>/")
@login_required
def video(id):
    video = Video.query.filter_by(id=id).first()
    path = video.path
    start, end = get_range(request)
    return partial_response(path, start, end)


@app.route("/search/", methods=['GET', 'POST'])
def search():
    name = request.form['name']
    shows = Show.query.filter(Show.name.ilike(f"%{name}%")).all()
    return render_template("index.html", shows=shows)


@app.route('/dummyShows/', methods=['GET'])
def dummyShows():
    show = Show('Friends', thumbnail=url_for(
        'static', filename='images/friends_thumbnail.jpg'))
    season = Season(name='Season 1')
    for index, value in enumerate(glob.glob(os.path.join(STATIC_FOLDER, 'videos')+"\\friends_?_?.mp4")):
        vid = Video(path=value, name="episode "+str(index+1))
        season.videos.append(vid)
    show.seasons.append(season)
    db.session.add(show)

    show2 = Show('The Office', thumbnail=url_for(
        'static', filename='images/the_office_thumbnail.jpg'))
    season = Season(name='Season 1')
    for index, value in enumerate(glob.glob(os.path.join(STATIC_FOLDER, 'videos')+"\\the_office_?_?.mp4")):
        vid = Video(path=value, name="episode "+str(index+1))
        season.videos.append(vid)
    show2.seasons.append(season)
    db.session.add(show2)

    db.session.commit()
    return render_template('test.html', vids=Video.query.all())


if __name__ == "__main__":
    db.drop_all(app=app)
    db.create_all(app=app)
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(8080)
    IOLoop.instance().start()
    HOST = '127.0.0.1'
    # app.run(host=HOST, port=8080, debug=True)
