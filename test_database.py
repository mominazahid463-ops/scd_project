import unittest
import os
import database
from datetime import datetime

class TestDatabase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Change the database name to a test database so we don't overwrite production data
        database.DB_NAME = 'test_finance_tk.db'

    def setUp(self):
        # Before each test, ensure we start with a clean test database
        if os.path.exists(database.DB_NAME):
            os.remove(database.DB_NAME)
        database.init_db()

    def tearDown(self):
        # Clean up the test database after each test
        if os.path.exists(database.DB_NAME):
            os.remove(database.DB_NAME)

    def test_init_db_creates_default_categories(self):
        categories = database.get_all_categories()
        self.assertTrue(len(categories) > 0, "Default categories should be created on init.")
        
        # Check if 'Food' is one of the default categories
        food_cat = next((cat for cat in categories if cat['name'] == 'Food'), None)
        self.assertIsNotNone(food_cat)
        self.assertEqual(food_cat['type'], 'expense')
        self.assertEqual(food_cat['is_default'], 1)

    def test_add_and_get_category(self):
        initial_count = len(database.get_all_categories())
        
        database.add_category(name='Test Income', type_='income', budget_limit=None)
        
        categories = database.get_all_categories()
        self.assertEqual(len(categories), initial_count + 1)
        
        test_cat = next((cat for cat in categories if cat['name'] == 'Test Income'), None)
        self.assertIsNotNone(test_cat)
        self.assertEqual(test_cat['type'], 'income')
        self.assertEqual(test_cat['is_default'], 0)
        self.assertIsNone(test_cat['budget_limit'])

    def test_delete_category(self):
        database.add_category(name='To Delete', type_='expense')
        categories = database.get_all_categories()
        cat_to_delete = next(cat for cat in categories if cat['name'] == 'To Delete')
        
        database.delete_category(cat_to_delete['id'])
        
        categories_after = database.get_all_categories()
        deleted_cat = next((cat for cat in categories_after if cat['name'] == 'To Delete'), None)
        self.assertIsNone(deleted_cat)

    def test_add_and_get_transaction(self):
        # We need a category ID first
        categories = database.get_all_categories()
        food_cat_id = next(cat['id'] for cat in categories if cat['name'] == 'Food')
        
        date_str = datetime.today().strftime('%Y-%m-%d')
        database.add_transaction(amount=50.5, date=date_str, type_='expense', category_id=food_cat_id, note='Lunch')
        
        transactions = database.get_all_transactions()
        self.assertEqual(len(transactions), 1)
        
        tx = transactions[0]
        self.assertEqual(tx['amount'], 50.5)
        self.assertEqual(tx['date'], date_str)
        self.assertEqual(tx['type'], 'expense')
        self.assertEqual(tx['category'], 'Food')
        self.assertEqual(tx['note'], 'Lunch')

    def test_update_transaction(self):
        categories = database.get_all_categories()
        food_cat_id = next(cat['id'] for cat in categories if cat['name'] == 'Food')
        
        date_str = datetime.today().strftime('%Y-%m-%d')
        database.add_transaction(amount=20.0, date=date_str, type_='expense', category_id=food_cat_id, note='Snack')
        
        transactions = database.get_all_transactions()
        tx_id = transactions[0]['id']
        
        database.update_transaction(tx_id, amount=30.0, date=date_str, type_='expense', category_id=food_cat_id, note='Large Snack')
        
        updated_transactions = database.get_all_transactions()
        updated_tx = updated_transactions[0]
        self.assertEqual(updated_tx['amount'], 30.0)
        self.assertEqual(updated_tx['note'], 'Large Snack')

    def test_delete_transaction(self):
        categories = database.get_all_categories()
        food_cat_id = next(cat['id'] for cat in categories if cat['name'] == 'Food')
        
        date_str = datetime.today().strftime('%Y-%m-%d')
        database.add_transaction(amount=15.0, date=date_str, type_='expense', category_id=food_cat_id, note='Coffee')
        
        transactions = database.get_all_transactions()
        self.assertEqual(len(transactions), 1)
        
        database.delete_transaction(transactions[0]['id'])
        
        transactions_after = database.get_all_transactions()
        self.assertEqual(len(transactions_after), 0)

    def test_get_monthly_transactions(self):
        categories = database.get_all_categories()
        food_cat_id = next(cat['id'] for cat in categories if cat['name'] == 'Food')
        
        database.add_transaction(amount=100.0, date='2026-05-15', type_='expense', category_id=food_cat_id, note='May Groceries')
        database.add_transaction(amount=200.0, date='2026-06-02', type_='expense', category_id=food_cat_id, note='June Groceries')
        
        may_txs = database.get_monthly_transactions(2026, 5)
        self.assertEqual(len(may_txs), 1)
        self.assertEqual(may_txs[0]['amount'], 100.0)

        june_txs = database.get_monthly_transactions(2026, 6)
        self.assertEqual(len(june_txs), 1)
        self.assertEqual(june_txs[0]['amount'], 200.0)

if __name__ == '__main__':
    unittest.main()
