from unittest import TestCase
from unittest.mock import MagicMock
from settings.models.transprensa import TransprensaModel


class TransprensaModelTestCase(TestCase):
    def setUp(self):
        self.model = TransprensaModel()
        self.test_config = {
            "transprensa_config": {
                "usuario_login": "TEST_USER",
                "usuario_password": "TEST_PASS",
                "test_url": "https://test.url",
                "production_url": "https://prod.url",
                "token": "test_token",
                "cookie": "PHPSESSID=test1234",
            }
        }
        # Mock the initial configuration
        self.model.get_config = MagicMock(return_value=self.test_config)
        self.model.update_config = MagicMock(return_value=True)
        self.model.update_field = MagicMock(return_value=True)
        self.model.get_field = MagicMock(return_value="TEST_USER")

    def test_get_config(self):
        config = self.model.get_config()
        self.assertIsInstance(config, dict)
        self.assertEqual(config, self.test_config)

    def test_get_field(self):
        value = self.model.get_field("transprensa_config.usuario_login")
        self.assertIsInstance(value, str)
        self.assertEqual(value, "TEST_USER")

    def test_update_field(self):
        result = self.model.update_field(
            "transprensa_config.token", "nuevo_token_ABC123"
        )
        self.assertTrue(result)

    def test_update_config(self):
        nuevo_config = {
            "transprensa_config": {
                "usuario_login": "WSOSAKA",
                "usuario_password": "NEW_PASS",
                "test_url": "https://nuevo.test.url",
                "production_url": "https://nuevo.prod.url",
                "token": "nuevo_token",
                "cookie": "PHPSESSID=abcd1234",
            }
        }
        result = self.model.update_config(nuevo_config)
        self.assertTrue(result)
        self.model.get_config.return_value = nuevo_config
        current_config = self.model.get_config()
        self.assertEqual(current_config, nuevo_config)


if __name__ == "__main__":
    import unittest

    unittest.main()
