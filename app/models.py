from datetime import datetime
from flask import current_app #to replace static app variable
from app import db

# All::users
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True, nullable = False)
    name = db.Column(db.String(50), unique = True, nullable = False)
    email = db.Column(db.String(50), unique = True, nullable = False)
    image_file = db.Column(db.String(20), default = 'default.jpg', nullable = False)
    password = db.Column(db.String(80), nullable = False)
    isadmin = db.Column(db.Boolean, nullable = False ,default = False)
    can_approve_vpn = db.Column(db.Boolean, nullable = False ,default = False)
    can_approve_svr = db.Column(db.Boolean, nullable = False ,default = False)
    can_approve_vpn_as = db.Column(db.Integer, nullable = False ,default = 0)
    can_approve_svr_as = db.Column(db.Integer, nullable = False ,default = 0)
    last_login = db.Column(db.Boolean, nullable = False ,default = False)
    user_info = db.relationship('UserData', backref='user_details', lazy = True)
    vpn = db.relationship('VpnRequest', backref='vpn_requestor', lazy = True)
    server = db.relationship('ServerRequest', backref='svr_requestor', lazy = True)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
# User::data
class UserData(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    employee_id = db.Column(db.String(30), unique = True, nullable = False)
    phone = db.Column(db.String(50), unique = True, nullable = False)
    department = db.Column(db.String(80), unique = False, nullable = False)
    function = db.Column(db.String(80), nullable = False)
    user_id = db.Column(db.String(80), db.ForeignKey('user.public_id'), nullable = False,  unique = True)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)

