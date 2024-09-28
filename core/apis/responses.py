from flask import Response, jsonify, make_response


class APIResponse(Response):
    @classmethod
    def respond(cls, data=None, message=None, error=None, status_code=200):
        response_data = {}
        
        if message:
            response_data['message'] = message
        if error:
            response_data['error'] = error
        if data is not None:
            response_data['data'] = data
            
        return make_response(jsonify(response_data), status_code)
