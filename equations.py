# Adjust length and filename to get the number of valid non-distinct equations of that length, using only + - / * and **
# (leading zeros allowed)
length = 7
filename = f"data/allequationsfor{length}.txt"

operators = ["+", "-", "/", "*"]
equals = ["="]
compatible = {
    "+": ["-", "+"],
    "-": ["+", "-"],
    "/": [],
    "*": ["*"],
    "**": ["+","-"]
}


def _get_options(length, current_equation):
    # Returns a list of options to check for the next character. Length is the desired length of the equation.

    numbers = list(str(x) for x in range(10))
    # Most recent char
    previous_char = current_equation[-1] if len(current_equation) else ""
    # Most two recent chars
    previous_chars = current_equation[-2:] if len(current_equation) > 1 else ""
    options = numbers
    if len(current_equation) == 0:
        # First character of equation
        return numbers + ["+", "-"]
    if len(current_equation) == length - 1 and previous_char == "/":
        # Don't divide by zero on last step
        options.remove("0")
    if previous_chars == "/0":
        # Only way to continue this equation is by adding another number in front of the leading zero.
        # Can't have an operator following, or an equal sign.
        return numbers
    if "=" not in current_equation:
        # No equal sign yet
        if previous_char not in operators:
            # Previous character is a number
            if len(current_equation) == length - 1:
                # If no equal sign, and this is our last character to place, there are no valid equations from this
                # point forward
                return None
            if len(current_equation) == length - 2:
                # Two spots left, this one needs to be an equal sign
                return equals
            # Otherwise, add the equal sign to the options
            options += equals
        else:
            # The previous char is an operator
            if len(current_equation) == length - 2:
                # Two spots left, need an equal side, and something to come after the operator, and something to go on
                # the right hand side. This is not possible with two characters
                return None
    if previous_char not in equals and len(current_equation) < length - 1:
        # We have at least 2 more spots left, and previous char isn't an equal sign
        if previous_char not in operators:
            # Previous char is a number, so add operators
            options += operators
        else:
            # Previous char is an operator, add the compatible operators to follow the previous operator.
            # Ex: - or - can follow + (+-1=1)
            options += compatible[previous_char]
    if previous_char in equals and len(current_equation) < length - 1:
        # We have at least 2 more spots left, and previous char is an equal sign
        options += ["+", "-"]
    if previous_chars == "**":
    	if "*" in options:
	        # If most two recent characters are **, remove * from the options, since we don't want ***
    	    options.remove("*")
    	if len(current_equation) < length - 1:
    		# Allow positive or negative exponents ex: 1**+1=1
	    	options += compatible[previous_chars]
    return options


def _strip_leading_zeros(equation):
    # Returns a reformatted version of equation that can be evaluated by python's eval() function
    # Takes out leading 0s, but leaves 0's on their own.
    previous_char = None
    next_char = equation[1]
    getting_number = True
    new_equation = ""
    for x, char in enumerate(equation):
        next_char = equation[x + 1] if x + 1 < len(equation) else None
        if getting_number and char == "0":
            if next_char in operators + equals or len(equation) == x + 1:
                new_equation += char
            continue
        if char != "0":
            getting_number = False
        if char in operators + equals:
            getting_number = True
        new_equation += char
    return new_equation


def get_possible_equations(length, filename, current_equation=""):
    # recursively gets called, and adds the next line of characters to the current equation.
    # If an equation is valid it is appended to a file
    options = _get_options(length, current_equation)
    if not options:
        # If there are no options, then return
        return
    for option in options:
        new_equation = current_equation + option
        if new_equation.count("=") > 1:
            # If there are more than 1 equal signs, continue to next iteration
            continue
        if len(new_equation) > length:
            # Too long, return to next iteration
            continue
        elif len(new_equation) == length:
            # Equation is right length, evaluate it.
            if new_equation.count("=") != 1:
                continue
            # Equation to be evaluated
            eval_equation = _strip_leading_zeros(new_equation.replace("=", "=="))
            try:
                evaluation = eval(eval_equation)
            except ZeroDivisionError:
                # Catch if we divide by zero
                evaluation = False
            except:
                # Log if we fail eval for other reason, to investigate
                print((new_equation, eval_equation), file=open("failed.txt", "a"))
                evaluation = False
            if evaluation:
                # The equation is valid, append to the file
                print(new_equation, file=open(filename, "a"))
                continue
            continue
        else:
            # Needs to be longer, call the function again.
            get_possible_equations(length, filename, new_equation)


open(filename, "w").truncate()
open("failed.txt", "w").truncate()
get_possible_equations(length, filename)