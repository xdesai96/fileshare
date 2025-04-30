from models import db, User, Admin, Owner
from werkzeug.security import generate_password_hash, check_password_hash

# ---------- USER FUNCTIONS ----------

def add_user(username, password):
    if not User.query.filter_by(username=username).first():
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()


def get_users():
    return {user.username: user for user in User.query.all()}


def get_role(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return None
    if Owner.query.filter_by(user_id=user.id).first():
        return 'owner'
    if Admin.query.filter_by(user_id=user.id).first():
        return 'admin'
    return 'user'


def get_logged_in_role(session):
    if 'user_id' not in session:
        return None
    user = get_user_by_id(session['user_id'])
    return get_role(user.username)


def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        # Удалим возможную связку с Owner/Admin
        admin = Admin.query.filter_by(user_id=user.id).first()
        owner = Owner.query.filter_by(user_id=user.id).first()
        if admin:
            db.session.delete(admin)
        if owner:
            db.session.delete(owner)

        db.session.delete(user)
        db.session.commit()


def change_user_password(username, new_password):
    user = User.query.filter_by(username=username).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()


def check_user_password(username, password):
    user = User.query.filter_by(username=username).first()
    return user and check_password_hash(user.password, password)


def get_user_by_id(user_id):
    return User.query.get(user_id)


# ---------- ADMIN FUNCTIONS ----------


def add_admin(username):
    user = User.query.filter_by(username=username).first()
    if user and not Admin.query.filter_by(user_id=user.id).first():
        admin = Admin(user_id=user.id)
        db.session.add(admin)
        db.session.commit()


def get_admins():
    return {User.query.get(admin.user_id).username for admin in Admin.query.all()}


def delete_admin(username):
    user = User.query.filter_by(username=username).first()
    if user:
        admin = Admin.query.filter_by(user_id=user.id).first()
        if admin:
            db.session.delete(admin)
            db.session.commit()


# ---------- OWNER FUNCTIONS ----------


def add_owner(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
    if not Owner.query.filter_by(user_id=user.id).first():
        owner = Owner(user_id=user.id)
        db.session.add(owner)
        db.session.commit()


def delete_owner(username):
    user = User.query.filter_by(username=username).first()
    if user:
        owner = Owner.query.filter_by(user_id=user.id).first()
        if owner:
            db.session.delete(owner)
            db.session.commit()

