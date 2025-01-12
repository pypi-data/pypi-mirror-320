""" Ce script permet de calculer les impôts fédéraux et provinciaux pour un salaire annuel donné."""

import csv
import os
from datetime import datetime


def load_tax_brackets(filename: str, year: int, tax_type: str) -> list:
    """Loads the tax brackets for a given year and tax type from a CSV file.

    Args:
        filename (str): Path to the CSV file containing the tax brackets.
        year (int): Year to load the tax brackets for.
        tax_type (str): federal or provincial tax brackets to load.

    Returns:
        list: List of tax brackets for the given year and tax type.
    """
    brackets = []
    with open(filename, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row["annee"]) == year and row["type"] == tax_type:
                brackets.append(
                    (
                        float(row["tranche_min"]),
                        (
                            float("inf")
                            if row["tranche_max"] == "inf"
                            else float(row["tranche_max"])
                        ),
                        float(row["taux"]),
                    )
                )
    return brackets


def calculate_taxes(income: int, brackets: list) -> float:
    """Calculates the total taxes for a given income and tax brackets.

    Args:
        income (int): The yearly income to calculate the taxes for.
        brackets (list): The tax brackets to use for the calculation.

    Returns:
        float: The total taxes for the given income.
    """
    return sum(
        (min(income, upper) - lower) * rate
        for lower, upper, rate in brackets
        if income > lower
    )


def calculate_marginal_rate(income: int, brackets: list) -> float:
    """Calculates the marginal tax rate for a given income and tax brackets.

    Args:
        income (int): The income to calculate the marginal tax rate for.
        brackets (list): The tax brackets to use for the calculation.

    Returns:
        float: The marginal tax rate for the given income.
    """
    return next(
        (rate for lower, upper, rate in brackets if lower < income <= upper),
        0,
    )


def get_tax_rate(salaire_annuel: float, annee: int = datetime.now().year) -> dict:
    """Calculates the federal and provincial taxes rates for a given yearly income.

    Args:
        salaire_annuel (float): The yearly income to calculate the taxes for.
        annee (int, optional): The year to calculate the taxes for. Defaults to the current year.

    Returns:
        dict: A dictionary containing the following:
            - taux_effectif_quebecois: The effective tax rate for Quebec.
            - taux_effectif_canadien: The effective tax rate for Canada.
            - taux_effectif_total: The total effective tax rate.
            - taux_marginal_quebecois: The marginal tax rate for Quebec.
            - taux_marginal_canadien: The marginal tax rate for Canada.
            - taux_marginal_total: The total marginal
    """
    if salaire_annuel < 0:
        raise ValueError("Le salaire doit être un nombre positif.")

    if 2023 > annee or annee > 2025:
        raise ValueError("L'année doit être comprise entre 2023 et 2025.")

    script_dir = os.path.dirname(__file__)

    federal_brackets = load_tax_brackets(
        f"{script_dir}/tax_brackets.csv", annee, "federal"
    )
    federal_tax = calculate_taxes(salaire_annuel, federal_brackets)
    federal_marginal_rate = calculate_marginal_rate(salaire_annuel, federal_brackets)

    provincial_brackets = load_tax_brackets(
        f"{script_dir}/tax_brackets.csv", annee, "provincial"
    )
    provincial_tax = calculate_taxes(salaire_annuel, provincial_brackets)
    provincial_marginal_rate = calculate_marginal_rate(
        salaire_annuel, provincial_brackets
    )

    total_tax = federal_tax + provincial_tax
    total_effective_rate = 0 if salaire_annuel == 0 else (total_tax / salaire_annuel)
    total_marginal_rate = federal_marginal_rate + provincial_marginal_rate

    return {
        "taux_effectif_quebecois": (
            0
            if salaire_annuel == 0
            else float(f"{provincial_tax / salaire_annuel:.4f}")
        ),
        "taux_effectif_canadien": (
            0 if salaire_annuel == 0 else float(f"{federal_tax / salaire_annuel:.4f}")
        ),
        "taux_effectif_total": float(f"{total_effective_rate:.4f}"),
        "taux_marginal_quebecois": provincial_marginal_rate,
        "taux_marginal_canadien": federal_marginal_rate,
        "taux_marginal_total": total_marginal_rate,
    }


def get_capital_gain_tax_rate(gain_capital: float) -> dict:
    """Calculates the capital gain tax rate for a given capital gain.

    Args:
        gain_capital (float): The capital gain to calculate the tax rate for.

    Returns:
        dict: A dictionary containing the following:
            - taux_effectif: The effective tax rate for the capital gain.
            - taux_marginal: The marginal tax rate for the capital gain.
    """
    if gain_capital < 0:
        raise ValueError("Le gain en capital doit être un nombre positif.")

    brackets = [
        (float(0), float(250000), float(0.5)),
        (float(250000), float("inf"), float(0.667)),
    ]

    return {
        "taux_effectif": (
            0
            if gain_capital == 0
            else float(f"{calculate_taxes(gain_capital, brackets) / gain_capital:.4f}")
        ),
        "taux_marginal": float(
            f"{calculate_marginal_rate(gain_capital, brackets):.4f}"
        ),
    }
