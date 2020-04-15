from flask import Blueprint, jsonify, request,current_app, make_response
from app.models import User,UserData,ApproveKind
from app import db
import uuid,jwt,datetime
from werkzeug.security import generate_password_hash,check_password_hash
from app.utils import AuthUtil
from app.utils import SysAccess as sa

users = Blueprint('users', __name__)

# handle 404
@users.errorhandler(404)
def invalid_route(e):
    f = open(str(current_app.config['LOGS_PATH']), 'a+')
    f.write(str(err))
    f.close()
    return jsonify({'status':-234,'error':'Seek failure'})

# routes
@users.route('/api/v0/users', methods = ['GET'])
@AuthUtil.auth_required
def findAll(sess_instance_user):
    if not sess_instance_user.isadmin:
        return jsonify({'status':-236, 'error':'Permission denied'})
    try:
        users = User.query.all()
        rtn = []
        for user in users:
            dt = {}
            dt['public_id'] = user.public_id
            dt['name'] = user.name
            dt['email'] = user.email
            dt['isadmin'] = user.isadmin
            dt['image_file'] = user.image_file
            dt['can_approve_vpn'] = user.can_approve_vpn
            dt['can_approve_svr'] = user.can_approve_svr
            dt['can_approve_vpn_as'] = user.can_approve_vpn_as
            dt['can_approve_svr_as'] = user.can_approve_svr_as
            dt['last_login'] = user.last_login
            dt['created_at'] = user.created_at
            rtn.append(dt)
        return jsonify({'status':0,'users':rtn})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})

@users.route('/api/v0/users/<public_id>', methods = ['GET'])
@AuthUtil.auth_required
def findOne(sess_instance_user,public_id):
    # if not sess_instance_user.isadmin and not sess_instance_user.can_approve_svr and not sa.can_approve(sess_instance_user.public_id, public_id) and sess_instance_user.public_id != public_id:
    #         return jsonify({'status':-236, 'error':'Permission denied. Only admins, approvers, Line managers & self allowed'})
    try:
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return jsonify({'status':0,'users':None})
        rtn = []
        dt = {}
        dt['public_id'] = user.public_id
        dt['name'] = user.name
        dt['email'] = user.email
        dt['isadmin'] = user.isadmin
        dt['image_file'] = user.image_file
        dt['can_approve_vpn'] = user.can_approve_vpn
        dt['can_approve_svr'] = user.can_approve_svr
        dt['can_approve_vpn_as'] = user.can_approve_vpn_as
        dt['can_approve_svr_as'] = user.can_approve_svr_as
        dt['last_login'] = user.last_login
        dt['created_at'] = user.created_at
        rtn.append(dt)            
        return jsonify({'status':0,'user':rtn})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})

@users.route('/api/v0/users', methods = ['POST'])
# @AuthUtil.auth_required
def create():
    db.create_all()
    # if not sess_instance_user.isadmin:
    #     return jsonify({'status':-236, 'error':'Permission denied'})
    try:
        data = request.get_json()
        hashed_password = generate_password_hash(data['password'], method = 'sha256')
        auto_gen_id = str(uuid.uuid4())
        user = User(public_id=auto_gen_id,name=data['name'],email=data['email'],password=hashed_password,isadmin=data['isadmin'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'status':0, 'created_user_id':auto_gen_id, 'message':'New user created!'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})

@users.route('/api/v0/users/<public_id>', methods = ['POST'])
@AuthUtil.auth_required
def update(sess_instance_user, public_id):
    if not sess_instance_user.isadmin and sess_instance_user.public_id != public_id:
        return jsonify({'status':-236, 'error':'Permission denied'})
    try:
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return jsonify({'status':-404, 'message':'User not found'})
        data = request.get_json()
        user.name = data['name']
        user.email = data['email']
        user.isadmin = data['isadmin']
        db.session.commit()
        return jsonify({'status':0,'message':'user updated!'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})

@users.route('/api/v0/users/<public_id>', methods = ['PUT'])
@AuthUtil.auth_required
def promote(sess_instance_user,public_id):
    if not sess_instance_user.isadmin:
        return jsonify({'status':-236, 'error':'Permission denied'})
    try:
        user = User.query.filter_by(public_id=public_id, isadmin=False).first()
        if not user:
            return jsonify({'status':0,'message':'User is either an admin already or does not exist'})
        user.isadmin = True
        db.session.commit()
        return jsonify({'status':0,'message':'User promoted to admin'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})

""" Aprrove permissions ++++++++++++++++++++++++++++++++ """
""" Aprrove permissions ++++++++++++++++++++++++++++++++ """

@users.route('/api/v0/users/approvevpn/<public_id>', methods = ['PUT'])
@AuthUtil.auth_required
def can_approve_vpn(sess_instance_user,public_id):
    if not sess_instance_user.isadmin:
        return jsonify({'status':-236, 'error':'Permission denied'})
    try:
        user = User.query.filter_by(public_id=public_id, can_approve_vpn=False, isadmin=False).first()
        if not user:
            return jsonify({'status':0,'message':'User is either a vpn approver already or does not exist'})
        user.can_approve_vpn = True
        db.session.commit()
        return jsonify({'status':0,'message':'User promoted to vpn approver'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})

