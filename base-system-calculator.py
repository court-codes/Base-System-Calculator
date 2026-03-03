
#----------------------------
# DIGITS 2-36
#----------------------------

digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
import math

#----------------------------
# FUNCTIONS
#----------------------------

# 1) Checking if all digits in number are valid for the input base
def check_inputs(number_input, base_input):
  if number_input.startswith("-"):
    number_input = number_input[1:]
  
  for char in number_input.replace(".",""):
    if char not in digits[:int(base_input)]:
      print("Error")
      return False
  return True 

# 2) Converting to base 10
def convert_to_base10(number_input, base_input):
  is_negative = False
  if number_input.startswith("-"):
    is_negative = True
    number_input = number_input[1:]
    
  if not check_inputs(number_input, base_input):
    return None

  # A) Split number into whole and decimal parts
  if "." in number_input: 
    whole, fraction = number_input.split(".")
  else:
    whole = number_input
    fraction = ""
    
  # B) Convert whole part
  value = 0
  length_whole = len(whole)
  for x in range(length_whole):
    digit_value = digits.index(whole[x])
    power = length_whole - 1 - x
    value += digit_value * (int(base_input) ** power)
  
  # C) Convert decimal part
  length_fraction = len(fraction)
  for y in range(length_fraction): 
    digit_value = digits.index(fraction[y])
    power = -(y+1)
    value += digit_value * (int(base_input) ** power)
  
  return -value if is_negative else value

# 3) Converting from base 10 to desired base 
def convert_from_base10(value, desired_base_input):
  if value == 0:
    return "0"
  
  is_negative = False
  if value < 0:
    is_negative = True
    value = -value  
  
  result = ""
  
  # A) Split whole and fraction
  whole_part = int(value)
  fraction_part = value - whole_part
  
  # B) Convert whole part
  whole_result = ""
  while whole_part > 0:
    remainder = whole_part % int(desired_base_input)
    whole_result = digits[remainder] + whole_result
    whole_part //= int(desired_base_input) 
  
  # C) Convert fraction part 
  fraction_result = ""
  count = 0
  place_value = 15
  while fraction_part > 0 and count < place_value:
    fraction_part *= int(desired_base_input)
    digit = int(fraction_part)
    fraction_result += digits[digit]
    fraction_part -= digit
    count += 1
    
  # D) Combine whole and fraction parts for result
  if fraction_result:
    result = whole_result + "." + fraction_result
  else:
    result = whole_result
  
  if is_negative:
    result = "-" + result

  return result 

# 4) Checking if base is in range 
def check_base_range(base_input):
  if base_input < 2 or base_input > 36:
    print("Error: Base must be between 2 and 36.")
    exit()
  
#----------------------------
# INTRODUCTION
#----------------------------
print(" ")
print("BASE SYSTEM CALCULATOR")

print(" ")
print("Options: ")
print("")
print("+ -  x  /  √  n√ convert")
print(" ")


#----------------------------
# CALCULATIONS
#----------------------------

operation = input("Enter an operation: ").strip()

#----------------------------
# BASIC FOUR-WAY FUNCTIONS
#----------------------------
if operation == "+" or operation == "-" or operation == "x" or operation == "/": 
  number1_input = input("Enter the first number: ").strip().upper()
  number2_input = input("Enter the second number: ").strip().upper()
  base_input = input("Enter the base: ").strip()

  if not base_input.isdigit():
    print("Error: Base must be a number.")
    exit()  
    
  base_input = int(base_input)
  check_base_range(base_input)
  
  value1 = convert_to_base10(number1_input, base_input)
  value2 = convert_to_base10(number2_input, base_input)

  if value1 is None or value2 is None:
    print("Invalid input.")
    exit()
    
  if operation == "+":
    result = value1 + value2
  elif operation == "-":
    result = value1 - value2
  elif operation == "x":
    result = value1 * value2
  elif operation == "/":
    result = value1 / value2

  final_result = convert_from_base10(result, base_input)
  print(" ")
  print(number1_input + " " + operation + " " + number2_input)
  print(" ")
  print("= " + str(final_result))
  
#----------------------------
# SQUARE ROOT  
#----------------------------
elif operation == "√":
  number_input = input("Enter the number: ").strip().upper()
  base_input = input("Enter the base: ").strip()
  
  if not base_input.isdigit():
    print("Error: Base must be a number.")
    exit()
  base_input = int(base_input)
  
  check_base_range(base_input)
  
  value = convert_to_base10(number_input, base_input)
  
  if value is None:
    print("Invalid input.")
    exit()
  
  if value < 0:
    print("Error: Cannot take square root of a negative number.")
    exit()
  
  result = math.sqrt(value)
  final_result = convert_from_base10(result, base_input)
  
  print(" ")
  print("√" + number_input)
  print("= " + str(final_result))
#----------------------------  
#NTH ROOT
#----------------------------
elif operation == "n√":
  number_input = input("Enter the number: ").strip().upper()
  base_input = input("Enter the base: ").strip()
  n_input = input("Enter the root degree: ").strip()
  
  if not base_input.isdigit():
    print("Error: Base must be a number.")
    exit()
  base_input = int(base_input)
  check_base_range(base_input)
  
  value = convert_to_base10(number_input, base_input)
  
  if value is None:
    print("Invalid input.")
    exit()
    
  if n_input.isdigit():
    n = int(n_input)
    if n == 0:
        print("Error: Root degree cannot be zero.")
        exit()
  else:
    print("Invalid root degree.")
    exit()
  
  if value < 0:
    if n % 2 == 0:
      print("Error: Cannot take even root of a negative number.")
      exit()
      
  result = math.pow(value, 1/n)
  final_result = convert_from_base10(result, base_input)
  
  print(" ")
  print(str(n_input) + "√" + str(number_input))
  print("= " + str(final_result))
  
#----------------------------
# CONVERSIONS
#----------------------------
elif operation.lower() == "convert": 
  number_input = input("Enter the number you want to convert: ").strip().upper()
  base_input = input("Enter the base (2-36) of the number: ").strip()
  desired_base_input = input("Enter the base you want to convert to: ").strip()

  if not base_input.isdigit():
    print("Error: Base must be a number.")
    exit()
  if not desired_base_input.isdigit():
    print("Error: Desired base must be a number.")
    exit()  
    
  base_input = int(base_input)
  desired_base_input = int(desired_base_input)
  
  check_base_range(base_input)
  check_base_range(desired_base_input)
  
  base10_value = convert_to_base10(number_input, base_input)

  if base10_value is not None:
    final_value = convert_from_base10(base10_value, desired_base_input)
    
    print(" ")
    print("The base value " + str(desired_base_input) + " is " + str(final_value))
#----------------------------
# INVALID
#----------------------------
else:
  print("Invalid input")
  