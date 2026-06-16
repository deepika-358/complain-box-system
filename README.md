# 🎯 Complain Box System

A full-stack anonymous complaint management system with admin dashboard, charts, resolution tracking, and email notifications.

---

## 🚀 Quick Start (Windows)

### Step 1 — Install Python dependencies
```powershell
cd backend
pip install -r requirements.txt
```

### Step 2 — Start the Backend
```powershell
cd backend
python app.py
```
> API will run at: **http://localhost:5000**
> SQLite database auto-created at `backend/complain_box.db`

### Step 3 — Open the Frontend
- Open `frontend/index.html` in your browser (double-click it)

---

## 🔐 Default Admin Credentials
| Username | Password |
|----------|----------|
| `shine`  | `262425` |

---

## 📋 Features

| Feature | Description |
|---------|-------------|
| 🕵️ Anonymous Submission | No login required for public users |
| 📂 9 Categories | Maintenance, Academics, Admin, Hostel, etc. |
| 🔍 Complaint Tracking | Track by unique ID (e.g. CB-A1B2C3D4) |
| 📊 Admin Dashboard | Pie chart + bar chart with live stats |
| ✏️ Status Update | Pending → In Progress → Resolved |
| 📅 Timeline View | Full history of every status change |
| 🔔 Notifications | Logged in DB, can be wired to SMTP email |
| 🔐 Admin Login | JWT-secured admin panel |

---

## 📁 Project Structure

```
complain box/
├── backend/
│   ├── app.py              ← Flask entry point
│   ├── config.py           ← Configuration
│   ├── models.py           ← Database models
│   ├── database.py         ← DB init + seeding
│   ├── complain_box.db     ← SQLite (auto-created)
│   ├── requirements.txt
│   └── routes/
│       ├── complaints.py   ← Complaint CRUD + stats
│       └── auth.py         ← Admin login / JWT
│
├── frontend/
│   ├── index.html          ← Full SPA (open in browser)
│   └── styles.css          ← Dark mode design system
│
├── start_backend.bat       ← One-click backend start
└── README.md
```

---

## 🗄️ Database Tables

| Table | Purpose |
|-------|---------|
| `users` | Admin accounts |
| `categories` | Complaint categories |
| `complaints` | All complaints with tracking ID |
| `status_history` | Every status change log |
| `notifications` | Email/SMS log |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/complaints` | Submit a complaint |
| GET | `/api/complaints` | List all (admin) |
| GET | `/api/complaints/track/:id` | Track by ID (public) |
| PATCH | `/api/complaints/:id/status` | Update status |
| GET | `/api/dashboard/stats` | Dashboard statistics |
| GET | `/api/categories` | List categories |
| POST | `/api/auth/login` | Admin login |

---

## ✉️ Email Notifications (Optional)

To enable real email delivery, create a `.env` file in `backend/`:
```
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=your_app_password
```
> Use a Gmail App Password (not your regular password).
> Enable 2FA on Gmail first, then generate an App Password from Google Account settings.
