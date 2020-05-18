from flask import Blueprint, jsonify, request,current_app, make_response
from app.models import User,UserData,AgencyCode
from app import db
import uuid,jwt,datetime
from werkzeug.security import generate_password_hash,check_password_hash
from app.utils import AuthUtil, UserUtil as uu

users = Blueprint('users', __name__)

# handle 404
@users.errorhandler(404)
def invalid_route(e):
    f = open(str(current_app.config['LOGS_PATH']), 'a+')
    f.write(str(err))
    f.close()
    return jsonify({'status':-234,'message':'Seek failure'})
# routes
@users.route('/api/v0/users', methods = ['GET'])
@AuthUtil.auth_required
def find_all(sess_instance_user):
    if not sess_instance_user.is_admin:
        return jsonify({'status':-236, 'message':'Permission denied'})
    try:
        users = User.query.all()
        rtn = []
        for user in users:
            dt = {}
            dt['public_id'] = user.public_id
            dt['email'] = user.email
            dt['image_file'] = user.image_file
            dt['password'] = user.password
            dt['is_admin'] = user.is_admin
            dt['is_agent'] = user.is_agent
            dt['last_login'] = user.last_login
            dt['has_profile'] = user.has_profile
            dt['created_at'] = user.created_at
            rtn.append(dt)
        return jsonify({'status':0,'users':rtn})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

@users.route('/api/v0/users/<public_id>', methods = ['GET'])
@AuthUtil.auth_required
def find_one(sess_instance_user,public_id):
    try:
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return jsonify({'status':0,'users':None})
        rtn = []
        dt = {}
        dt['public_id'] = user.public_id
        dt['email'] = user.email
        dt['image_file'] = user.image_file
        dt['password'] = user.password
        dt['is_admin'] = user.is_admin
        dt['is_agent'] = user.is_agent
        dt['last_login'] = user.last_login
        dt['has_profile'] = user.has_profile
        dt['created_at'] = user.created_at
        rtn.append(dt)            
        return jsonify({'status':0,'user':rtn})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

