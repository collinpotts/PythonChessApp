from flask import (Flask, render_template, request, flash, session,redirect, url_for, flash)
from model import connect_to_db, db, Message, Post, Vote, Reply, User
from jinja2 import StrictUndefined
import crud
import datetime
import feedparser

app = Flask(__name__)
app.secret_key = "dev"

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route("/home")
def home():
    logged_in_user_id = session.get("user_id")
    user = crud.get_user_by_user_id(logged_in_user_id)
    username = user.username
    rss_url = 'https://www.chess.com/rss/news'
    feed = feedparser.parse(rss_url)
    
    news_items = []
    for entry in feed.entries:
        item = {
            'title': entry.title,
            'link': entry.link,
            'description': entry.summary,
            'pubDate': entry.published
        }
        news_items.append(item)
    return render_template('index.html', username=username, news=news_items)

@app.route("/index")
def index():
    logged_in_user_id = session.get("user_id")
    user = crud.get_user_by_user_id(logged_in_user_id)
    username=user.username
    return render_template('index.html', username=username)
    
@app.route('/play')
def play():
    return render_template('play.html')

@app.route("/users", methods=["POST"])
def register_user():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    
    user_by_username = crud.get_user_by_username(username)
    if user_by_username:
        return redirect("/")
    
    user_by_email = crud.get_user_by_email(email)
    if user_by_email:
        return redirect("/")
    
    user = crud.create_user(username, password, email)
    db.session.add(user)
    db.session.commit()
    
    username=user.username
    return render_template("index.html", username=username)


@app.route("/login", methods=["POST"])
def process_login():
    username = request.form.get("username")
    password = request.form.get("password")
    user = crud.get_user_by_username(username)
    if user == None:
        print("username failed")
        if user.password != password:
            print("password is incorrect... Try again!")

            return redirect("/")
    else:
        session["user_id"] = user.user_id
        username=user.username
        rss_url = 'https://www.chess.com/rss/news'
        feed = feedparser.parse(rss_url)

        news_items = []
        for entry in feed.entries:
            item = {
                'title': entry.title,
                'link': entry.link,
                'description': entry.summary,
                'pubDate': entry.published
            }
            news_items.append(item)
        return render_template("index.html", username=username, news=news_items)

@app.route('/messages')
def messages():
    logged_in_user_id = session.get("user_id")
    conversations, sorted_messages = crud.get_conversations_for_user(logged_in_user_id)
    users = crud.get_users()
    return render_template('messages.html', conversations=conversations, users=users, current_user_id=logged_in_user_id)


@app.route('/messages/<int:user_id>')
def message_thread(user_id):
    logged_in_user_id = session.get("user_id")
    if not logged_in_user_id:
        return redirect('/')
    conversations, sorted_messages = crud.get_conversations_for_user(user_id)
    messages = crud.get_messages_for_user(logged_in_user_id)
    users = crud.get_users()
    user = crud.get_user_by_user_id(user_id)
    return render_template('message_thread.html', messages=messages, current_user_id=logged_in_user_id, conversations=conversations, users=users, user=user, sorted_messages=sorted_messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    logged_in_user_id = session.get("user_id")
    recipient_id = request.form['recipient_id']
    message = request.form['message']
    crud.create_message(logged_in_user_id, recipient_id, message)
    return redirect(request.referrer)

@app.route('/forums')
def show_post():
    posts = crud.get_all_posts()
    return render_template('forums.html', posts=posts)

@app.route('/forums/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':

        title = request.form['title']
        body = request.form['body']
        user_id = session.get('user_id')
        
        post = Post(title=title, body=body, user_id=user_id, created_at=datetime.datetime.now())
        db.session.add(post)
        db.session.commit()
        
        return redirect(f'/forums')
    
    return render_template('create_post.html')

@app.route('/posts/<int:post_id>')
def post_detail(post_id):
    logged_in_user = session.get("user_id")
    post = crud.get_post_by_id(post_id)
    return render_template('post_detail.html', post=post, post_id=post.post_id, logged_in_user=logged_in_user)

@app.route('/posts/<int:post_id>/vote', methods=['POST'])
def vote_post(post_id):
    current_user = request.form['user_id']
    vote_type = request.form['vote']
    post = Post.query.get(post_id)
    user = User.query.get(current_user)
    
    existing_vote = Vote.query.filter_by(user=user, post=post).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            if vote_type == 'upvote':
                return redirect(url_for('post_detail', post_id=post_id))
            else:
                db.session.delete(existing_vote)
                db.session.commit()
                return redirect(url_for('post_detail', post_id=post_id))
        else:
            existing_vote.vote_type = vote_type
            db.session.commit()
            return redirect(url_for('post_detail', post_id=post_id))

    else:
        if vote_type == 'downvote' and not existing_vote:
            return redirect(url_for('post_detail', post_id=post_id))
        new_vote = Vote(user=user, post=post, vote_type=vote_type)
        db.session.add(new_vote)
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post_id))


@app.route('/posts/<int:post_id>/reply', methods=['POST'])
def reply_post(post_id):
    user_id = session.get('user_id')
    body = request.form.get('body')
    
    reply = Reply(user_id=user_id, post_id=post_id, body=body, created_at=datetime.datetime.now())
    db.session.add(reply)
    db.session.commit()
    
    return redirect(f'/posts/{post_id}')


if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug = True, port = 5005, host = "localhost")
