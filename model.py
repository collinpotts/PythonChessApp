from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    rating = db.Column(db.Integer)

    def __repr__(self):
        return f"<User user_id={self.user_id} email={self.email}>"

class Message(db.Model):
    __tablename__ = "messages"

    message_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    message = db.Column(db.String)
    timestamp = db.Column(db.DateTime)

    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])

    def __repr__(self):
        return f"<Message message_id={self.message_id} sender_id={self.sender_id} recipient_id={self.recipient_id}>"

def create_message(sender_id, recipient_id, message_text):
    message = Message(sender_id=sender_id, recipient_id=recipient_id, message_text=message_text)
    db.session.add(message)
    db.session.commit()
    return message

def get_messages_for_user(user_id):
    return Message.query.filter_by(recipient_id=user_id).all()

class Post(db.Model):
    __tablename__ = "posts"

    post_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(db.DateTime)

    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    votes = db.relationship('Vote', backref='post', lazy=True)
    replies = db.relationship('Reply', backref='post', lazy=True)
    
    def __repr__(self):
        return f"<Post post_id={self.post_id} title={self.title}>"

class Reply(db.Model):
    __tablename__ = "replies"

    reply_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    body = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'))
    created_at = db.Column(db.DateTime)

    user = db.relationship('User', backref=db.backref('replies', lazy=True))
    reply_post = db.relationship('Post', backref=db.backref('post_replies', lazy=True))

    def __repr__(self):
        return f"<Reply reply_id={self.reply_id} post_id={self.post_id}>"

class Vote(db.Model):
    __tablename__ = "votes"

    vote_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'))
    reply_id = db.Column(db.Integer, db.ForeignKey('replies.reply_id'))
    vote_type = db.Column(db.String)

    user = db.relationship('User', backref=db.backref('votes', lazy=True))
    voted_post = db.relationship('Post', backref=db.backref('post_votes', lazy=True))
    reply = db.relationship('Reply', backref=db.backref('votes', lazy=True))

    def __repr__(self):
        return f"<Vote vote_id={self.vote_id} user_id={self.user_id} vote_type={self.vote_type}>"


def connect_to_db(flask_app, db_uri=os.environ["POSTGRES_URI"], echo=False):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":
    from server import app
    connect_to_db(app)
