# FileShare

**FileShare** is a lightweight and user-friendly Flask web application for file sharing and user management. It provides drag-and-drop upload, role-based access control, and an admin panel — all through a clean and modern interface.

## 🚀 Features

- Drag & drop file uploads
- File listing with download and delete options
- Role-based user system: `user`, `admin`, `owner`
- Admin panel for managing users and permissions
- Modal-based UI with smooth animations
- Secure login and session management
- Configurable via `.env` file
- Error-only logging support
- SQLite-based (easily switchable to other databases)

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/xdesai96/fileshare.git
cd fileshare
```
### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # On Linux/macOS
venv\Scripts\activate           # On Windows
```
3. Install dependencies

```bash
pip install -r requirements.txt
```
### 4. Create a .env file

```bash
owner_username=admin
owner_password=admin
secret_key=your_secret_key
SHARE_DIR=./uploads
```
### 5. Run the server

```bash
python server.py
```
### 🛠️ Project Structure

```bash
fileshare/
├── static/           # CSS, JavaScript, assets
├── templates/        # Jinja2 HTML templates
├── models.py         # SQLAlchemy models
├── server.py         # Flask application
├── utils.py          # Utility functions (e.g. hashing)
├── .env              # Environment variables
└── requirements.txt  # Python dependencies
```
### 👮 User Roles

- Owner: Full access to all features, including user management
- Admin: Can upload files, delete their own files
- User: Can download files

### 🧩 Roadmap / Ideas
- Upload progress bar
- Ability to cancel ongoing uploads
- File search feature
- Cloud storage support (e.g. S3, Dropbox)

### 📄 License
MIT License — free to use with credit.

### 🤝 Contact
Telegram: [@xdesai](https://t.me/xdesai)
Web-bio: https://xdesai.org
