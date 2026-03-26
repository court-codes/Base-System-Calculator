# Core logic for base-2–36 calculator (digits 0–9, A–Z).

import math

digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def check_inputs(number_input, base_input):
    if number_input.startswith("-"):
        number_input = number_input[1:]
    for char in number_input.replace(".", ""):
        if char not in digits[: int(base_input)]:
            return False
    return True


def validate_base(base_input):
    if base_input < 2 or base_input > 36:
        raise ValueError("Base must be between 2 and 36.")


def convert_to_base10(number_input, base_input):
    is_negative = False
    if number_input.startswith("-"):
        is_negative = True
        number_input = number_input[1:]
    if not check_inputs(number_input, base_input):
        return None
    if "." in number_input:
        whole, fraction = number_input.split(".")
    else:
        whole = number_input
        fraction = ""
    value = 0
    length_whole = len(whole)
    for x in range(length_whole):
        digit_value = digits.index(whole[x])
        power = length_whole - 1 - x
        value += digit_value * (int(base_input) ** power)
    length_fraction = len(fraction)
    for y in range(length_fraction):
        digit_value = digits.index(fraction[y])
        power = -(y + 1)
        value += digit_value * (int(base_input) ** power)
    return -value if is_negative else value


def convert_from_base10(value, desired_base_input):
    if value == 0:
        return "0"
    is_negative = False
    if value < 0:
        is_negative = True
        value = -value
    whole_part = int(value)
    fraction_part = value - whole_part
    whole_result = ""
    while whole_part > 0:
        remainder = whole_part % int(desired_base_input)
        whole_result = digits[remainder] + whole_result
        whole_part //= int(desired_base_input)
    fraction_result = ""
    count = 0
    place_value = 15
    while fraction_part > 0 and count < place_value:
        fraction_part *= int(desired_base_input)
        digit = int(fraction_part)
        fraction_result += digits[digit]
        fraction_part -= digit
        count += 1
    if fraction_result:
        result = whole_result + "." + fraction_result
    else:
        result = whole_result
    if is_negative:
        result = "-" + result
    return result


def _parse_base(s, field_name="base"):
    if not str(s).isdigit():
        raise ValueError(f"{field_name} must be a whole number.")
    return int(s)


def api_calculate(payload):
    """
    payload: dict with 'operation' and fields.
    Returns {"ok": True, "result": str, "expression": str} or {"ok": False, "error": str}.
    """
    op = (payload.get("operation") or "").strip().lower()
    try:
        if op == "convert":
            number_input = (payload.get("number") or "").strip().upper()
            base_input = _parse_base(payload.get("fromBase"), "Starting base")
            desired_base = _parse_base(payload.get("toBase"), "Target base")
            validate_base(base_input)
            validate_base(desired_base)
            base10_value = convert_to_base10(number_input, base_input)
            if base10_value is None:
                return {"ok": False, "error": "Invalid digits for the starting base."}
            final_value = convert_from_base10(base10_value, desired_base)
            return {
                "ok": True,
                "result": final_value,
                "expression": f"{number_input} (base {base_input}) → base {desired_base}",
            }

        if op in ("add", "subtract", "multiply", "divide"):
            n1 = (payload.get("num1") or "").strip().upper()
            n2 = (payload.get("num2") or "").strip().upper()
            base_input = _parse_base(payload.get("base"), "Base")
            validate_base(base_input)
            v1 = convert_to_base10(n1, base_input)
            v2 = convert_to_base10(n2, base_input)
            if v1 is None or v2 is None:
                return {"ok": False, "error": "Invalid digits for this base."}
            sym = {"add": "+", "subtract": "−", "multiply": "×", "divide": "÷"}[op]
            if op == "add":
                result = v1 + v2
            elif op == "subtract":
                result = v1 - v2
            elif op == "multiply":
                result = v1 * v2
            else:
                if v2 == 0:
                    return {"ok": False, "error": "Division by zero."}
                result = v1 / v2
            final_result = convert_from_base10(result, base_input)
            return {
                "ok": True,
                "result": final_result,
                "expression": f"{n1} {sym} {n2} (base {base_input})",
            }

        if op == "sqrt":
            number_input = (payload.get("number") or "").strip().upper()
            base_input = _parse_base(payload.get("base"), "Base")
            validate_base(base_input)
            value = convert_to_base10(number_input, base_input)
            if value is None:
                return {"ok": False, "error": "Invalid digits for this base."}
            if value < 0:
                return {"ok": False, "error": "Cannot take square root of a negative number."}
            result = math.sqrt(value)
            final_result = convert_from_base10(result, base_input)
            return {
                "ok": True,
                "result": final_result,
                "expression": f"√{number_input} (base {base_input})",
            }

        if op == "nthroot":
            number_input = (payload.get("number") or "").strip().upper()
            base_input = _parse_base(payload.get("base"), "Base")
            n_raw = (payload.get("n") or "").strip()
            validate_base(base_input)
            if not n_raw.isdigit():
                return {"ok": False, "error": "Root degree must be a non-negative whole number."}
            n = int(n_raw)
            if n == 0:
                return {"ok": False, "error": "Root degree cannot be zero."}
            value = convert_to_base10(number_input, base_input)
            if value is None:
                return {"ok": False, "error": "Invalid digits for this base."}
            if value < 0 and n % 2 == 0:
                return {"ok": False, "error": "Cannot take an even root of a negative number."}
            result = math.pow(value, 1 / n)
            final_result = convert_from_base10(result, base_input)
            return {
                "ok": True,
                "result": final_result,
                "expression": f"{n}√{number_input} (base {base_input})",
            }

        return {"ok": False, "error": "Unknown operation."}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def run_cli():
    print(" ")
    print("BASE SYSTEM CALCULATOR")
    print(" ")
    print("Options: ")
    print("")
    print("+ -  x  /  √  n√ convert")
    print(" ")
    operation = input("Enter an operation: ").strip()
    try:
        _run_cli_operation(operation)
    except ValueError as e:
        print(str(e))


