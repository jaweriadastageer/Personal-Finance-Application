import os
import unittest
from finance_utils import (
    Transaction, Income, Expense, Investment,
    save_transaction, load_transactions,
    calculate_totals, get_insights, string_analysis,
    DATA_FILE
)

class TestFinanceCore(unittest.TestCase):
    def setUp(self):
        # Clean up existing data file for testing
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)

    def tearDown(self):
        # Clean up after tests
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)

    def test_save_and_load_transactions(self):
        t1 = Income("2023-10-01", 5000.0, "Salary", "Monthly salary")
        t2 = Expense("2023-10-05", 100.0, "Food", "Groceries")
        t3 = Investment("2023-10-10", 1000.0, "Stocks", "Tech stocks")

        save_transaction(t1)
        save_transaction(t2)
        save_transaction(t3)

        loaded = load_transactions()
        self.assertEqual(len(loaded), 3)
        self.assertIsInstance(loaded[0], Income)
        self.assertIsInstance(loaded[1], Expense)
        self.assertIsInstance(loaded[2], Investment)
        self.assertEqual(loaded[0].amount, 5000.0)

    def test_calculate_totals(self):
        transactions = [
            Income("2023-10-01", 5000.0, "Salary"),
            Expense("2023-10-05", 2000.0, "Rent"),
            Investment("2023-10-10", 1000.0, "Stocks")
        ]

        totals = calculate_totals(transactions)
        self.assertEqual(totals["Total Income"], 5000.0)
        self.assertEqual(totals["Total Expense"], 2000.0)
        self.assertEqual(totals["Total Investment"], 1000.0)
        self.assertEqual(totals["Net Balance"], 2000.0) # 5000 - 2000 - 1000
        self.assertEqual(totals["Savings Percentage"], 60.0) # (3000 / 5000) * 100 -> (Income - Expense) / Income

    def test_get_insights(self):
        transactions = [
            Expense("2023-10-01", 100.0, "Food"),
            Expense("2023-10-02", 50.0, "Transport"),
            Expense("2023-10-03", 200.0, "Food")
        ]

        insights = get_insights(transactions)
        self.assertEqual(insights["highest_spending_category"], "Food")
        self.assertEqual(insights["most_frequent_category"], "Food")
        self.assertEqual(len(insights["unique_categories"]), 2)

    def test_string_analysis(self):
        categories = ["Salary", "Food", "Stocks"]
        upper_str, count_a = string_analysis(categories)

        self.assertEqual(upper_str, "SALARY, FOOD, STOCKS")
        self.assertEqual(count_a, 2) # SALARY (2), FOOD (0), STOCKS (0) -> Total 2
        # "SALARY, FOOD, STOCKS" -> A appears in SALARY (2 times).

if __name__ == '__main__':
    unittest.main()