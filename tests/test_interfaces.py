import os
import unittest
from unittest.mock import patch

from app.interfaces import build_interfaces


class BuildInterfacesTestCase(unittest.TestCase):
    def test_returns_no_interfaces_when_whatsapp_is_disabled(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(build_interfaces(agent=object()), [])

    def test_raises_when_whatsapp_is_enabled_but_not_configured(self) -> None:
        with patch.dict(os.environ, {"WHATSAPP_ENABLED": "true"}, clear=True):
            with self.assertRaises(RuntimeError) as context:
                build_interfaces(agent=object())

        self.assertIn("WHATSAPP_ENABLED=true", str(context.exception))
        self.assertIn("WHATSAPP_ACCESS_TOKEN", str(context.exception))

    def test_builds_whatsapp_interface_when_enabled_and_configured(self) -> None:
        env = {
            "WHATSAPP_ENABLED": "true",
            "WHATSAPP_ACCESS_TOKEN": "token-value",
            "WHATSAPP_PHONE_NUMBER_ID": "phone-id",
            "WHATSAPP_VERIFY_TOKEN": "verify-token",
            "WHATSAPP_APP_SECRET": "app-secret",
        }
        with patch.dict(os.environ, env, clear=True):
            with patch("app.interfaces.Whatsapp", autospec=True) as whatsapp_cls:
                interfaces = build_interfaces(agent="knowledge-agent")

        whatsapp_cls.assert_called_once_with(
            agent="knowledge-agent",
            access_token="token-value",
            phone_number_id="phone-id",
            verify_token="verify-token",
        )
        self.assertEqual(interfaces, [whatsapp_cls.return_value])

    def test_allows_signature_validation_skip_without_app_secret(self) -> None:
        env = {
            "WHATSAPP_ENABLED": "true",
            "WHATSAPP_ACCESS_TOKEN": "token-value",
            "WHATSAPP_PHONE_NUMBER_ID": "phone-id",
            "WHATSAPP_VERIFY_TOKEN": "verify-token",
            "WHATSAPP_SKIP_SIGNATURE_VALIDATION": "true",
        }
        with patch.dict(os.environ, env, clear=True):
            with patch("app.interfaces.Whatsapp", autospec=True) as whatsapp_cls:
                interfaces = build_interfaces(agent="knowledge-agent")

        whatsapp_cls.assert_called_once()
        self.assertEqual(interfaces, [whatsapp_cls.return_value])


if __name__ == "__main__":
    unittest.main()
