import math
from flask import Flask, jsonify, make_response, request

myServer = Flask(__name__)
myServer.config['JSON_SORT_KEYS'] = False
stack = []


@myServer.route('/stack/size', methods=["GET"])
def get_stack_size():
    result = len(stack)
    response = {"result": result, "error-message": None}
    return make_response(jsonify(response), 200)


@myServer.route('/stack/arguments', methods=["PUT"])
def add_arguments():
    args = request.get_json()
    args = args["arguments"]
    stack.extend(args)
    result = len(stack)
    response = {"result": result, "error-message": None}
    return make_response(jsonify(response), 200)


@myServer.route('/stack/arguments', methods=["DELETE"])
def delete_arguments():
    args = request.args
    count = args.get('count', type=int)
    error_message = None
    result = None
    error_code = 200
    if len(stack) >= count:
        for i in range(count):
            stack.pop()
        result = len(stack)
    else:
        error_message = "Error: cannot remove {} from the stack. It has only {} arguments".format(count, len(stack))
        error_code = 409
    response = {"result": result, "error-message": error_message}
    return make_response(jsonify(response), error_code)


def calc_operation(data, operation_name):
    error_message = None
    result = None
    if operation_name.lower() == 'plus':
        result = data.pop() + data.pop()
    elif operation_name.lower() == 'minus':
        if data == stack:
            result = data.pop() - data.pop()
        else:
            result = data[0] - data[1]
    elif operation_name.lower() == 'times':
        result = data.pop() * data.pop()
    elif operation_name.lower() == 'divide':
        if data == stack:
            if data[-2] == 0:
                error_message = "Error while performing operation Divide: division by 0"
                data.pop()
                data.pop()
            else:
                result = data.pop() // data.pop()
        else:
            if data[1] == 0:
                error_message = "Error while performing operation Divide: division by 0"
            else:
                result = data[0] // data[1]
    elif operation_name.lower() == 'pow':
        if data == stack:
            result = pow(data.pop(), data.pop())
        else:
            result = pow(data[0], data[1])
    elif operation_name.lower() == 'abs':
        result = abs(data.pop())
    elif operation_name.lower() == 'fact':
        if data[len(data) - 1] < 0:
            error_message = "Error while performing operation Factorial: not supported for the negative number"
            data.pop()
        else:
            result = math.factorial(data.pop())
    response = {"result": result, "error-message": error_message}
    return response


def create_response_calc_operation(data, operation_name):
    accepted_operations1 = {'abs', 'fact'}
    accepted_operations2 = {'plus', 'minus', 'times', 'divide', 'pow'}
    if (len(data) < 2 and operation_name.lower() in accepted_operations2) or \
            (len(data) < 1 and operation_name.lower() in accepted_operations1):
        if data == stack:
            error_message = "Error: cannot implement operation {}. It requires {} arguments and the stack has only {} arguments"
            if operation_name.lower() in accepted_operations1:
                error_message = error_message.format(operation_name, 1, len(data))
            else:
                error_message = error_message.format(operation_name, 2, len(data))
        else:
            error_message = "Error: Not enough arguments to perform the operation {}".format(operation_name)
        return make_response(jsonify({"result": None, "error-message": error_message}), 409)
    elif operation_name.lower() not in accepted_operations1 and operation_name.lower() not in accepted_operations2:
        error_message = "Error: unknown operation: {}".format(operation_name)
        return make_response(jsonify({"result": None, "error-message": error_message}), 409)
    else:
        result = calc_operation(data, operation_name)
        error_code = 200
        result_message = result["error-message"]
        if result_message is not None:
            error_code = 409
        return make_response(jsonify(result), error_code)


@myServer.route('/stack/operate', methods=["GET"])
def calc_operation_stack():
    args = request.args
    operation_name = args.get('operation', type=str)
    return create_response_calc_operation(stack, operation_name)


@myServer.route('/independent/calculate', methods=["POST"])
def calc_independent_calculation():
    args = request.get_json()
    accepted_operations1 = {'abs', 'fact'}
    accepted_operations2 = {'plus', 'minus', 'times', 'divide', 'pow'}
    operation_name = args["operation"]
    data = args["arguments"]
    if (len(data) > 2 and operation_name.lower() in accepted_operations2) or \
            (len(data) > 1 and operation_name.lower() in accepted_operations1):
        error_message = "Error: Too many arguments to perform the operation {}".format(operation_name)
        response = {"result": None, "error-message": error_message}
        return make_response(jsonify(response), 409)
    elif (len(data) < 2 and operation_name.lower() in accepted_operations2) or \
            (len(data) < 1 and operation_name.lower() in accepted_operations1):
        error_message = "Error: Not enough arguments to perform the operation {}".format(operation_name)
        response = {"result": None, "error-message": error_message}
        return make_response(jsonify(response), 409)
    else:
        return create_response_calc_operation(data, operation_name)


if __name__ == '__main__':
    myServer.run(host='localhost', port=8496)


