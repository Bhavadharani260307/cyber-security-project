"""
Authentication & User Management Blueprint
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from backend.app.database import db
from backend.app.models.user import User
from backend.app.security.decorators import admin_required
from backend.app.services.audit_service import AuditService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.dashboard_view"))

    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            username = data.get("username", "").strip()
            password = data.get("password", "")
        else:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            AuditService.log_event("USER_LOGIN_SUCCESS", f"User {username} logged in successfully.")
            if request.is_json:
                return jsonify({"message": "Login successful", "user": user.to_dict()}), 200
            return redirect(url_for("views.dashboard_view"))

        AuditService.log_event("USER_LOGIN_FAILED", f"Failed login attempt for username '{username}'.")
        if request.is_json:
            return jsonify({"error": "Invalid username or password"}), 401
        flash("Invalid username or password", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    username = current_user.username
    logout_user()
    AuditService.log_event("USER_LOGOUT", f"User {username} logged out.")
    if request.is_json:
        return jsonify({"message": "Logged out successfully"}), 200
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")

        if not username or not email or not password:
            msg = "Username, email, and password are required."
            return (jsonify({"error": msg}), 400) if request.is_json else (flash(msg, "danger") or render_template("auth/register.html"))

        if User.query.filter_by(username=username).first():
            msg = "Username already exists."
            return (jsonify({"error": msg}), 400) if request.is_json else (flash(msg, "danger") or render_template("auth/register.html"))

        if User.query.filter_by(email=email).first():
            msg = "Email already registered."
            return (jsonify({"error": msg}), 400) if request.is_json else (flash(msg, "danger") or render_template("auth/register.html"))

        new_user = User(username=username, email=email, role="Analyst")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        AuditService.log_event("USER_REGISTERED", f"New user account created: {username}")
        if request.is_json:
            return jsonify({"message": "User registered successfully", "user": new_user.to_dict()}), 201

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/users", methods=["GET"])
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([u.to_dict() for u in users]), 200
