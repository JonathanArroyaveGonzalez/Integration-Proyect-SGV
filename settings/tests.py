from unittest import TestCase
from unittest.mock import MagicMock, patch, Mock
from settings.models.transprensa import TransprensaModel


class TransprensaModelTestCase(TestCase):
    def setUp(self):
        # Mock Config class before creating TransprensaModel instance
        self.mock_config_patcher = patch("settings.models.transprensa.Config")
        self.mock_config_class = self.mock_config_patcher.start()

        # Create a mock instance of Config
        self.mock_config_instance = Mock()
        self.mock_config_class.return_value = self.mock_config_instance

        # Mock the MongoDB collection
        self.mock_collection = Mock()
        self.mock_config_instance.client = {
            "apiconfig": {"transprensa_test": self.mock_collection}
        }

        # Now create the model with mocked Config
        self.model = TransprensaModel()

        self.test_config = {
            "transprensa_config": {
                "usuario_login": "TEST_USER",
                "usuario_password": "TEST_PASS",
                "test_url": "https://test.url",
                "production_url": "https://prod.url",
                "token": "test_token",
                "cookie": "PHPSESSID=test1234",
                "test": "True",
            }
        }

        # Mock the collection methods
        self.mock_collection.find_one = MagicMock(return_value=self.test_config)
        self.mock_collection.update_one = MagicMock(return_value=Mock(modified_count=1))
        self.mock_collection.replace_one = MagicMock(
            return_value=Mock(modified_count=1, upserted_id=None)
        )

    def tearDown(self):
        # Stop the patcher to restore the original Config class
        self.mock_config_patcher.stop()

    def test_get_config(self):
        config = self.model.get_config()
        self.assertIsInstance(config, dict)
        self.assertIn("transprensa_config", config)
        self.assertIn("base_url", config["transprensa_config"])
        # Verify that test_url and production_url were replaced with base_url
        self.assertNotIn("test_url", config["transprensa_config"])
        self.assertNotIn("production_url", config["transprensa_config"])

    def test_get_field(self):
        # Setup mock to return a document with the field
        self.mock_collection.find_one = MagicMock(
            return_value={"transprensa_config": {"usuario_login": "TEST_USER"}}
        )
        value = self.model.get_field("transprensa_config.usuario_login")
        self.assertIsInstance(value, str)
        self.assertEqual(value, "TEST_USER")

    def test_update_field(self):
        result = self.model.update_field(
            "transprensa_config.token", "nuevo_token_ABC123"
        )
        self.assertTrue(result)
        # Verify update_one was called with correct parameters
        self.mock_collection.update_one.assert_called_once_with(
            {}, {"$set": {"transprensa_config.token": "nuevo_token_ABC123"}}
        )

    def test_update_config(self):
        nuevo_config = {
            "transprensa_config": {
                "usuario_login": "WSOSAKA",
                "usuario_password": "NEW_PASS",
                "test_url": "https://nuevo.test.url",
                "production_url": "https://nuevo.prod.url",
                "token": "nuevo_token",
                "cookie": "PHPSESSID=abcd1234",
                "test": "True",
            }
        }
        result = self.model.update_config(nuevo_config)
        self.assertTrue(result)
        # Verify replace_one was called with correct parameters
        self.mock_collection.replace_one.assert_called_once_with(
            {}, nuevo_config, upsert=True
        )


if __name__ == "__main__":
    import unittest

    unittest.main()
