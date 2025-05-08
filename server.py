import os
import time
import logging
import subprocess
import shutil
from dotenv import load_dotenv
import html
import mimetypes
from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    redirect,
    url_for,
    session,
    send_from_directory,
    flash,
    abort,
    send_file,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Admin, Owner
from utils import (
    add_owner,
    add_user,
    change_user_password,
    delete_user,
    secure_path_from_url,
    get_logged_in_role,
    get_user_by_id,
    get_users,
    get_file_icon,
    get_admins,
    check_user_password,
)

# -------------------- Logs --------------------

logging.basicConfig(level=logging.ERROR)
werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.ERROR)

# ------------------ App init ------------------

load_dotenv()
secret_key = os.getenv("secret_key")
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = secret_key
app.config["SESSION_COOKIE_SECURE"] = False


# ------------------ DB init --------------------


owner_username = os.getenv("owner_username")
owner_password = os.getenv("owner_password")

db.init_app(app)
with app.app_context():
    db.create_all()
    init_owner = db.session.query(User).filter_by(username=owner_username).first()
    if not init_owner:
        add_owner(owner_username, owner_password)


# ------------------ Files ----------------------


SHARE_DIR = os.getenv("SHARE_DIR")
LOGIN_TEMPLATE = "login.html"
FILES_TEMPLATE = "browse.html"


# ---------------- Auth routes ------------------


