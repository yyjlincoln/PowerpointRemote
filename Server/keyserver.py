import threading
from flask import Flask, request, jsonify
import mongoengine as me
from flask_mongoengine import MongoEngine
from dbconnect import keycollection
from copy import deepcopy

app = Flask(__name__)

app.config['MONGODB_SETTINGS']={
    'db':'premote',
    "host": "localhost",
    "port": 27017
}

MongoEngine().init_app(app)


@app.route('/obtain')
def obtainkey():
    rand = request.values.get('rand')
    if rand:
        query = keycollection.query(rand=rand)
        if query:
            query = query.first()
            key = deepcopy(query.key)
            query.delete()
            query.save() # Ensures it can only be accessed once.
            return jsonify({
                'key':key
            })
        return jsonify({
            'error':'No pending key collection!'            
        })
    return jsonify({
        'error':'No rand'
    })