@users.route('/api/v0/users', methods = ['POST'])
# NO login required for users  sign up
def create_one():
    try:
        data = request.get_json()
        hashed_password = generate_password_hash(data['password'], method = 'sha256')
        auto_gen_id = str(uuid.uuid4())
        user = User(public_id=auto_gen_id,email=data['email'],password=hashed_password)
        db.session.add(user)
        db.session.commit()
        created_user = User.query.filter_by(public_id=auto_gen_id).first()
        otp = uu.create_otp(created_user)
        uu.send_email(created_user, otp)
        return jsonify({'status':0, 'created_user_id':auto_gen_id, 'message':'Account created. A one-time-password has been send to your email. Use it to complete account setup'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

@users.route('/api/v0/de-o-adms', methods = ['POST'])
@AuthUtil.auth_required
def create_one_admin(sess_instance_user):
    if not sess_instance_user.is_admin:
        return jsonify({'status':-236, 'message':'Permission denied'})
    try:
        data = request.get_json()
        hashed_password = generate_password_hash(data['password'], method = 'sha256')
        auto_gen_id = str(uuid.uuid4())
        user = User(public_id=auto_gen_id,email=data['email'],password=hashed_password,is_admin=True)
        db.session.add(user)
        db.session.commit()
        created_user = User.query.filter_by(public_id=auto_gen_id)
        otp = uu.create_otp(created_user)
        uu.send_email(created_user, otp)
        return jsonify({'status':0, 'created_user_id':auto_gen_id, 'message':'Account created. A one-time-password has been send to your email. Use it to complete account setup'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

@users.route('/api/v0/users/toagent/<public_id>', methods = ['PUT'])
@AuthUtil.auth_required
def to_agent(sess_instance_user,public_id):
    if not sess_instance_user.is_admin:
        return jsonify({'status':-236, 'message':'Permission denied'})
    try:
        user = User.query.filter_by(public_id=public_id, is_agent=False).first()
        if not user:
            return jsonify({'status':0,'message':'User with this role does not exist'})
        user.is_agent = True
        db.session.commit()
        return jsonify({'status':0,'message':'User updated to agent'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

@users.route('/api/v0/users/toregular/<public_id>', methods = ['PUT'])
@AuthUtil.auth_required
def to_regular(sess_instance_user,public_id):
    if not sess_instance_user.is_admin:
        return jsonify({'status':-236, 'message':'Permission denied'})
    try:
        user = User.query.filter_by(public_id=public_id, is_agent=True).first()
        if not user:
            return jsonify({'status':0,'message':'User with this role does not exist'})
        user.is_agent = False
        db.session.commit()
        return jsonify({'status':0,'message':'User updated to regular'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})
########################
## USER DATA   
#######################
@users.route('/api/v0/users/data/<public_id>', methods = ['POST'])
@AuthUtil.auth_required
def add_user_data(sess_instance_user,public_id):
    if not sess_instance_user.is_admin and sess_instance_user.public_id != public_id:
        return jsonify({'status':-236, 'message':'Permission denied'})
    try:
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return jsonify({'status':1,'message':'User not found'})
        data = request.get_json()
        user_data = UserData(first_name=data['fname'],middle_name=data['mname'],sir_name=data['sname'],phone=data['phone'],national_id=data['national_id'],next_of_kin_name=data['next_of_kin_name'],next_of_kin_email=data['next_of_kin_email'], next_of_kin_phone=data['next_of_kin_name'],user_id=user.public_id)
        db.session.add(user_data)
        user.has_profile = True
        db.session.commit()
        return jsonify({'status':0,'message':'User profile updated successfully!'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

@users.route('/api/v0/users/data/<public_id>', methods = ['PUT'])
@AuthUtil.auth_required
def update_user_data(sess_instance_user,public_id):
    if not sess_instance_user.is_admin and sess_instance_user.public_id != public_id:
        return jsonify({'status':-236, 'message':'Permission denied'})
    try:
        user_data = UserData.query.filter_by(user_id=public_id).first()
        if not user_data:
            return jsonify({'status':0,'message':'User info not found'})
        data = request.get_json()
        user_data.first_name = data['fname']
        user_data.middle_name = data['mname']
        user_data.sir_name = data['sname']
        user_data.phone = data['phone']
        user_data.national_id = data['national_id']
        user_data.next_of_kin_name = data['next_of_kin_name']
        user_data.next_of_kin_email = data['next_of_kin_email']
        user_data.next_of_kin_phone = data['next_of_kin_name']
        db.session.commit()
        return jsonify({'status':0,'message':'User profile data updated successfully!'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

@users.route('/api/v0/users/data/<public_id>', methods = ['GET'])
@AuthUtil.auth_required
def get_user_data(sess_instance_user,public_id):
    if not sess_instance_user.is_admin and sess_instance_user.public_id != public_id:
        return jsonify({'status':-236, 'message':'Permission denied'})
    try:
        user_data = UserData.query.filter_by(user_id=public_id).first()
        if not user_data:
            return jsonify({'status':0,'message':'User info not found'})
        rtn = []
        dt = {}
        dt['user_id'] = user_data.user_id
        dt['first_name'] = user_data.first_name
        dt['middle_name'] = user_data.middle_name
        dt['sir_name'] = user_data.sir_name
        dt['phone'] = user_data.phone
        dt['national_id'] = user_data.national_id
        dt['next_of_kin_name'] = user_data.next_of_kin_name
        dt['next_of_kin_email'] = user_data.next_of_kin_email
        dt['next_of_kin_phone'] = user_data.next_of_kin_phone
        dt['created_at'] = user_data.created_at
        rtn.append(dt)
        return jsonify({'status':0,'data':rtn})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

@users.route('/api/v0/users/<public_id>', methods = ['DELETE'])
@AuthUtil.auth_required
def delete(sess_instance_user,public_id):
    if not sess_instance_user.is_admin:
        return jsonify({'status':-236, 'message':'Permission denied'})
    user = User.query.filter_by(public_id=public_id).first()
    user_data = UserData.query.filter_by(user_id=public_id).first()
    if not user:
        return jsonify({'status':0, 'message':'User not found'})
    user.delete()
    user_data.delete()
    return jsonify({'status':0, 'message':'User removed successfully!'})
    
@users.route('/api/v0/auth/resetpwd/<email>', methods = ['POST'])
def resetpwd(sess_instance_user, email):
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'status':0, 'message':'User not found'})
        data = request.get_json()
        user.password = generate_password_hash(data['password'], method = 'sha256')
        db.session.commit()
        return jsonify({'status':0,'message':'user password updated!'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

@users.route('/api/v0/auth/otp/validate', methods = ['POST'])
@AuthUtil.auth_required
def validate_otp(sess_instance_user):
    try:
        data = request.get_json()
        is_valid = uu.is_valid_otp(sess_instance_user, data['otp'])
        if not is_valid:
            return jsonify({'status':-233,'message':'Invalid OTP'})
        return jsonify({'status':0,'message':'authenticated!'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})
@users.route('/api/v0/auth/validate', methods = ['POST'])
@AuthUtil.auth_required
def validate(sess_instance_user):
    try:
        if sess_instance_user.public_id:
            return jsonify({'payload':{'status':0, 'expired':False, 'message':'Session is active'}})
        else:
            return jsonify({'payload':{'status':0, 'expired':True, 'message':'Session is expired'}})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

@users.route('/api/v0/userdata/refresh/<public_id>', methods = ['POST'])
@AuthUtil.auth_required
def refresh(sess_instance_user, public_id):
    try:
        if sess_instance_user.public_id != public_id:
            return jsonify({'status':0, 'message':'Not allowed to access this'})
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return jsonify({'status':0, 'message':'Not found'})
        dt = {}
        dt['public_id'] = user.public_id
        dt['email'] = user.email
        dt['image_file'] = user.image_file
        dt['password'] = user.password
        dt['is_admin'] = user.is_admin
        dt['is_agent'] = user.is_agent
        dt['last_login'] = user.last_login
        dt['has_profile'] = user.has_profile
        dt['created_at'] = user.created_at
        user_data = UserData.query.filter_by(user_id=user.public_id).first()
        if user_data:
            dt['user_id'] = user_data.user_id
            dt['first_name'] = user_data.first_name
            dt['middle_name'] = user_data.middle_name
            dt['sir_name'] = user_data.sir_name
            dt['phone'] = user_data.phone
            dt['national_id'] = user_data.national_id
            dt['next_of_kin_name'] = user_data.next_of_kin_name
            dt['next_of_kin_email'] = user_data.next_of_kin_email
            dt['next_of_kin_phone'] = user_data.next_of_kin_phone
            dt['profile_updated_at'] = user_data.created_at
        return jsonify({'payload':{'status':0, 'logged_user':dt, 'message':'Success! User information fetched'}})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

@users.route('/api/v0/auth', methods = ['POST'])
def login():
    try:
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return make_response('Access Denied!', 401, {'WWW-Authenticate' : 'Basic real="Auth headers required!"'})
        user = User.query.filter_by(email=auth.username).first()
        if not user:
            return make_response('Access Denied for current credentials!', 401, {'WWW-Authenticate' : 'Basic real="Permission required!"'})
        if check_password_hash(user.password, auth.password):
            auth_token = jwt.encode({'username':user.public_id, 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'])
            otp = uu.create_otp(user)
            uu.send_email(user, otp)
            dt = {}
            dt['public_id'] = user.public_id
            dt['email'] = user.email
            dt['image_file'] = user.image_file
            dt['password'] = user.password
            dt['is_admin'] = user.is_admin
            dt['is_agent'] = user.is_agent
            dt['last_login'] = user.last_login
            dt['has_profile'] = user.has_profile
            dt['created_at'] = user.created_at
            user_data = UserData.query.filter_by(user_id=user.public_id).first()
            if user_data:
                dt['user_id'] = user_data.user_id
                dt['first_name'] = user_data.first_name
                dt['middle_name'] = user_data.middle_name
                dt['sir_name'] = user_data.sir_name
                dt['phone'] = user_data.phone
                dt['national_id'] = user_data.national_id
                dt['next_of_kin_name'] = user_data.next_of_kin_name
                dt['next_of_kin_email'] = user_data.next_of_kin_email
                dt['next_of_kin_phone'] = user_data.next_of_kin_phone
                dt['profile_updated_at'] = user_data.created_at
            return jsonify({'payload':{'status':0, 'otp_sent':otp, 'logged_user':dt, 'token':auth_token.decode('utf-8'),'message':'Success! Otp has been send to your email address'}})
        return make_response('User/Password mismatch. Access Denied!', 401, {'WWW-Authenticate' : 'Basic real="Permission required!"'})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

# AGENCY CODES
@users.route('/api/v0/users/agencycodes/<public_id>', methods = ['POST'])
@AuthUtil.auth_required
def generate(sess_instance_user, public_id):
    try:
        if sess_instance_user.public_id != public_id:
            return jsonify({'status':0, 'message':'Not allowed to access this'})
        agency_code = uu.agency_code()
        if not agency_code:
            return jsonify({'status':0, 'message':'Not found'})
        auto_gen_id = str(uuid.uuid4())
        useragencycode = AgencyCode(public_id=auto_gen_id,code=agency_code,user_id=public_id)
        db.session.add(useragencycode)
        db.session.commit()
        return jsonify({'payload':{'status':0, 'generated_code':agency_code, 'message':'Success!'}})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})

@users.route('/api/v0/users/agencycodes/<public_id>', methods = ['GET'])
@AuthUtil.auth_required
def getbyagent(sess_instance_user, public_id):
    try:
        if sess_instance_user.public_id != public_id:
            return jsonify({'status':0, 'message':'Not allowed to access this'})
        agency_codes = AgencyCode.query.filter_by(user_id=public_id).first()
        if not agency_codes:
            return jsonify({'status':0, 'message':'Not found'})
        return jsonify({'payload':{'status':0, 'agency_code':agency_codes.code, 'date_code_created':agency_codes.created_at, 'message':'Success!'}})
    except Exception as err:
        f = open(str(current_app.config['LOGS_PATH']), 'a+')
        f.write(str(err))
        f.close()
        return jsonify({'status':-233,'message':'Invalid request payload params'})
