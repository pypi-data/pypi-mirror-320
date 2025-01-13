#!/usr/bin/env python3

import sys
import random
import re
import argparse

def roll_dice(dice_expression):
    """
    Roll dice based on the given dice expression (e.g., '2d6+3').

    Parameters:
        dice_expression (str): The dice expression to parse and roll.

    Returns:
        tuple: A list of rolls and the total (rolls, total).
    """
    match = re.match(r'(\d*)d(\d+)([+-]?\d*)', dice_expression)
    if not match:
        print(f"Invalid dice format: {dice_expression}")
        return None, None

    # Parse dice components
    num_dice = int(match.group(1)) if match.group(1) else 1
    dice_sides = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0

    # Roll the dice
    rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
    total = sum(rolls) + modifier

    return rolls, total

def roll_with_advantage_or_disadvantage(dice_expression, advantage):
    """
    Roll dice with advantage or disadvantage.

    Parameters:
        dice_expression (str): The dice expression to roll.
        advantage (bool): True for advantage, False for disadvantage.

    Returns:
        tuple: Two rolls and the selected final roll (roll1, roll2, final).
    """
    rolls1, total1 = roll_dice(dice_expression)
    rolls2, total2 = roll_dice(dice_expression)

    if advantage:
        return (rolls1, total1), (rolls2, total2), max((rolls1, total1), (rolls2, total2), key=lambda x: x[1])
    else:
        return (rolls1, total1), (rolls2, total2), min((rolls1, total1), (rolls2, total2), key=lambda x: x[1])

def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Roll dice with optional advantage or disadvantage.")
    parser.add_argument("dice_expressions", nargs="*", help="Dice expressions in the format XdY+Z.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Enable quiet output.")
    parser.add_argument("-a", "--advantage", action="store_true", help="Roll with advantage.")
    parser.add_argument("-d", "--disadvantage", action="store_true", help="Roll with disadvantage.")

    return parser.parse_args()

def process_rolls(dice_expressions, verbose, advantage, disadvantage):
    """
    Process the dice rolls based on the provided options.

    Parameters:
        dice_expressions (list): List of dice expressions.
        verbose (bool): Whether to enable verbose output.
        advantage (bool): Roll with advantage.
        disadvantage (bool): Roll with disadvantage.

    Returns:
        int: The total sum of all rolls.
    """
    if advantage and disadvantage:
        raise ValueError("Cannot use both advantage and disadvantage at the same time.")

    total_sum = 0
    for dice_expression in dice_expressions:
        if advantage or disadvantage:
            roll1, roll2, final = roll_with_advantage_or_disadvantage(dice_expression, advantage)
            rolls, total = final
            if verbose:
                print(f"{dice_expression}: Roll 1 = {roll1[0]} (Total = {roll1[1]}), Roll 2 = {roll2[0]} (Total = {roll2[1]}), Final Total = {total}")
        else:
            rolls, total = roll_dice(dice_expression)
            if verbose:
                print(f"{dice_expression}: Rolls = {rolls}, Total = {total}")

        if rolls is not None:
            total_sum += total

    if verbose:
        print(f"Grand Total: {total_sum}")

    return total_sum

def main():
    """
    Main entry point for the script.
    """
    args = parse_arguments()
    try:
        total = process_rolls(args.dice_expressions, args.verbose, args.advantage, args.disadvantage)
        if not args.verbose:
            print(total)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

# Allow the script to be run as a standalone program or imported as a module
if __name__ == "__main__":
    main()
