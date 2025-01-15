from rest_framework.test import APITestCase, APIClient
from unittest import mock
from django.contrib.auth.models import User
from identity_client.views import _get_public_identity_host
from django.contrib import auth
from django.contrib.sessions.models import Session


class TestLogin(APITestCase):
    @mock.patch("identity_client.views.requests.post")
    def test_returns_redirect_url_to_state(self, requests_post_mock):
        mock_token_reply = mock.MagicMock()
        mock_token_reply.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
        }
        mock_introspect_reply = mock.MagicMock()
        mock_introspect_reply.json.return_value = {"username": "test@me.com"}
        requests_post_mock.side_effect = [mock_token_reply, mock_introspect_reply]
        response = self.client.get(
            "/auth/login/?code=testCode&state=https://example.com"
        )
        self.assertRedirects(
            response,
            "https://example.com",
            status_code=302,
            fetch_redirect_response=False,
        )

    @mock.patch("identity_client.views.requests.post")
    def test_creates_users_if_it_doesnt_exist(self, requests_post_mock):
        mock_token_reply = mock.MagicMock()
        mock_token_reply.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
        }
        mock_introspect_reply = mock.MagicMock()
        mock_introspect_reply.json.return_value = {"username": "test@me.com"}
        requests_post_mock.side_effect = [mock_token_reply, mock_introspect_reply]
        response = self.client.get(
            "/auth/login/?code=testCode&state=https://example.com"
        )
        user = User.objects.get(email="test@me.com")
        self.assertIsNotNone(user)


class TestLogout(APITestCase):
    @mock.patch("identity_client.views._get_public_identity_host")
    def test_redirects_to_identity_logout(self, mock_get_pub_domain):
        mock_get_pub_domain.return_value = "https://id.stitchdesignlab.com"
        response = self.client.get(
            "/auth/logout/?code=testCode&state=https://example.com"
        )
        self.assertRedirects(
            response,
            "https://id.stitchdesignlab.com/auth/logout/?state=https://example.com",
            status_code=302,
            fetch_redirect_response=False,
        )

    def test_get_identity_public_domain(self):
        mock_request = mock.MagicMock()
        mock_request.get_host.return_value = (
            "https://stage-api.staging.stitchdesinglab.com"
        )
        self.assertEqual(
            _get_public_identity_host(mock_request),
            "https://id.staging.stitchdesinglab.com",
        )


class TestClearSession(APITestCase):
    @mock.patch("identity_client.views.requests.post")
    def test_clears_active_session(self, requests_post_mock):
        # simulate login
        mock_token_reply = mock.MagicMock()
        mock_token_reply.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
        }
        mock_introspect_reply = mock.MagicMock()
        mock_introspect_reply.json.return_value = {"username": "test@test.com"}
        requests_post_mock.side_effect = [mock_token_reply, mock_introspect_reply]
        response = self.client.get(
            "/auth/login/?code=testCode&state=https://example.com"
        )
        self.assertEqual(response.status_code, 302)
        sessions = Session.objects.all()
        self.assertEqual(len(sessions), 1)
        print(sessions[0].get_decoded())

        other_client = APIClient()
        flush_response = other_client.post(
            "/internal/sessions/flush/", data={"email": "test@test.com"},
        )
        self.assertEqual(flush_response.status_code, 200)
        sessions = Session.objects.all()
        self.assertEqual(len(sessions), 0)
