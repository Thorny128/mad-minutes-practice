import re
from fractions import Fraction
import random

def generate_coterminal_question(question, answer):
    """
    Takes a base angle question and generates a coterminal version.
    Adds/subtracts multiples of 2π (for radians) or 360º (for degrees).
    Range: -4π to 4π (or -720º to 720º)
    """

    # Check if it's a degree or radian question
    if 'º' in question:
        # Degrees question
        # Extract the function name and angle
        match = re.match(r'(\w+)\((-?\d+)º\)', question)
        if match:
            func_name = match.group(1)
            base_angle = int(match.group(2))

            # Choose a random multiple of 360 to add/subtract (-2, -1, 0, 1, 2)
            multiplier = random.choice([-2, -1, 0, 1, 2])
            coterminal_angle = base_angle + (multiplier * 360)

            # Only apply coterminal if multiplier is not 0
            if multiplier != 0:
                new_question = f"{func_name}({coterminal_angle}º)"
                return new_question, answer, multiplier
    else:
        # Radians question
        # Extract the function name and angle
        match = re.match(r'(\w+)\((.*?)\)', question)
        if match:
            func_name = match.group(1)
            angle_str = match.group(2)

            # Choose a random multiple of 2π to add/subtract (-2, -1, 0, 1, 2)
            multiplier = random.choice([-2, -1, 0, 1, 2])

            # Only apply coterminal if multiplier is not 0
            if multiplier != 0:
                # Parse the angle string to extract the fraction
                # Handle cases like "0", "π", "π/3", "5π/3", "-π/4", etc.

                if angle_str == "0":
                    # Special case: 0 + n*2π = n*2π
                    new_numerator = multiplier * 2
                    if new_numerator == 1:
                        new_question = f"{func_name}(π)"
                    elif new_numerator == -1:
                        new_question = f"{func_name}(-π)"
                    else:
                        new_question = f"{func_name}({new_numerator}π)"
                    return new_question, answer, multiplier

                # Parse angle like "π", "5π/3", "-π/4", etc.
                angle_match = re.match(r'(-?\d*)π(?:/(\d+))?', angle_str)
                if angle_match:
                    numerator_str = angle_match.group(1)
                    denominator_str = angle_match.group(2)

                    # Parse numerator (handle "", "-", and numbers)
                    if numerator_str == "" or numerator_str == "+":
                        numerator = 1
                    elif numerator_str == "-":
                        numerator = -1
                    else:
                        numerator = int(numerator_str)

                    # Parse denominator
                    denominator = int(denominator_str) if denominator_str else 1

                    # Create fractions and add
                    base_fraction = Fraction(numerator, denominator)
                    coterminal_add = Fraction(multiplier * 2, 1)
                    result_fraction = base_fraction + coterminal_add

                    # Format the result
                    if result_fraction.denominator == 1:
                        # Whole number
                        if result_fraction.numerator == 1:
                            new_question = f"{func_name}(π)"
                        elif result_fraction.numerator == -1:
                            new_question = f"{func_name}(-π)"
                        elif result_fraction.numerator == 0:
                            new_question = f"{func_name}(0)"
                        else:
                            new_question = f"{func_name}({result_fraction.numerator}π)"
                    else:
                        # Fraction
                        if result_fraction.numerator < 0:
                            new_question = f"{func_name}(-{abs(result_fraction.numerator)}π/{result_fraction.denominator})"
                        else:
                            new_question = f"{func_name}({result_fraction.numerator}π/{result_fraction.denominator})"

                    return new_question, answer, multiplier

    # If no modification was made, return original
    return question, answer, 0


# Test cases
test_cases = [
    ("sin(5π/3)", "√3/2"),
    ("cos(π/4)", "√2/2"),
    ("tan(π)", "0"),
    ("sin(0)", "0"),
    ("cos(60º)", "1/2"),
    ("sin(30º)", "1/2"),
    ("tan(-π/3)", "-√3"),
    ("csc(π/6)", "2"),
]

print("Testing coterminal angle generation:\n")
for original_q, answer in test_cases:
    # Set seed for reproducibility
    random.seed(42)
    new_q, new_answer, mult = generate_coterminal_question(original_q, answer)
    if mult != 0:
        print(f"{original_q:20} → {new_q:25} (mult={mult:2}, answer={new_answer})")
    else:
        print(f"{original_q:20} → (no change)")

    # Generate a few more examples
    for _ in range(3):
        new_q, new_answer, mult = generate_coterminal_question(original_q, answer)
        if mult != 0:
            print(f"{' '*20}   {new_q:25} (mult={mult:2}, answer={new_answer})")
    print()

