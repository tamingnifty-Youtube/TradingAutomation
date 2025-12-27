
def calculater(x, y, operation):
    if operation == 'add':
        return x + y
    elif operation == 'subtract':
        return x - y
    elif operation == 'multiply':
        return x * y
    elif operation == 'divide':
        if y != 0:
            return x / y
        else:
            return "Error: Division by zero"
    else:
        return "Error: Invalid operation"
    
print(calculater(10, 5, 'add'))
print(calculater(10, 5, 'subtract'))
print(calculater(10, 5, 'multiply'))
print(calculater(10, 5, 'divide'))
print(calculater(10, 0, 'divide'))
print(calculater(10, 5, 'modulus'))