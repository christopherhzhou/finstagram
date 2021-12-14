from uuid import uuid1
import json

from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_app.utils import current_time
from flask_login import current_user, login_required, login_user, logout_user

from .. import bcrypt
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, SearchForm
from ..models import User

import plotly
import plotly.graph_objects as go


users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("posts.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")

        id = uuid1().hex
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed, uid=id)

        user.save()

        return redirect(url_for("users.login"))

    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("posts.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            return redirect(url_for("posts.index"))
        else:
            flash("Login failed. Check your username and/or password")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("users.login"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    username_form = UpdateUsernameForm()

    num_users = len(User.objects())
    num_followers = len(
        [u for u in User.objects() if current_user.uid in u.following])

    labels = ['Followers', 'Non-followers']
    values = [num_followers, num_users - num_followers]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    if username_form.validate_on_submit():
        # current_user.username = username_form.username.data
        current_user.modify(username=username_form.username.data)
        current_user.save()
        return redirect(request.path)

    return render_template(
        "account.html",
        title="Account",
        username_form=username_form,
        current_user=current_user,
        graphJSON=graphJSON
    )


@users.route('/search', methods=["GET", "POST"])
@login_required
def search_users():
    search_form = SearchForm()

    if search_form.validate_on_submit():
        query = search_form.query.data
        search_results = [
            user for user in User.objects() if query in user.username]
        return render_template(
            "search_users.html",
            form=search_form,
            search_results=search_results
        )

    return render_template(
        "search_users.html",
        form=search_form,
    )
