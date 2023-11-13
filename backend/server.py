import logging
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from functools import partial
from token_processing import requires_auth, create_access_token, verify_refresh_token
from auth import auth_endpoint
from mongo import initialize_collection_from_schema
import jsonschema
import json
import os

# Initialize logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

schema_dir = './schema'


# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    logging.info(f"health: {request.method} {request.path}")
    return jsonify({'status': 'healthy'}), 200


@app.route('/refresh_token', methods=['POST'])
def refresh_token():
    refresh_token = request.json.get('refresh_token')
    if not refresh_token:
        return jsonify({'error': 'Missing refresh token'}), 400

    valid, payload = verify_refresh_token(refresh_token, token_type='refresh')
    if not valid:
        return jsonify({'error': 'Invalid refresh token'}), 401

    new_access_token = create_access_token(payload['sub'])
    return jsonify({'access_token': new_access_token})


@requires_auth
def create(model_name, schema, collection, username):
    logging.info(f"create: {request.method} {request.path}")
    try:
        item = request.json

        if schema['properties'].get('owner', None):
            item['owner'] = username

        jsonschema.validate(instance=item, schema=schema)
        collection.insert_one(item)
        logging.info(f"Item successfully created in {model_name}")
        return jsonify({'status': 'success'}), 201
    except jsonschema.ValidationError as e:
        logging.error(f"Validation Error in POST /{model_name}: {str(e)}")
        return jsonify({'error': str(e)}), 400


@requires_auth
def read(model_name, collection, username):
    logging.info(f"read: {request.method} {request.path}")
    try:
        items = list(collection.find())

        logging.info(
            f"Items successfully retrieved from {model_name}: {items}")
        return jsonify(items), 200
    except Exception as e:
        logging.error(f"Error in GET /{model_name}: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500


@requires_auth
def update(model_name, schema, collection, item_id, username):
    logging.info(f"update: {request.method} {request.path}")
    try:
        # If item.owner exists, check if authorized user is owner
        if 'owner' in schema['properties']:
            item = collection.find_one({'_id': ObjectId(item_id)})
            if item['owner'] != username:
                logging.error(
                    f"User {username} is not the owner of item {item_id}")
                return jsonify({'error': 'Unauthorized'}), 401

        # If model is user and username does not match, return unauthorized
        if model_name == 'user':
            item = collection.find_one({'_id': ObjectId(item_id)})
            if item['username'] != username:
                logging.error(
                    f"User {username} is not the owner of item {item_id}")
                return jsonify({'error': 'Unauthorized'}), 401

        item = request.json
        jsonschema.validate(instance=item, schema=schema)

        collection.replace_one({'_id': ObjectId(item_id)}, item)

        # Get whole item from database
        item = collection.find_one({'_id': ObjectId(item_id)})

        # remove _id field
        item.pop('_id', None)

        return jsonify({'status': 'success', 'data': item}), 200

    except jsonschema.ValidationError as e:
        logging.error(f"Validation Error in PUT /{model_name}: {str(e)}")
        return jsonify({'error': str(e)}), 400


@requires_auth
def delete(model_name, collection, item_id, username):
    logging.info(f"delete: {request.method} {request.path}")
    try:
        # If item.owner exists, check if authorized user is owner
        if 'owner' in schema['properties']:
            item = collection.find_one({'_id': ObjectId(item_id)})
            if item['owner'] != username:
                logging.error(
                    f"User {username} is not the owner of item {item_id}")
                return jsonify({'error': 'Unauthorized'}), 401

        # If model is user and username does not match, return unauthorized
        if model_name == 'user':
            item = collection.find_one({'_id': ObjectId(item_id)})
            if item['username'] != username:
                logging.error(
                    f"User {username} is not the owner of item {item_id}")
                return jsonify({'error': 'Unauthorized'}), 401

        result = collection.delete_one({'_id': ObjectId(item_id)})
        if result.deleted_count == 1:
            logging.info(f"Item successfully deleted from {model_name}")
            return jsonify({'status': 'success'}), 200
        else:
            logging.error(f"Item not found in DELETE /{model_name}")
            return jsonify({'error': 'Item not found'}), 404
    except Exception as e:
        logging.error(f"Error in DELETE /{model_name}: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500


app.add_url_rule('/auth', 'auth_endpoint',
                 auth_endpoint, methods=['POST'])


@app.route('/static_events', methods=['GET'])
def list_events():
    # Load static events from static_events.json
    logging.info(f"list_events: {request.method} {request.path}")
    static_events = []
    with open('static_events.json') as f:
        static_events = json.load(f)
        logging.info(f"Static events successfully retrieved")

    return jsonify(static_events), 200


if __name__ == '__main__':
    client = MongoClient('mongo', 27017)
    db = client['swag']
    app.config['ENV'] = 'development'

    for filename in os.listdir(schema_dir):
        if filename.endswith('.json'):
            model_name = filename[:-5]

            schema, collection = initialize_collection_from_schema(
                model_name,
                os.path.join(schema_dir, filename),
                db
            )

            app.add_url_rule(f'/{model_name}', f'create_{model_name}',
                             partial(create, model_name, schema, collection), methods=['POST'])
            app.add_url_rule(f'/{model_name}', f'read_{model_name}',
                             partial(read, model_name, collection), methods=['GET'])
            app.add_url_rule(f'/{model_name}/<string:item_id>', f'update_{model_name}',
                             partial(update, model_name, schema, collection), methods=['PUT'])
            app.add_url_rule(f'/{model_name}/<string:item_id>', f'delete_{model_name}',
                             partial(delete, model_name, collection), methods=['DELETE'])

    app.run(host='0.0.0.0', port=5000, debug=True)
