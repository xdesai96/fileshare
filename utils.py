from models import db, User, Admin, Owner
import os
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
        return "owner"
    if Admin.query.filter_by(user_id=user.id).first():
        return "admin"
    return "user"


def get_logged_in_role(session):
    if "user_id" not in session:
        return None
    user = get_user_by_id(session["user_id"])
    return get_role(user.username)


def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        admin = Admin.query.filter_by(user_id=user.id).first()
        owner = Owner.query.filter_by(user_id=user.id).first()
        if admin:
            db.session.delete(admin)
        if owner:
            db.session.delete(owner)

        db.session.delete(user)
        db.session.commit()


def get_file_icon(file_name):
    file_extension = file_name.split(".")[-1].lower()

    icons = {
        "zip": "archive.png",
        "tar": "archive.png",
        "exe": "exe.png",
        "gz": "archive.png",
        "jpg": "image.png",
        "jpeg": "image.png",
        "png": "image.png",
        "gif": "image.png",
        "py": "python.png",
        "js": "js.png",
        "java": "java.png",
        "html": "html.png",
        "css": "css.png",
        "txt": "file.png",
        "pdf": "pdf.png",
        "docx": "word.png",
        "pptx": "ppt.png",
        "mp4": "video.png",
        "avi": "video.png",
        "mp3": "audio.png",
        "xlsx": "excel.png",
        "txt": "txt.png",
        "php": "php.png",
        "rb": "ruby.png",
        "c": "c.png",
        "cpp": "cpp.png",
    }
    if os.path.isdir(file_name):
        return "folder.png"

    return icons.get(file_extension, "file.png")


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
