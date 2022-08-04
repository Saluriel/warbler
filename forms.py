from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, InputRequired


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class EditUserForm(FlaskForm):
    """Form for editing the current user"""

    username = StringField("New Username")
    email = StringField("New Email Address")
    image_url=StringField("New profile image url")
    header_image_url=StringField("New header image url")
    bio = StringField("Edit Bio")
    password = StringField("Current Password", validators=[InputRequired()])
