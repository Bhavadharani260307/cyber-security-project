"""
Frontend Page Render Views Blueprint
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from backend.app.security.decorators import admin_required

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("views.dashboard_view"))
    return redirect(url_for("auth.login"))


@views_bp.route("/dashboard")
@login_required
def dashboard_view():
    return render_template("dashboard.html", user=current_user)


@views_bp.route("/traffic-analysis")
@login_required
def traffic_analysis_view():
    return render_template("traffic_analysis.html", user=current_user)


@views_bp.route("/single-predict")
@login_required
def single_predict_view():
    return render_template("single_predict.html", user=current_user)


@views_bp.route("/alerts")
@login_required
def alerts_view():
    return render_template("alerts.html", user=current_user)


@views_bp.route("/reports")
@login_required
def reports_view():
    return render_template("reports.html", user=current_user)


@views_bp.route("/model-metrics")
@login_required
def model_metrics_view():
    return render_template("model_metrics.html", user=current_user)


@views_bp.route("/user-management")
@login_required
@admin_required
def user_management_view():
    return render_template("user_management.html", user=current_user)
