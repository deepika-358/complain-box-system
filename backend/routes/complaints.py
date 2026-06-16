from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid

try:
    from backend.database import db
    from backend.models import Complaint, Category, StatusHistory, Notification, User
except ImportError:
    from database import db
    from models import Complaint, Category, StatusHistory, Notification, User

complaints_bp = Blueprint("complaints", __name__)


# ─── Submit Anonymous Complaint ───────────────────────────────────────────────
@complaints_bp.route("/api/complaints", methods=["POST"])
def submit_complaint():
    data = request.get_json()

    # Validate required fields
    if not data.get("title") or not data.get("description") or not data.get("category_id"):
        return jsonify({"error": "title, description, and category_id are required"}), 400

    category = Category.query.get(data["category_id"])
    if not category:
        return jsonify({"error": "Invalid category"}), 400

    # Generate unique tracking ID
    tracking_id = f"CB-{str(uuid.uuid4())[:8].upper()}"

    complaint = Complaint(
        tracking_id=tracking_id,
        title=data["title"],
        description=data["description"],
        category_id=data["category_id"],
        priority=data.get("priority", "medium"),
        is_anonymous=data.get("is_anonymous", True),
        submitter_email=data.get("submitter_email") or None,
        status="pending",
    )
    db.session.add(complaint)
    db.session.flush()  # get ID before commit

    # Log initial status
    history = StatusHistory(
        complaint_id=complaint.id,
        old_status=None,
        new_status="pending",
        note="Complaint submitted",
    )
    db.session.add(history)

    # Send notification to responsible staff
    _notify_staff(complaint, category)

    db.session.commit()

    return jsonify({
        "message": "Complaint submitted successfully",
        "tracking_id": tracking_id,
        "complaint": complaint.to_dict(),
    }), 201


# ─── Track complaint by tracking ID (public) ──────────────────────────────────
@complaints_bp.route("/api/complaints/track/<tracking_id>", methods=["GET"])
def track_complaint(tracking_id):
    complaint = Complaint.query.filter_by(tracking_id=tracking_id.upper()).first()
    if not complaint:
        return jsonify({"error": "Complaint not found. Check your tracking ID."}), 404

    history = [h.to_dict() for h in complaint.status_logs]
    result = complaint.to_dict()
    result["history"] = history
    return jsonify(result)


# ─── Get all complaints (admin) ────────────────────────────────────────────────
@complaints_bp.route("/api/complaints", methods=["GET"])
def get_complaints():
    status_filter = request.args.get("status")
    category_filter = request.args.get("category_id")
    priority_filter = request.args.get("priority")

    query = Complaint.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category_id=int(category_filter))
    if priority_filter:
        query = query.filter_by(priority=priority_filter)

    complaints = query.order_by(Complaint.created_at.desc()).all()
    return jsonify([c.to_dict() for c in complaints])


# ─── Get categories ────────────────────────────────────────────────────────────
@complaints_bp.route("/api/categories", methods=["GET"])
def get_categories():
    cats = Category.query.all()
    return jsonify([c.to_dict() for c in cats])


# ─── Update complaint status (admin) ──────────────────────────────────────────
@complaints_bp.route("/api/complaints/<int:complaint_id>/status", methods=["PATCH"])
def update_status(complaint_id):
    data = request.get_json()
    complaint = Complaint.query.get_or_404(complaint_id)

    old_status = complaint.status
    new_status = data.get("status")
    if new_status not in ("pending", "in_progress", "resolved"):
        return jsonify({"error": "Invalid status"}), 400

    complaint.status = new_status
    complaint.updated_at = datetime.utcnow()

    if data.get("assigned_to"):
        complaint.assigned_to = data["assigned_to"]

    history = StatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=data.get("admin_id"),
        note=data.get("note", ""),
    )
    db.session.add(history)

    # Notify submitter if they gave email
    if complaint.submitter_email and new_status == "resolved":
        notif = Notification(
            complaint_id=complaint.id,
            type="email",
            recipient=complaint.submitter_email,
            message=f"Your complaint [{complaint.tracking_id}] has been resolved.",
            status="sent",
        )
        db.session.add(notif)

    db.session.commit()
    return jsonify({"message": "Status updated", "complaint": complaint.to_dict()})


# ─── Dashboard stats ───────────────────────────────────────────────────────────
@complaints_bp.route("/api/dashboard/stats", methods=["GET"])
def dashboard_stats():
    total = Complaint.query.count()
    pending = Complaint.query.filter_by(status="pending").count()
    in_progress = Complaint.query.filter_by(status="in_progress").count()
    resolved = Complaint.query.filter_by(status="resolved").count()

    # By category
    categories = Category.query.all()
    by_category = []
    for cat in categories:
        count = Complaint.query.filter_by(category_id=cat.id).count()
        by_category.append({"name": cat.name, "count": count, "color": cat.color})

    # By priority
    by_priority = {
        "high": Complaint.query.filter_by(priority="high").count(),
        "medium": Complaint.query.filter_by(priority="medium").count(),
        "low": Complaint.query.filter_by(priority="low").count(),
    }

    # Recent 7
    recent = Complaint.query.order_by(Complaint.created_at.desc()).limit(7).all()

    return jsonify({
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "by_category": by_category,
        "by_priority": by_priority,
        "recent": [c.to_dict() for c in recent],
    })


# ─── Internal: notify staff ────────────────────────────────────────────────────
def _notify_staff(complaint, category):
    if not category.responsible_email:
        return
    notif = Notification(
        complaint_id=complaint.id,
        type="email",
        recipient=category.responsible_email,
        message=(
            f"New complaint [{complaint.tracking_id}] in '{category.name}':\n"
            f"Title: {complaint.title}\n"
            f"Priority: {complaint.priority}\n"
            f"Description: {complaint.description[:200]}"
        ),
        status="sent",
    )
    db.session.add(notif)


# ─── Delete a status history entry (admin) ─────────────────────────────────
@complaints_bp.route("/api/history/<int:history_id>", methods=["DELETE"])
def delete_history(history_id):
    history = StatusHistory.query.get(history_id)
    if not history:
        return jsonify({"error": "History entry not found"}), 404

    # Remove the history entry
    db.session.delete(history)
    db.session.commit()
    return jsonify({"message": "History entry deleted"})


# ─── Delete a complaint (admin) ────────────────────────────────────────────
@complaints_bp.route("/api/complaints/<int:complaint_id>", methods=["DELETE"])
def delete_complaint(complaint_id):
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404

    # Delete associated history and notifications
    StatusHistory.query.filter_by(complaint_id=complaint_id).delete()
    Notification.query.filter_by(complaint_id=complaint_id).delete()
    
    # Delete the complaint
    db.session.delete(complaint)
    db.session.commit()
    return jsonify({"message": "Complaint deleted successfully"})
