from flask import Blueprint, jsonify, request, abort

main = Blueprint('main', __name__)

# routes

@main.route('/', methods = ['GET'])
def Abort():
    abort(403)
    return jsonify({'status':-231,'message':'Aborted!'})
