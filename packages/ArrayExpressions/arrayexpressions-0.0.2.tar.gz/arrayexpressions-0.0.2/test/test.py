from ArrayExpressions import arrex
import math


def sin_func(**kwargs):
    # Gets the arguments
    k = kwargs['k']  # Parameter
    array = kwargs['array']  # Scope array
    tokens = kwargs['tokens']  # Tokens
    token_types = kwargs['token_types']  # Token Types
    index = kwargs['index']
    a = kwargs['a']  # The a
    b = kwargs['b']  # The b

    # Do any checks that need to be made for k, array, etc.

    # Interprets answer
    tokens_info = arrex.interpret_code(tokens, token_types, array, index, a, b)

    # Converts answer to python equivalent type as tokens_info[0][0] is the token and [0][1] is the token type
    answer = arrex.convert_token_with_token_type(tokens_info[0][0], tokens_info[1][0])

    # Do any needed checks
    if not isinstance(answer, (int, float)):
        arrex.call_error("Tokens inside are not of type float")

    # Return value
    return round(math.sin(math.radians(answer)), 10) #Returns the sin of degrees


func_dict = {
    "sin": sin_func
}

lst = [90, 180, 270, 360, 45, 30]

output = arrex.evaluate(lst, "e(sin(x))", [func_dict])

print(output)
