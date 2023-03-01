from model import db, User, Message, Post, Vote, Reply, connect_to_db

def create_user(username, password, email):
    user = User(username=username, password=password, email=email)
    db.session.add(user)
    db.session.commit()
    return user

def get_users():
    return User.query.all()

def get_user_by_email(email):
    return User.query.filter(User.email == email).first()

def get_user_by_username(username):
    return User.query.filter_by(username = username).first()

def get_user_by_user_id(user_id):
    return User.query.get(user_id)

def create_message(sender_id, receiver_id, message_text):
    message = Message(sender_id=sender_id, recipient_id=receiver_id, message=message_text)
    db.session.add(message)
    db.session.commit()
    return message

def get_messages_for_user(user_id):
    return Message.query.filter_by(recipient_id=user_id).all()

def get_conversations_for_user(user_id):
    conversations = []
    messages_sent = Message.query.filter_by(sender_id=user_id).all()
    messages_received = Message.query.filter_by(recipient_id=user_id).all()
    message_ids = set()

    for message in messages_sent:
        other_user_id = message.recipient_id
        if other_user_id not in message_ids and other_user_id != user_id:
            other_user = User.query.get(other_user_id)
            if other_user:
                conversation = {"other_user": other_user, "latest_message": message}
                conversations.append(conversation)
                message_ids.add(other_user_id)

    for message in messages_received:
        other_user_id = message.sender_id
        if other_user_id not in message_ids and other_user_id != user_id:
            other_user = User.query.get(other_user_id)
            if other_user:
                conversation = {"other_user": other_user, "latest_message": message}
                conversations.append(conversation)
                message_ids.add(other_user_id)

    all_messages = Message.query.filter((Message.sender_id == user_id) | (Message.recipient_id == user_id)).all()
    sorted_messages = sorted(all_messages, key=lambda m: m.message_id, reverse=True)

    return conversations, sorted_messages

def create_post(title, content, user_id):
    post = Post(title=title, content=content, user_id=user_id)
    db.session.add(post)
    db.session.commit()
    return post

def get_all_posts():
    return Post.query.all()


def get_post_by_id(post_id):
    return Post.query.get(post_id)

def get_post(post_id):
    post = Post.query.get(post_id)
    votes = Vote.query.filter_by(post_id=post_id).all()
    replies = Reply.query.filter_by(post_id=post_id).all()
    return post, votes, replies

if __name__ == '__main__':
    from server import app
    connect_to_db(app)
