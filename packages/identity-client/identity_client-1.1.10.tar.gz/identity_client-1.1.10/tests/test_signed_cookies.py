from unittest import TestCase
from unittest import mock

from identity_client.signed_cookies import get_domain_from_header
from identity_client.helpers import get_assets_v2_domain


class FetchKeysTestCase(TestCase):
    def test_gets_url_properly(self):
        self.assertEqual(get_domain_from_header('http://test.me.com'), '.me.com')

    def test_gets_url_properly_no_http(self):
        self.assertEqual(get_domain_from_header('test.me.com'), '.me.com')

    def test_get_assets_v2_url(self):
        request = mock.MagicMock()
        request.META = {
            'HTTP_HOST': 'boards.stitch.fashion',
        }
        self.assertEqual(get_assets_v2_domain(request), '*.stitch.fashion')
        request.META = {
            'HTTP_HOST': 'boards.stitchdesignlab.com',
        }
        self.assertEqual(get_assets_v2_domain(request), '*.stitchdesignlab.com')
