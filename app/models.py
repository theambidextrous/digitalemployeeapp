from datetime import datetime
from flask import current_app #to replace static app variable
from app import db

# User
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True, nullable = False)
    email = db.Column(db.String(50), unique = True, nullable = False)
    image_file = db.Column(db.String(20), default = 'default.jpg', nullable = False)
    password = db.Column(db.String(80), nullable = False)
    is_admin = db.Column(db.Boolean, nullable = False ,default = False)
    is_agent = db.Column(db.Boolean, nullable = False ,default = False)
    last_login = db.Column(db.Boolean, nullable = False ,default = False)
    has_profile = db.Column(db.Boolean, nullable = False ,default = False)
    user_data = db.relationship('UserData', backref='user', lazy = True)
    agency_code = db.relationship('AgencyCode', backref='user', lazy = True)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
# User data
class UserData(db.Model):
    __tablename__ = 'user_data'
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(20), unique = False, nullable = False)
    middle_name = db.Column(db.String(20), unique = False, nullable = False)
    sir_name = db.Column(db.String(20), unique = False, nullable = False)
    phone = db.Column(db.String(15), unique = True, nullable = False)
    national_id = db.Column(db.String(20), unique = True, nullable = False)
    next_of_kin_name = db.Column(db.String(50), unique = False, nullable = False)
    next_of_kin_email = db.Column(db.String(50), unique = True, nullable = False)
    next_of_kin_phone = db.Column(db.String(50), unique = True, nullable = False)
    user_id = db.Column(db.String(80), db.ForeignKey('user.public_id'), nullable = False,  unique = True)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
# Otp
class Otp(db.Model):
    __tablename__ = 'otp'
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(80), unique = True, nullable = False)
    user = db.Column(db.String(80), unique = False, nullable = False)
    otp = db.Column(db.Integer, unique = False, nullable = False)
    expired = db.Column(db.Boolean, default = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
# Agency Code
class AgencyCode(db.Model):
    __tablename__ = 'agency_code'
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(80), unique = True, nullable = False)
    code = db.Column(db.String(16), unique = True, nullable = False)
    user_id = db.Column(db.String(80), db.ForeignKey('user.public_id'), nullable = False,  unique = True)
    referral = db.relationship('Referral', backref='agency_code', lazy = True)
    is_active = db.Column(db.Boolean, nullable = False, default = True)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
# Referral
class Referral(db.Model):
    __tablename__ = 'referral'
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(80), unique = True, nullable = False)
    trxn_code = db.Column(db.String(30), unique = True, nullable = False)
    trxn_ai_key = db.Column(db.Integer, unique = True, nullable = False)
    trxn_tracking_id = db.Column(db.String(30), unique = True, nullable = False)
    trxn_account = db.Column(db.String(30), unique = False, nullable = False)
    trxn_amount = db.Column(db.Float, unique = False, nullable = False)
    trxn_type = db.Column(db.String(10), unique = False, nullable = False)
    comm_code = db.Column(db.String(80), unique = False, nullable = False)
    agent_code = db.Column(db.String(16), db.ForeignKey('agency_code.code'), nullable = False,  unique = False)
    created_by = db.Column(db.String(80), nullable = False,  unique = False)
    referral_trxn = db.relationship('Transaction', backref='referral', lazy = True)
    is_active = db.Column(db.Boolean, nullable = False, default = True)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
# Transaction
class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(80), unique = True, nullable = False)
    trxn_init_code = db.Column(db.String(30), db.ForeignKey('referral.trxn_code'), nullable = False,  unique = True)
    trxn_ai_key = db.Column(db.Integer, unique = True, nullable = False)
    trxn_tracking_id = db.Column(db.String(30), unique = True, nullable = False)
    trxn_account = db.Column(db.String(30), unique = False, nullable = False)
    trxn_amount = db.Column(db.Float, unique = False, nullable = False)
    trxn_type = db.Column(db.String(10), unique = False, nullable = False)
    trxn_cr_amt = db.Column(db.Float, unique = False, nullable = False)
    trxn_dr_amt = db.Column(db.Float, unique = False, nullable = False)
    reducing_bal = db.Column(db.Float, unique = False, nullable = False)
    agency_comm_amt = db.Column(db.Float, unique = False, nullable = False)
    accu_comm_amt = db.Column(db.Float, unique = False, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
# Withdrawal
class Withdrawal(db.Model):
    __tablename__ = 'withdrawal'
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(80), unique = True, nullable = False)
    trxn_init_code = db.Column(db.String(30), nullable = False,  unique = False)
    trxn_amount = db.Column(db.Float, unique = False, nullable = False)
    trxn_type = db.Column(db.String(10), unique = False, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
# Commission
class Commission(db.Model):
    __tablename__ = 'commission'
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(80), unique = True, nullable = False)
    name = db.Column(db.String(10), unique = True, nullable = False)
    value = db.Column(db.Float, unique = False, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)





