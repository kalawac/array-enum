from flask import make_response, abort
import uuid

def validate_intID(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        abort(make_response({"message": f"{cls.__name__} {model_id} invalid"}, 400))

    instance = cls.query.get(model_id)

    if not instance:
        abort(make_response({"message": f"{cls.__name__} {model_id} not found"}, 404))

    return instance

def validate_UUID(cls, model_id):
    # invalid UUIDs are handled and rejected by flask-UUID: 404, no message.

    instance = cls.query.get(model_id)

    if not instance:
        abort(make_response({"message": f"{cls.__name__} {model_id} not found"}, 404))

    return instance

def append_dicts_to_list(objects):
    return [object.to_dict() for object in objects]