import os
import secrets
import jwt,uuid
from functools import wraps
from flask import jsonify, request, current_app
from app.models import User,UserData,Otp
from PIL import Image
from flask_mail import Message
from datetime import datetime as dt, timedelta as td
from app import mail
from app import db

class AuthUtil:
    def auth_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'x-api-key' in request.headers:
                token = request.headers['x-api-key']
            if not token:
                return jsonify({'message':'Invalid auth data!', 'status':-235}), 401
            try:
                payload = jwt.decode(token, current_app.config['SECRET_KEY'])
                sess_instance_user = User.query.filter_by(public_id=payload['username']).first()
            except:
               return jsonify({'message':'Session ended', 'status':-201}), 401
            return f(sess_instance_user, *args, **kwargs)
        return decorated

class UserUtil:
    def save_picture(form_picture):
        random_hex = secrets.token_hex()
        f_name, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(current_app.root_path, 'static/src-profiles', picture_fn)
        output_size = (125, 125)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
        return picture_fn
    def send_email(user, otp, message = None):
        message_f = message
        if not message:
            message_f = ('Thank you for openning a {} account. It is time to earn! Please use the following OTP to confirm your email and activate your account. OTP: {}').format(current_app.config['APP_NAME'], otp)
        msg = Message('Digital Employee', sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
        msg.body = (message_f)
        mail.send(msg)
    def create_otp(user):
        otp =  str(uuid.uuid4().int>>64)[0:6]
        new_otp = Otp(public_id=str(uuid.uuid4()), otp=otp, user=user.public_id)
        db.session.add(new_otp)
        db.session.commit()
        return otp
    def is_valid_otp(user, otp_in):
        now = dt.now()
        ten_min_ago = now - timedelta(minutes=10)
        otp_stored = Otp.query.filter(Otp.created_at > ten_min_ago).filter(Otp.created_at > now).filter(Otp.otp == otp_in, Otp.user == user.public_id)
        if otp_stored:
            return True
        return False
    def agency_code():
        return str(uuid.uuid4().int>>64)[0:10]
