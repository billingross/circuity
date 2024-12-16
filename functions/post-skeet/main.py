import os
import re
import pdb
import json
import logging

# Functions framework for Python: https://pypi.org/project/functions-framework/
import flask 
import functions_framework

from google.cloud import storage

@functions_framework.http
def post_skeet_http(request: flask.request) -> flask.typing.ResponseReturnValue:
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'skeet' in request_json:
        name = request_json['skeet']
    elif request_args and 'skeet' in request_args:
        name = request_args['skeet']
    else:
        return 'Error: Could not parse skeet from request.'
    return 'Posting skeet: "{}".'.format(name)
