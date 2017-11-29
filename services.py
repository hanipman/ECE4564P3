#!/usr/bin/env python
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'accounts'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/accounts'

mongo = PyMongo(app)

auth = HTTPBasicAuth();

@auth.get_password
def get_pw(username):
    accounts = mongo.db.accounts
    accExists = accounts.find_one({'username': username})
    if accExists:
       return accExists['password'];
    return None

@app.route('/accounts', methods=['GET'])
@auth.login_required
def get_all_accounts():
    accounts = mongo.db.accounts
    output = []
    for s in accounts.find():
        output.append({'username': s['username'], 'password': s['password']})
    return jsonify({'Get all accounts': output})

@app.route('/accounts/<username>', methods=['GET'])
@auth.login_required
def get_one_accounts(username):
    accounts = mongo.db.accounts
    accExists = accounts.find_one({'username': username})
    if accExists:
        output = {'username': accExists['username'], 'password': accExists['password']}
    else:
        output = "Account does not exist"
    return jsonify({'Get account': output})


@app.route('/accounts', methods=['POST'])
@auth.login_required
def add_account():
    accounts = mongo.db.accounts
    username = request.values.get('username')
    password = request.values.get('password')
    accExists = accounts.find_one({'username': username})
    if accExists:
        output = "User already exists"
    else:
        accounts.insert_one({'username': username, 'password': password})
        accExists = accounts.find_one({'username': username, 'password': password})
        if accExists:
            output = {'username': accExists['username'], 'password': accExists['password']}
        else:
            output = "Unable to create account"
    return jsonify({'Created': output})

@app.route('/accounts', methods=['PUT'])
@auth.login_required
def update_password():
    accounts = mongo.db.accounts
    username = request.values.get('username')
    password = request.values.get('password')
    accExists = accounts.find_one({'username': username, 'password': password})
    if accExists:
        accounts.update_one({'username': username}, {'$set': {'password': password}}, upsert=False)
        updated_account = accounts.find_one({'username': username, 'password': password})
        if updated_account:
            output = {'username': updated_account['username'], 'password': updated_account['password']}
        else:
            output = "Unable to update password"
    else:
        output = "Account does not exist"
    return jsonify({'Updated': output})

@app.route('/accounts', methods=['DELETE'])
@auth.login_required
def remove_account():
    accounts = mongo.db.accounts
    username = request.values.get('username')
    password = request.values.get('password')
    accExists = accounts.find_one({'username': username, 'password': password})
    if accExists:
        accounts.remove({'username': username, 'password': password})
        removed_account = accounts.find_one({'username': username})
        if removed_account:
            output = "Unable to delete account"
        else:
            output = {'username': username, 'password': password}
    else:
        output = "Username and password do not match or account does not exist"
    return jsonify({'Deleted': output})

if __name__ == '__main__':
    app.run(debug=True)
