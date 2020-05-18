from flask import Blueprint, jsonify, request, redirect, abort, url_for, render_template
main = Blueprint('main', __name__)
# routes
@main.route('/', methods = ['GET'])
def Abort():
    return redirect(url_for('main.index'))
    # abort(403)

@main.route('/default.tpl', methods = ['GET'])
def index():
    title = 'DE App'
    return render_template('dflt.html', title = title)
