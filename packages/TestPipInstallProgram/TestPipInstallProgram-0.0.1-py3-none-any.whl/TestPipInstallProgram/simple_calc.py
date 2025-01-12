# Simple Calculater, attraction, subtraction, multiplication and division

def attraction(a,b):
    #Adds a and b together.
    c = a+b
    return(c)

def subtraction(a,b):
    #subtracts b from a.
    c = a-b
    return(c)

def multiplication(a,b):
    #Multiply a and b.
    c = a*b
    return(c)

def division(a,b):
    #divide a by b.
    try:    # Error handling if divition by 0
        c = a/b
        return(c)
    except Exception as Error:
        return(print(Error))
