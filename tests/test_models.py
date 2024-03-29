# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

logger = logging.getLogger("flask.app")

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_product(self):
        "it should read a product"
        product = ProductFactory()
        logger.debug(product)
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        product_from_db = Product.find(product.id)
        self.assertEqual(product_from_db.name, product.name)
        self.assertEqual(product_from_db.description, product.description)
        self.assertEqual(Decimal(product_from_db.price), product.price)
        self.assertEqual(product_from_db.available, product.available)
        self.assertEqual(product_from_db.category, product.category)

    def test_desirialize_invalid_product(self):
        "it should deserialiwe a invalid product"
        product = ProductFactory()
        logger.debug(product)
        product.id = None
        product.available = "beh"
        data = {}
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_update_product(self):
        "it should update a product"
        product = ProductFactory()
        logger.debug(product)
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        self.assertEqual(len(Product.all()), 1)
        product.description = "Just a simple description to test with hola"
        product.update()
        product_from_db = Product.find(product.id)
        self.assertEqual(product_from_db.id, product.id)
        self.assertEqual(product_from_db.description, product.description)

    def test_update_product_with_empty_id(self):
        "it should update a product with empty id"
        product = ProductFactory()
        logger.debug(product)
        product.id = None
        with self.assertRaises(DataValidationError):
            product.update()

    def test_delete_product(self):
        "it should delete a product"
        product = ProductFactory()
        logger.debug(product)
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_all_products(self):
        "it should retreive all product"
        self.assertEqual(len(Product.all()), 0)
        for i in range(5):
            logger.debug(i)
            product = ProductFactory()
            logger.debug(product)
            product.id = None
            product.create()
        self.assertEqual(len(Product.all()), 5)

    def test_find_product_by_name(self):
        "it should find a product by name"
        self.assertEqual(len(Product.all()), 0)
        products = []
        for i in range(5):
            logger.debug(i)
            product = ProductFactory()
            product.create()
            products.append(product)
        first_product_name = products[0].name
        name_occurences = len([product for product in products if product.name == first_product_name])
        found = Product.find_by_name(first_product_name)
        name_occurences_in_db = found.count()
        self.assertEqual(name_occurences_in_db, name_occurences)
        for product in found:
            self.assertEqual(product.name, first_product_name)

    def test_find_product_by_availability(self):
        "it should find a product by name"
        self.assertEqual(len(Product.all()), 0)
        products = []
        for i in range(10):
            logger.debug(i)
            product = ProductFactory()
            product.create()
            products.append(product)
        first_product_avl = products[0].available
        avl_occurences = len([product for product in products if product.available == first_product_avl])
        found = Product.find_by_availability(first_product_avl)
        avl_occurences_in_db = found.count()
        self.assertEqual(avl_occurences_in_db, avl_occurences)
        for product in found:
            self.assertEqual(product.available, first_product_avl)

    def test_find_product_by_category(self):
        "it should find a product by category"
        self.assertEqual(len(Product.all()), 0)
        products = []
        for i in range(10):
            logger.debug(i)
            product = ProductFactory()
            product.create()
            products.append(product)
        first_product_cat = products[0].category
        cat_occurences = len([product for product in products if product.category == first_product_cat])
        found = Product.find_by_category(first_product_cat)
        cat_occurences_in_db = found.count()
        self.assertEqual(cat_occurences_in_db, cat_occurences)
        for product in found:
            self.assertEqual(product.category, first_product_cat)

    def test_find_product_by_price(self):
        "it should find a product by price"
        self.assertEqual(len(Product.all()), 0)
        products = []
        for i in range(10):
            logger.debug(i)
            product = ProductFactory()
            product.create()
            products.append(product)
        first_product_price = products[0].price
        occurences = len([product for product in products if product.price == first_product_price])
        found = Product.find_by_price(first_product_price)
        self.assertEqual(found.count(), occurences)
