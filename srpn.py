#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import re
stack = []
comment = False

rand = [1804289383, 846930886, 1681692777, 1714636915, 1957747793, 424238335, 719885386,         1649760492, 596516649, 1189641421, 1025202362, 1350490027, 783368690, 1102520059,        2044897763, 1967513926, 1365180540, 1540383426, 304089172, 1303455736, 35005211,         521595368]
random_count = 0

operators = {"+", "-", "*", "/", "%", "^"}

#regular expressions:
operators_without_spaces_re = "[+/*^%]\d+" #any operator followed by some integers, not including negative numbers
two_ops_or_equals_re = "[\-+/*^%=][\-+/*^%=]" #2 consecutive operators or equals
sums_re = "-?\d+[\-+/*^%]\d+" #equations, so two integers with an operator between and no spaces, e.g. -3*4
negative_square_re = "-\d+\*\*\d+" # 
negative_power_re = "\^-(\d+)"


def process_individual(user_in):
    #Two conditions that check if the input matches these particular patterns, used further down in this if statement
    op_and_int = re.fullmatch(operators_without_spaces_re, user_in)
    two_ops = re.fullmatch(two_ops_or_equals_re, user_in)
    global comment
    #if the user enters a "#" all input will be ignored until second "#" entered
    if user_in == "#":
        comment = not comment
    elif comment:
        #function does nothing if comment is true
        pass
    elif user_in in operators:
        #if user enters an operator takes last two items in the stack and replaces with result of operation
        try:
            #starts by ensuring correct syntax for operators, e.g. ^ is replaced by **
            user_in = process_operators(user_in)
            #pop_numbers takes the last two items from the stack, prints an error if not enough items
            (x , y) = pop_numbers()
            result = eval(str(x) + user_in + str(y))
            #checks stack is not full and number is not too high or low, adds result to stack
            check_and_append_to_stack(result)
        except ZeroDivisionError:
            print("Divide by 0.")
        except TypeError:
            #stack underflow error dealt with in pop_numbers function
            pass
    elif user_in == "=":
        #prints the last item in the stack, or "Stack empty." if no items
        try:
            print(int(stack[-1]))
        except IndexError:
            print("Stack empty.")
    elif user_in == "d":
        #prints the stack (if stack empty SRPN prints -2147483648)
        for i in stack:
            print(int(i))
        if len(stack) == 0:
            print(-2147483648)
    elif user_in == "r":
        #adds next integer from random function to the stack (if not full)
        check_and_append_to_stack(random())
    elif user_in == "" or user_in == " ":
        #ignores empty entries or spaces
        pass 
    elif op_and_int:
        #detects if an operator followed directly by an integer is entered
        try:
            x = str(stack.pop())
            #calculates the result of the operation with infix notation, e.g is *5 will multiple last item in the stack by 5
            #negative numbers are not included in the regex so would append -5 rather than carrying out a calculation
            result = infix_notation(user_in, x)
            check_and_append_to_stack(result)
        except IndexError:
            #if stack is empty prints Stack underflow and appends the number to the stack without the operator
            print("Stack underflow.")
            num = remove_operator(user_in)
            check_and_append_to_stack(int(num))
    elif two_ops:
        #if two different operators (or "=") are entered they are processed in reverse
            a = user_in[0]
            b = user_in[1]
            process_individual(b)
            process_individual(a)
    else:
        if is_int(user_in):
            #if an integer is entered it is appended (taking into account saturation and if the stack is full)
            check_and_append_to_stack(int(user_in))
        elif len(user_in) == 1:
            #if a single unrecognised character is entered an error message is displayed
            print(f'Unrecognised operator or operand "{user_in}".')
        else:
            #any longer strings that do not fit an above pattern are run through a different function to break them up
            inputted_a_string(user_in)
            
        
        
        
def process_operators(user_in):
    #updates user_in so operators can be used correctly in python eval() function
    updated_user_in = user_in
    updated_user_in = updated_user_in.replace("^", "**")
    updated_user_in = updated_user_in.replace("/", "//")
    return updated_user_in


def pop_numbers():
    #tries to pop last two items off the stack
    try:
        y = stack.pop()
        try:
            x = stack.pop()
            return (x , y)
        except IndexError:
            #if len(stack) < 2 will print stack underflow
            #if able to pop y but not x, y is returned to the stack
            print("Stack underflow.")
            stack.append(y)
    except IndexError:
        print("Stack underflow.")
        