@app.before_request
def ensure_user_valid():
    if "user_id" in session:
        user = db.session.get(User, session["user_id"])
        if not user:
            session.pop("user_id", None)
            return redirect(url_for("login"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and check_user_password(username, password):
            session["user_id"] = user.id

            if user.owner:
                session["role"] = "owner"
            elif user.admin:
                session["role"] = "admin"
            else:
                session["role"] = "user"

            return redirect(url_for("browse"))
        else:
            flash("Invalid credentials.")

    return render_template(LOGIN_TEMPLATE)


@app.route("/register_user", methods=["POST"])
def register_user():
    if session["role"] != "owner":
        return redirect(request.referrer)

    username = request.form["username"]
    password = request.form["password"]

    add_user(username, password)
    return redirect(request.referrer)


@app.route("/delete_user", methods=["POST"])
def delete_user_req():
    if "user_id" not in session or session["role"] != "owner":
        return redirect(request.referrer)

    username = request.form["username"]

    if username not in get_users().keys():
        return redirect(request.referrer)

    delete_user(username)
    return redirect(request.referrer)


@app.route("/change_role/<username>/<role>", methods=["POST"])
def change_role(username, role):
    if session["role"] != "owner":
        return jsonify({"success": False, "message": "Access Denied"}), 403

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    if user.admin:
        db.session.delete(user.admin)
        db.session.commit()
    if user.owner:
        db.session.delete(user.owner)
        db.session.commit()

    if role == "admin":
        new_admin = Admin(user_id=user.id)
        db.session.add(new_admin)
        db.session.commit()
    elif role == "owner":
        new_owner = Owner(user_id=user.id)
        db.session.add(new_owner)
        db.session.commit()
    else:
        if user.admin:
            db.session.delete(user.admin)
            db.session.commit()
        if user.owner:
            db.session.delete(user.owner)
            db.session.commit()
    return jsonify({"success": True})


@app.route("/change_password", methods=["POST"])
def change_password():
    current_session = get_user_by_id(session["user_id"])
    new_pswd = request.form["new_password"]
    change_user_password(current_session.username, new_pswd)
    return redirect(request.referrer)


# ---------------- File browser routes ------------------


def get_file_info(full_path, rel_path):
    stat = os.stat(full_path)
    return {
        "name": os.path.basename(full_path),
        "icon": url_for("static", filename="icons/" + get_file_icon(full_path)),
        "rel": rel_path,
        "href": url_for("browse", path=rel_path)
        if os.path.isdir(full_path)
        else url_for("download", path=rel_path),
        "is_dir": os.path.isdir(full_path),
        "size": f"{stat.st_size / 1024:.1f} KB" if not os.path.isdir(full_path) else "",
        "mtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime)),
    }


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def browse(path):
    if "user_id" not in session:
        return redirect(url_for("login"))
    full_path = os.path.join(SHARE_DIR, path)
    if not os.path.exists(full_path) or not os.path.commonpath(
        [SHARE_DIR, full_path]
    ).startswith(SHARE_DIR):
        abort(404)

    files = []

    if os.path.isdir(full_path):
        for name in os.listdir(full_path):
            p = os.path.join(full_path, name)
            r = os.path.join(path, name)
            files.append(get_file_info(p, r))
    else:
        files.append(get_file_info(full_path, path))

    sort = request.args.get("sort", "name")
    files.sort(key=lambda x: x.get(sort) or "", reverse=False)
    me = get_user_by_id(session["user_id"])
    parent_path = os.path.dirname(path)
    return render_template(
        FILES_TEMPLATE,
        admins=get_admins(),
        me=me,
        users=get_users(),
        role=get_logged_in_role(session),
        session=session,
        files=files,
        rel_path=path,
        parent_path=parent_path,
    )


@app.route("/delete_folder", methods=["POST"])
def delete_folder():
    folder_path = request.form["folder_path"]

    full_folder_path = os.path.join(SHARE_DIR, folder_path)

    if os.path.exists(full_folder_path) and os.path.isdir(full_folder_path):
        try:
            shutil.rmtree(full_folder_path)
            return redirect(request.referrer)
        except Exception as e:
            return f"Error deleting folder: {e}", 500
    else:
        return f"Folder not found: {full_folder_path}", 404


@app.route("/download/<path:path>")
def download(path):
    full_path = os.path.join(SHARE_DIR, path)
    if not os.path.exists(full_path):
        abort(404)
    return send_from_directory(SHARE_DIR, path, as_attachment=True)


@app.route("/delete_file", methods=["POST"])
def delete_file():
    user = get_user_by_id(session["user_id"])
    file_path = request.form["file_path"]
    full_path = os.path.join(SHARE_DIR, file_path)

    if os.path.isfile(full_path) and (
        user.username in os.path.basename(full_path) or user.role == "owner"
    ):
        os.remove(full_path)
        return redirect(request.referrer)
    else:
        return "Unauthorized or file not found", 403


@app.route("/admin_upload", methods=["POST"])
def admin_upload():
    uploaded_files = request.files.getlist("files")
    if len(uploaded_files) < 1:
        return redirect(request.referrer)

    current_session = get_user_by_id(session["user_id"])
    username = current_session.username

    for file in uploaded_files:
        if file.filename:
            relative_path = file.filename

            if username != owner_username:
                relative_path = os.path.join(username, relative_path)

            final_path = os.path.join(SHARE_DIR, relative_path)

            os.makedirs(os.path.dirname(final_path), exist_ok=True)

            base, ext = os.path.splitext(os.path.basename(final_path))
            folder = os.path.dirname(final_path)
            i = 1
            while os.path.exists(final_path):
                new_filename = f"{i}_{base}{ext}"
                final_path = os.path.join(folder, new_filename)
                i += 1

            file.save(final_path)

    return redirect(request.referrer)


@app.route("/update_fileshare", methods=["POST"])
def update_fileshare():
    try:
        result = subprocess.run(
            ["git", "pull"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return jsonify({"success": True, "output": result.stdout.decode("utf-8")}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": e.stderr.decode("utf-8")}), 500


@app.route("/preview")
def preview_file():
    file_url = request.args.get("file_url")
    try:
        file_path = secure_path_from_url(SHARE_DIR, file_url)

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        if mime_type.startswith("image/"):
            return f'<img src="/files/{file_url}" alt="Image Preview" style="max-width:100%;">'

        elif mime_type.startswith("text/") or file_path.endswith(
            (".txt", ".sh", ".ovpn", ".config", ".conf")
        ):
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            escaped = html.escape(content)
            return f"<pre>{escaped}</pre>"

        else:
            return f"<p>📦 Невозможно отобразить файл типа: {mime_type}</p>", 415

    except Exception as e:
        logging.error(f"Error: {e}")
        return f"<p>❌ Ошибка при открытии файла: {e}</p>", 400


@app.route("/files/<path:path>")
def serve_file(path):
    full_path = os.path.join(SHARE_DIR, path)
    if not os.path.exists(full_path):
        abort(404)
    return send_file(full_path)


@app.route("/download_folder/<path:path>")
def download_folder(path):
    full_path = os.path.join(SHARE_DIR, path)
    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        abort(404)

    zip_filename = f"{path.strip('/').replace('/', '_')}.zip"
    zip_path = os.path.join("/tmp", zip_filename)

    shutil.make_archive(zip_path.replace(".zip", ""), "zip", full_path)

    return send_file(zip_path, as_attachment=True, download_name=zip_filename)


# ---------------- Run ------------------


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5555, debug=False)