# ==================================
# Vpn
class VpnRequest(db.Model):
    __tablename__ = 'vpnrequest'
    id = db.Column(db.Integer, primary_key = True)
    request_id = db.Column(db.String(50), unique = True, nullable = False)
    request_info = db.relationship('Vpn', backref='vpnrequest', lazy = True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.public_id'), nullable = False)
    general_note = db.Column(db.Text, nullable = False, default = 'To gain access to Family Bank or its associated systems and/or infrastructure, the user must complete this form and it should be signed by the said user, the line manager, Information Security and the Director IT. Note: This is required information.')
    confidentiality_note = db.Column(db.Text, nullable = False, default = 'All system administration access is provided for official business of Family Bank. Family Bank computer systems and/or infrastructure are for the use of authorized users only. If one is suspected of unauthorized activities, IT or Information Security staff may monitor and record all session activities and action taken in line with the Bank policies. Anyone using these systems expressly consents to such monitoring')
    access_start = db.Column(db.Date, nullable = False)
    access_end = db.Column(db.Date, nullable = False)
    isexpired = db.Column(db.Boolean, nullable = False ,default = False)
    isapproved = db.Column(db.Boolean, nullable = False ,default = False)
    issubmitted = db.Column(db.Boolean, nullable = False ,default = False)
    # hasrejection = db.Column(db.Boolean, nullable = False ,default = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
class Vpn(db.Model):
    __tablename__ = 'vpn'
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True, nullable = False)
    server = db.Column(db.String(100), nullable = False)
    reason = db.Column(db.Text, nullable = False)
    access_type = db.Column(db.String(80), nullable = False)
    req_id = db.Column(db.String(50), db.ForeignKey('vpnrequest.request_id'), unique = True, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
    __table_args__ = (
        db.UniqueConstraint(server, req_id),
    )
# ==================================
# server access
class ServerRequest(db.Model):
    __tablename__ = 'serverrequest'
    id = db.Column(db.Integer, primary_key = True)
    request_id = db.Column(db.String(50), unique = True, nullable = False)
    request_type = db.Column(db.String(40), nullable = False)
    request_group = db.Column(db.String(40), nullable = False)
    request_info = db.relationship('Server', backref='serverrequest', lazy = True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.public_id'), nullable = False)
    preferred_id = db.Column(db.String(30), unique = True, nullable = False)
    general_note = db.Column(db.Text, nullable = False, default = 'DO NOT USE REGULAR DOMAIN MAIL ID FOR SECURITY REASONS')
    confidentiality_note = db.Column(db.Text, nullable = False,  default = 'To reduce the risk of the created user id being hijacked, it is requested that the Data Centre Manager be informed that regular requests to enable/disable the account will be made without having to refill this form again. A request to disable the account could be made, for example, at the end of the day, when work is not being done using the account, and then re-enabled the next day on resuming work')
    access_start = db.Column(db.Date, nullable = False)
    access_end = db.Column(db.Date, nullable = False)
    isexpired = db.Column(db.Boolean, nullable = False ,default = False)
    isapproved = db.Column(db.Boolean, nullable = False ,default = False)
    issubmitted = db.Column(db.Boolean, nullable = False ,default = False)
    # hasrejection = db.Column(db.Boolean, nullable = False ,default = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
class Server(db.Model):
    __tablename__ = 'server'
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True, nullable = False)
    server = db.Column(db.String(100), nullable = False)
    reason = db.Column(db.Text, nullable = False)
    access_rights = db.Column(db.String(80), nullable = False)
    access_matrix = db.Column(db.Text, nullable = False, default='all tables')
    req_id = db.Column(db.String(50), db.ForeignKey('serverrequest.request_id'), unique = True, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
    __table_args__ = (
        db.UniqueConstraint(server, req_id),
    )

# ======================================
# approvals
class Approvevpn(db.Model):
    __tablename__ = 'approvevpn'
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(80), unique = True, nullable = False)
    request_id = db.Column(db.String(80), unique = False, nullable = False)
    user_id = db.Column(db.String(80), unique = False, nullable = False)
    approved_by = db.Column(db.String(80), unique = False, nullable = False)
    remarks = db.Column(db.String(80), unique = False, nullable = False)
    approve_as = db.Column(db.Enum('1','3','4','00', name="approve_as"), nullable = False)
    approved_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
    __table_args__ = (
        db.UniqueConstraint(request_id, approve_as),
        db.UniqueConstraint(request_id, approved_by),
    )
class Approveserver(db.Model):
    __tablename__ = 'approveserver'
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(80), unique = True, nullable = False)
    request_id = db.Column(db.String(80), unique = False, nullable = False)
    user_id = db.Column(db.String(80), unique = False, nullable = False)
    approved_by = db.Column(db.String(80), unique = False, nullable = False)
    remarks = db.Column(db.String(80), unique = False, nullable = False)
    approve_as = db.Column(db.Enum('1','2','3','4','5','6','00', name="approve_as"), nullable = False)
    approved_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
    __table_args__ = (
        db.UniqueConstraint(request_id, approve_as),
        db.UniqueConstraint(request_id, approved_by),
    )
class RequestType(db.Model):
    __tablename__ = 'requesttype'
    id = db.Column(db.Integer, primary_key = True)
    type_id = db.Column(db.String(80), unique = True, nullable = False)
    # type_name = db.Column(db.String(100), nullable = False)
    type_name = db.Column(db.Enum("Vpn", "Server", name="type_name"), unique = True, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
# request categor
class RequestGroup(db.Model): #Id creation/deletion/password reset
    __tablename__ = 'requestgroup'
    id = db.Column(db.Integer, primary_key = True)
    group_id = db.Column(db.String(80), unique = True, nullable = False)
    group_name = db.Column(db.Enum("ID Creation", "ID Deletion", "ID Password Reset", name="group_name"), unique = True, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
# request categor
class Right(db.Model):
    __tablename__ = 'right'
    id = db.Column(db.Integer, primary_key = True)
    right_id = db.Column(db.String(80), unique = True, nullable = False)
    right_name = db.Column(db.String(100), nullable = False, unique = True)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
# Departments
class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key = True)
    dept_id = db.Column(db.String(80), unique = True, nullable = False)
    dept_name = db.Column(db.String(100), nullable = False, unique = True)
    line_manager = db.Column(db.String(100), unique = True, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)
# Approve as
class ApproveKind(db.Model):
    __tablename__ = 'approvekind'
    id = db.Column(db.Integer, primary_key = True)
    kind_type = db.Column(db.Integer, nullable = False, unique = True)
    kind_name = db.Column(db.String(100), nullable = False, unique = True)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)