def _run_cli_operation(operation):
    if operation in ("+", "-", "x", "/"):
        number1_input = input("Enter the first number: ").strip().upper()
        number2_input = input("Enter the second number: ").strip().upper()
        base_input = input("Enter the base: ").strip()
        if not base_input.isdigit():
            print("Error: Base must be a number.")
            return
        base_input = int(base_input)
        validate_base(base_input)
        value1 = convert_to_base10(number1_input, base_input)
        value2 = convert_to_base10(number2_input, base_input)
        if value1 is None or value2 is None:
            print("Invalid input.")
            return
        if operation == "+":
            result = value1 + value2
        elif operation == "-":
            result = value1 - value2
        elif operation == "x":
            result = value1 * value2
        else:
            if value2 == 0:
                print("Error: Division by zero.")
                return
            result = value1 / value2
        final_result = convert_from_base10(result, base_input)
        print(" ")
        print(number1_input + " " + operation + " " + number2_input)
        print(" ")
        print("= " + str(final_result))
    elif operation == "√":
        number_input = input("Enter the number: ").strip().upper()
        base_input = input("Enter the base: ").strip()
        if not base_input.isdigit():
            print("Error: Base must be a number.")
            return
        base_input = int(base_input)
        validate_base(base_input)
        value = convert_to_base10(number_input, base_input)
        if value is None:
            print("Invalid input.")
            return
        if value < 0:
            print("Error: Cannot take square root of a negative number.")
            return
        result = math.sqrt(value)
        final_result = convert_from_base10(result, base_input)
        print(" ")
        print("√" + number_input)
        print("= " + str(final_result))
    elif operation == "n√":
        number_input = input("Enter the number: ").strip().upper()
        base_input = input("Enter the base: ").strip()
        n_input = input("Enter the root degree: ").strip()
        if not base_input.isdigit():
            print("Error: Base must be a number.")
            return
        base_input = int(base_input)
        validate_base(base_input)
        value = convert_to_base10(number_input, base_input)
        if value is None:
            print("Invalid input.")
            return
        if n_input.isdigit():
            n = int(n_input)
            if n == 0:
                print("Error: Root degree cannot be zero.")
                return
        else:
            print("Invalid root degree.")
            return
        if value < 0:
            if n % 2 == 0:
                print("Error: Cannot take even root of a negative number.")
                return
        result = math.pow(value, 1 / n)
        final_result = convert_from_base10(result, base_input)
        print(" ")
        print(str(n_input) + "√" + str(number_input))
        print("= " + str(final_result))
    elif operation.lower() == "convert":
        number_input = input("Enter the number you want to convert: ").strip().upper()
        base_input = input("Enter the base (2-36) of the number: ").strip()
        desired_base_input = input("Enter the base you want to convert to: ").strip()
        if not base_input.isdigit():
            print("Error: Base must be a number.")
            return
        if not desired_base_input.isdigit():
            print("Error: Desired base must be a number.")
            return
        base_input = int(base_input)
        desired_base_input = int(desired_base_input)
        validate_base(base_input)
        validate_base(desired_base_input)
        base10_value = convert_to_base10(number_input, base_input)
        if base10_value is not None:
            final_value = convert_from_base10(base10_value, desired_base_input)
            print(" ")
            print("The base value " + str(desired_base_input) + " is " + str(final_value))
    else:
        print("Invalid input")

