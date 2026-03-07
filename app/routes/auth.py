from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

# ---- REGISTER ----
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    # Block logged-in normal users only
    if current_user.is_authenticated and not current_user.is_admin:
        return redirect(url_for('index.html'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password != confirm:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))

        # Prevent creating admin from public register
        if User.query.filter_by(username=username, is_admin=True).first():
            flash('Username not allowed', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# ---- LOGIN ----
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated and not current_user.is_admin:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):

            # Admin must login from admin panel
            if user.is_admin:
                flash("Admins must login from the admin panel.", "danger")
                return redirect(url_for("admin.login"))

            login_user(user)
            return redirect(url_for("main.home"))

        flash("Invalid username or password", "danger")

    return render_template('login.html')


# ---- LOGOUT ----
@auth_bp.route('/logout')
@login_required
def logout():

    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    logout_user()
    flash('You have been logged out', 'info')

    return redirect(url_for('index.html'))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":
        username = request.form.get("username")

        user = User.query.filter_by(username=username).first()

        if user and not user.is_admin:
            token = user.get_reset_token()

            reset_link = url_for("auth.reset_password", token=token, _external=True)

            # Normally you would send email here
            print("Reset link:", reset_link)

            flash("Password reset link has been generated. Check server logs.", "info")
            return redirect(url_for("auth.login"))

        flash("User not found or not allowed.", "danger")

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    user = User.verify_reset_token(token)

    if not user or user.is_admin:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        password = request.form.get("password")

        user.set_password(password)
        db.session.commit()

        flash("Your password has been updated. You can now login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")