def check_number(num):
    #Ensures inputs/results saturate correctly
    if num > 2147483647:
        num = 2147483647
    elif num < -2147483648:
        num = -2147483648
    return str(num)


def check_and_append_to_stack(integer):
    #appends an integer to the stack as a string, tells user if stack full
    if len(stack) < 23:
        stack.append(check_number(integer))
    else:
        print("Stack overflow.")


def random():
    #generates the repeating list of random numbers used by the SRPN
    global random_count
    current_count = random_count
    random_count += 1
    if random_count == len(rand):
        random_count = 0
    return rand[current_count]


def infix_notation(user_in, last_entry):
    #takes two strings: user_in (which will be an operator followed by integer), and last_entry
    #evaluates the result with infix notation and returns result as a int
    updated_user_in = process_operators(user_in)
    result = eval(last_entry + updated_user_in)
    return result


def remove_operator(user_in):
    #removes the first character of a string, e.g *5 becomes 5
    to_remove_operator = list(user_in)
    without_operator = to_remove_operator[1:]
    return "".join(without_operator)
    

def is_int(string):
    #returns true if inputted string can be converted to an integer
    try:
        int(string)
        return True
    except ValueError:
        return False
    
    
def inputted_a_string(user_in):
    #first, if user tries to enter a negative power caclulator will remove this and print an error
    negative_pow = re.search(negative_power_re, user_in)
    if negative_pow:
        user_in = re.sub(negative_power_re, r" -\1", user_in)
        print("Negative power")
    #second, pre-processes string to perform any necessary inflix notation calculations
    pre_processed_user_in = pre_process_string(user_in)
    int_string = ""
    split_list = []
    #splits input string up into a list
    #keeps together any consecutive integers, or an operator followed by integers,
    for char in pre_processed_user_in:
        if char in operators and len(int_string) == 0:
            #operators can only be added to the start of the int_string
            int_string = int_string + char
        elif is_int(char):
            #any consecutive integers are added to the int_string
            int_string = int_string + char
        elif char in operators and len(int_string) > 0:
            #if there is then a subsequent operator the current int_string is added and a new one started
            #e.g. +5* will be split as +5, *
            split_list.append(int_string)
            int_string = char
        else:
            if len(int_string) > 0:
                #if there is any character that isn't an operator or integer the current int_string is appended 
                #the new character is then also appended 
                split_list.append(int_string)
                int_string = ""
            split_list.append(char)
    if len(int_string) > 0:
        #finally, any left over characters in the int_string are appended to create the complete list
        split_list.append(int_string)
    #runs each item through the calculator
    for i in range(len(split_list)):
        #when an operator is followed by an equals the SRPN prints the prev integer
        if split_list[i] == "=" and preceeding_operator(split_list[:i]):
            if last_int(split_list[:i]) is not None:
                print(last_int(split_list[:i]))
            else:
                #if there is no preceeding integer inthe string, prints the last item in the stack
                process_individual("=")
        else:
            process_individual(split_list[i])
                 
        
        
        
def last_int(split_list):
    #finds the last integer in a list
    for i in reversed(split_list):
        op_and_int = re.fullmatch(operators_without_spaces_re, i)
        if op_and_int:
            modified = remove_operator(i)
            return modified
        elif is_int(i):
            return i


def pre_process_string(user_in):
    #splits user_in by space and calculates any infix sums present, e.g. -4*3
    split_by_space = user_in.split()
    for i in range(len(split_by_space)):
        is_a_sum = re.fullmatch(sums_re, split_by_space[i])
        if is_a_sum:
            #ensures is in correct notation for eval function
            to_be_evaled = process_operators(split_by_space[i])
            negative_square = re.fullmatch(negative_square_re, to_be_evaled)
            #picks up equations that are a negative integer to some power, e.g. -3**2, corrects answer as eval() return -9
            if negative_square:
                split_by_space[i] = str(eval(to_be_evaled) *-1)
            else:
                split_by_space[i] = str(eval(to_be_evaled))
            
                
    #rejoins list as a string for further processing
    return " ".join(split_by_space)
        

def preceeding_operator(string):
    #checks from the end of a string if the last item (ignoring "=") is an operator
    for i in reversed(string):
        if i in operators:
            return True
        elif i == "=":
            pass
        else:
            return False


while True:
    user_in = input()
    process_individual(user_in)

