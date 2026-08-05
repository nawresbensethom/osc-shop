import unittest

from config import BaseConfig
from services.auth_flow_demo import build_flow_status
from services.oidc_service import has_required_group, normalize_groups


class OIDCServiceTests(unittest.TestCase):
    def test_normalize_groups_handles_strings_and_lists(self) -> None:
        self.assertEqual(normalize_groups("app-users"), ["app-users"])
        self.assertEqual(normalize_groups(["app-users", "admins"]), ["app-users", "admins"])
        self.assertEqual(normalize_groups(None), [])

    def test_has_required_group_matches_expected_groups(self) -> None:
        self.assertTrue(has_required_group(["app-users", "admins"], {"app-users"}))
        self.assertFalse(has_required_group(["users"], {"app-users"}))

    def test_oidc_disabled_by_default(self) -> None:
        self.assertFalse(BaseConfig.OIDC_ENABLED)

    def test_build_flow_status_does_not_require_groups_when_unset(self) -> None:
        status = build_flow_status(
            {"OIDC_ENABLED": True, "OIDC_METADATA_URL": "http://example.invalid", "OIDC_REQUIRED_GROUPS": ""},
            {"oidc_claims": {"sub": "alice"}, "oidc_groups": []},
            authenticated=True,
        )
        self.assertEqual(status["required_groups"], [])


if __name__ == "__main__":
    unittest.main()
