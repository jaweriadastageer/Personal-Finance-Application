# finance_core.py
import csv
import os
from typing import List, Dict

DATA_FILE = "transactions.csv"

class Transaction:
    def __init__(self, date: str, amount: float, category: str, note: str = ""):
        self.date = date
        self.amount = float(amount)
        self.category = category
        self.note = note

    def to_dict(self) -> Dict:
        return {
            "Date": self.date,
            "Type": self.__class__.__name__,
            "Amount": self.amount,
            "Category": self.category,
            "Note": self.note
        }

class Income(Transaction): pass
class Expense(Transaction): pass
class Investment(Transaction): pass

def save_transaction(transaction: Transaction):
    """Append a transaction to CSV (creates file with header if missing)."""
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Type", "Amount", "Category", "Note"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(transaction.to_dict())

def load_transactions() -> List[Transaction]:
    txns: List[Transaction] = []
    if not os.path.isfile(DATA_FILE):
        return txns

    with open(DATA_FILE, mode="r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # Normalize fieldnames (strip whitespace)
        if reader.fieldnames:
            reader.fieldnames = [fn.strip() for fn in reader.fieldnames]

        for row in reader:
            if not row:
                continue
            t_type = row.get("Type", "").strip()
            date = row.get("Date", "").strip()
            amount_str = row.get("Amount", "0").strip()
            category = row.get("Category", "").strip()
            note = row.get("Note", "").strip()
            try:
                amount = float(amount_str)
            except (ValueError, TypeError):
                continue
            if t_type == "Income":
                txns.append(Income(date, amount, category, note))
            elif t_type == "Expense":
                txns.append(Expense(date, amount, category, note))
            elif t_type == "Investment":
                txns.append(Investment(date, amount, category, note))
    return txns

def calculate_totals(transactions: List[Transaction]) -> Dict[str, float]:
    totals = {
        "Total Income": 0.0,
        "Total Expense": 0.0,
        "Total Investment": 0.0,
        "Net Balance": 0.0
    }
    for t in transactions:
        if isinstance(t, Income):
            totals["Total Income"] += t.amount
        elif isinstance(t, Expense):
            totals["Total Expense"] += t.amount
        elif isinstance(t, Investment):
            totals["Total Investment"] += t.amount
    totals["Net Balance"] = totals["Total Income"] - totals["Total Expense"] - totals["Total Investment"]
    return totals

def get_insights(transactions: List[Transaction]) -> Dict:
    if not transactions:
        return {
            "unique_categories": set(),
            "category_totals": {},
            "highest_spending_category": "N/A",
            "most_frequent_category": "N/A"
        }

    categories = [t.category for t in transactions]
    unique_categories = set(categories)

    # category-wise totals (all types)
    cat_totals = {}
    for t in transactions:
        cat_totals[t.category] = cat_totals.get(t.category, 0.0) + t.amount

    # highest spending category (expenses only)
    expense_totals = {}
    for t in transactions:
        if isinstance(t, Expense):
            expense_totals[t.category] = expense_totals.get(t.category, 0.0) + t.amount
    highest_spending = max(expense_totals, key=expense_totals.get) if expense_totals else "N/A"

    # most frequent category (all transactions)
    most_freq = max(set(categories), key=categories.count) if categories else "N/A"

    return {
        "unique_categories": unique_categories,
        "category_totals": cat_totals,
        "highest_spending_category": highest_spending,
        "most_frequent_category": most_freq
    }

def string_analysis(categories: List[str]):
    if not categories:
        return "", 0
    joined = ", ".join(categories)
    upper = joined.upper()
    count_a = upper.count("A")
    return upper, count_a
