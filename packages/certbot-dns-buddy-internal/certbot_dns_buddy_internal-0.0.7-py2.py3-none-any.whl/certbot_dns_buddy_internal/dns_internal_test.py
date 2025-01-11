"""Tests for certbot_dns_buddy.dns_buddy."""

import io
import logging
import sys
from unittest import mock

try:
    import certbot.compat.os as os
except ImportError:
    import os
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

FAKE_TOKEN = "XXXX"
FAKE_HOST = "https://foo.bar"
FAKE_MACHINE = "abc"
FAKE_WORKSPACE_ID = "123"
FAKE_TUNNEL_ID = "456"
FAKE_DOMAIN = "foo.bar"

class AuthenticatorTest(test_util.TempDirTestCase, dns_test_common.BaseAuthenticatorTest):
    """Class to test the Authenticator."""
    def setUp(self):
        super(AuthenticatorTest, self).setUp()

        self.config = mock.MagicMock()

        os.environ["BUDDY_TOKEN"] = FAKE_TOKEN
        os.environ["BUDDY_HOST"] = FAKE_HOST
        os.environ["BUDDY_MACHINE"] = FAKE_MACHINE
        os.environ["BUDDY_WORKSPACE_ID"] = FAKE_WORKSPACE_ID
        os.environ["BUDDY_TUNNEL_ID"] = FAKE_TUNNEL_ID
        os.environ["BUDDY_DOMAIN"] = FAKE_DOMAIN

        from certbot_dns_buddy_internal.dns_internal import Authenticator
        self.auth = Authenticator(self.config, "buddy")
        self.mock_client = mock.MagicMock(default_propagation_seconds=15)
        self.auth._api_client = mock.MagicMock(return_value=self.mock_client)

        try:
            from certbot.display.util import notify
            notify_patch = mock.patch('certbot._internal.main.display_util.notify')
            self.mock_notify = notify_patch.start()
            self.addCleanup(notify_patch.stop)
            self.old_stdout = sys.stdout
            sys.stdout = io.StringIO()
        except ImportError:
            self.old_stdout = sys.stdout

    def tearDown(self):
        sys.stdout = self.old_stdout

    def test_perform(self):
        """Tests the perform function to see if client method is called"""
        self.auth.perform([self.achall])
        expected = [
            mock.call.add_txt_record(DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY)
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)

    def test_cleanup(self):
        """Tests cleanup method to see if client method is called"""
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])
        expected = [
            mock.call.del_txt_record(DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY)
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)