import jwt
from functools import wraps
from flask import jsonify, request, current_app
from app.models import User,Department,UserData,Approveserver,Approvevpn,ServerRequest,VpnRequest
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

class SysAccess:
    def can_approve(instance_user, user_id):
        user_dept = UserData.query.filter_by(user_id=user_id).first()
        if not user_dept: #user has no department
            return False
        isuserlinemanager = Department.query.filter_by(line_manager=instance_user, dept_id=user_dept.department).first()
        if not isuserlinemanager:# is not user's line manager
            return False
        return True
    def is_approved_svr(request_id):
        user_req_aprvl_count = Approveserver.query.filter(Approveserver.request_id==request_id,Approveserver.approve_as != '00').count()
        if not user_req_aprvl_count:
            raise Exception("This request has no approvals. But why?")
            return False
        if user_req_aprvl_count == 6:
            this_req = ServerRequest.query.filter_by(request_id=request_id).first()
            if not this_req:
                raise Exception("This request is not found. But why?")
            this_req.isapproved = True
            db.session.commit()
            return True
        return False
    def is_approved_vpn(request_id):
        user_req_aprvl_count = Approvevpn.query.filter(Approvevpn.request_id==request_id, Approvevpn.approve_as != '00').count()
        if not user_req_aprvl_count:
            raise Exception("This request has no approvals. But why?")
            return False
        if user_req_aprvl_count == 3:
            this_req = VpnRequest.query.filter_by(request_id=request_id).first()
            if not this_req:
                raise Exception("This request is not found. But why?")
            this_req.isapproved = True
            db.session.commit()
            return True
        return False