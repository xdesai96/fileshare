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