@users.route('/api/v0/users/approvevpnas/<public_id>', methods = ['PUT'])
@AuthUtil.auth_required
def can_approve_vpn_as(sess_instance_user,public_id):
    if not sess_instance_user.isadmin:
        return jsonify({'status':-236, 'error':'Permission denied'})
    try:
        data = request.get_json()
        user = User.query.filter_by(public_id=public_id, isadmin=False).first()
        if not user:
            return jsonify({'status':0,'message':'User does not exist'})
        apr_kind = ApproveKind.query.filter_by(kind_type=data['can_approve_vpn_as']).first()
        if not apr_kind:
            return jsonify({'status':0,'message':'Invalid Approval Kind'})
        user.can_approve_vpn_as = data['can_approve_vpn_as']
        db.session.commit()
        return jsonify({'status':0,'message':'User promoted to vpn approver'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})

@users.route('/api/v0/users/approveserver/<public_id>', methods = ['PUT'])
@AuthUtil.auth_required
def can_approve_svr(sess_instance_user,public_id):
    if not sess_instance_user.isadmin:
        return jsonify({'status':-236, 'error':'Permission denied'})
    try:
        user = User.query.filter_by(public_id=public_id, can_approve_svr=False, isadmin=False).first()
        if not user:
            return jsonify({'status':0,'message':'User is either a server approver already or does not exist'})
        user.can_approve_svr = True
        db.session.commit()
        return jsonify({'status':0,'message':'User promoted to server approver'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})
@users.route('/api/v0/users/approveserveras/<public_id>', methods = ['PUT'])
@AuthUtil.auth_required
def can_approve_svr_as(sess_instance_user,public_id):
    if not sess_instance_user.isadmin:
        return jsonify({'status':-236, 'error':'Permission denied'})
    try:
        data = request.get_json()
        user = User.query.filter_by(public_id=public_id,isadmin=False).first()
        if not user:
            return jsonify({'status':0,'message':'User does not exist'})
        apr_kind = ApproveKind.query.filter_by(kind_type=data['can_approve_svr_as']).first()
        if not apr_kind:
            return jsonify({'status':0,'message':'Invalid Approval Kind'})
        user.can_approve_svr_as = data['can_approve_svr_as']
        db.session.commit()
        return jsonify({'status':0,'message':'User promoted to vpn approver'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})

""" End ++++++++++++++++++++++++++++++++ """
""" End ++++++++++++++++++++++++++++++++ """


@users.route('/api/v0/users/info/<public_id>', methods = ['POST'])
@AuthUtil.auth_required
def add_more_info(sess_instance_user,public_id):
    if not sess_instance_user.isadmin and sess_instance_user.public_id != public_id:
        return jsonify({'status':-236, 'error':'Permission denied'})
    try:
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return jsonify({'status':0,'message':'User not found'})
        data = request.get_json()
        user_info = UserData(employee_id=data['employee_id'],phone=data['phone'],department=data['department'],function=data['function'],user_id=public_id)
        db.session.add(user_info)
        db.session.commit()
        return jsonify({'status':0,'message':'User data added successfully!'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})

@users.route('/api/v0/users/info/<public_id>', methods = ['PUT'])
@AuthUtil.auth_required
def updated_more_info(sess_instance_user,public_id):
    if not sess_instance_user.isadmin and sess_instance_user.public_id != public_id:
        return jsonify({'status':-236, 'error':'Permission denied'})
    try:
        user_data = UserData.query.filter_by(user_id=public_id).first()
        if not user_data:
            return jsonify({'status':0,'message':'User info not found'})
        data = request.get_json()
        user_data.employee_id=data['employee_id']
        user_data.phone=data['phone']
        user_data.department=data['department']
        user_data.function=data['function']
        db.session.commit()
        return jsonify({'status':0,'message':'User data updated successfully!'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})

@users.route('/api/v0/users/info/<public_id>', methods = ['GET'])
@AuthUtil.auth_required
def get_more_info(sess_instance_user,public_id):
    if not sess_instance_user.isadmin and sess_instance_user.public_id != public_id:
        return jsonify({'status':-236, 'error':'Permission denied'})
    try:
        user_data = UserData.query.filter_by(user_id=public_id).first()
        if not user_data:
            return jsonify({'status':0,'message':'User info not found'})
        rtn = []
        dt = {}
        dt['user_id'] = user_data.user_id
        dt['employee_id'] = user_data.employee_id
        dt['phone'] = user_data.phone
        dt['department'] = user_data.department
        dt['function'] = user_data.function
        dt['created_at'] = user_data.created_at
        rtn.append(dt)
        return jsonify({'status':0,'data':rtn})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})

@users.route('/api/v0/users/<public_id>', methods = ['DELETE'])
@AuthUtil.auth_required
def delete(sess_instance_user):
    pass

@users.route('/api/v0/auth/resetpwd/<email>', methods = ['POST'])
def resetpwd(sess_instance_user, email):
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'status':-404, 'message':'User not found'})
        data = request.get_json()
        user.password = generate_password_hash(data['password'], method = 'sha256')
        db.session.commit()
        return jsonify({'status':0,'message':'user password updated!'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params'})

@users.route('/api/v0/auth', methods = ['POST'])
def login():
    # db.create_all()
    try:
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return make_response('Access Denied!', 401, {'WWW-Authenticate' : 'Basic real="Auth headers required!"'})
        user = User.query.filter_by(email=auth.username).first()

        if not user:
            return make_response('Access Denied for current credentials!', 401, {'WWW-Authenticate' : 'Basic real="Permission required!"'})
        if check_password_hash(user.password, auth.password):
            auth_token = jwt.encode({'username':user.public_id, 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'])
            return jsonify({'status':0, 'logged_user_id':user.public_id,'token':auth_token.decode('utf-8')})
        return make_response('User/Password mismatch. Access Denied!', 401, {'WWW-Authenticate' : 'Basic real="Permission required!"'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'error':'Invalid request payload params' + str(err)})
