from datetime import datetime
import bcrypt
import uuid

try:
    from backend.database import db
except ImportError:
    from database import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default="staff")   # admin | staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    responsible_email = db.Column(db.String(120), default="")
    color = db.Column(db.String(20), default="#6366f1")
    complaints = db.relationship("Complaint", backref="category", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "responsible_email": self.responsible_email,
            "color": self.color,
        }


class Complaint(db.Model):
    __tablename__ = "complaints"
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(20), unique=True, nullable=False, default=lambda: f"CB-{str(uuid.uuid4())[:8].upper()}")
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    status = db.Column(db.String(20), default="pending")   # pending | in_progress | resolved
    priority = db.Column(db.String(10), default="medium")  # low | medium | high
    is_anonymous = db.Column(db.Boolean, default=True)
    submitter_email = db.Column(db.String(120), nullable=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignee = db.relationship("User", foreign_keys=[assigned_to], backref="assigned_complaints")
    status_logs = db.relationship("StatusHistory", backref="complaint", lazy=True, order_by="StatusHistory.changed_at")
    notifications_sent = db.relationship("Notification", backref="complaint", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "tracking_id": self.tracking_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.to_dict() if self.category else None,
            "status": self.status,
            "priority": self.priority,
            "is_anonymous": self.is_anonymous,
            "submitter_email": self.submitter_email,
            "assigned_to": self.assignee.to_dict() if self.assignee else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class StatusHistory(db.Model):
    __tablename__ = "status_history"
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    note = db.Column(db.Text, default="")
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship("User", foreign_keys=[changed_by])

    def to_dict(self):
        return {
            "id": self.id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "changed_by": self.admin.username if self.admin else "System",
            "note": self.note,
            "changed_at": self.changed_at.isoformat(),
        }


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=False)
    type = db.Column(db.String(10), default="email")  # email | sms
    recipient = db.Column(db.String(120))
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(10), default="sent")  # sent | failed

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "recipient": self.recipient,
            "message": self.message,
            "sent_at": self.sent_at.isoformat(),
            "status": self.status,
        }
