import requests
from flask import Flask, redirect, render_template, request, session
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdsgdfgdfbhfdwe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///baza.sqlite'
db = SQLAlchemy(app)
API_KEY = '66ed6267'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(55), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/home')
def home():
    return render_template('Homepage.html')


@app.route('/movieinfo', methods=['GET', 'POST'])
def movieinfo():
    movie_info = None
    if request.method == 'POST':
        movie = request.form.get('movie')
        if movie:
            url = f'http://www.omdbapi.com/?t={movie}&apikey={API_KEY}'
            response = requests.get(url)
            if response.ok:
                movie_info = response.json()
            else:
                movie_info = {'Error': 'Could not retrieve movie information'}

    return render_template('movieinfo.html', movie_info=movie_info)

@app.route('/mypage')
def mypage():
    return render_template('mypage.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        p = request.form['password']
        session['username'] = user
        base1 = User(username = user, password = generate_password_hash(p))
        db.session.add(base1)
        db.session.commit()
        return redirect('/mypage')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username')
    return render_template('logout.html')

@app.route('/features')
def features():
    kinoafisha_url = 'https://www.kinoafisha.ge/'
    response = requests.get(kinoafisha_url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    movie_divs = soup.find_all('div', class_='movie')

    movie_list = []
    for movie_div in movie_divs:
        title_div = movie_div.find('h5', class_='truncate')
        if title_div:
            movie_title = title_div.text.strip()
        else:
            movie_title = 'N/A'

        image_div = movie_div.find('img', class_='movie-avatar')
        if image_div:
            movie_image_url = image_div['src']
        else:
            movie_image_url = 'N/A'

        movie_list.append({'title': movie_title, 'image_url': movie_image_url})

    return render_template('features.html', movies=movie_list)
if __name__ == '__main__':
    app.run(debug=True)
