import unittest
from unittest.mock import patch

from gistapi.api import app


class TestGistApi(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_ping(self):
        rv = self.client.get('/ping')
        self.assertEqual(rv.data, b'pong')

    @patch('gistapi.api.gists_for_user_generator')
    def test_search_empty_array(self, mock_gists_for_user_generator):
        mock_gists_for_user_generator.return_value = []

        rv = self.client.post('/api/v1/search', json={
            'username': 'test',
            'pattern': 'print'
        })
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['status'], 'success')
        self.assertEqual(rv.json['username'], 'test')
        self.assertEqual(rv.json['pattern'], 'print')
        self.assertEqual(rv.json['matches'], [])

    @patch('gistapi.api.gists_for_user_generator')
    @patch('gistapi.api.GistMatcher.get_matching_gists')
    def test_search(
        self,
        mock_get_matching_gists,
        mock_gists_for_user_generator
    ):
        mock_gists_for_user_generator.return_value = [[
            {
                'id': '1234',
                'description': 'test gist',
                'files': {
                    'test.py': {
                        'raw_url': 'raw_url',
                        'type': 'text/plain'
                    }
                }
            }
        ]]

        mock_get_matching_gists.return_value = mock_gists_for_user_generator\
            .return_value[0]

        rv = self.client.post('/api/v1/search', json={
            'username': 'test',
            'pattern': 'print'
        })
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['status'], 'success')
        self.assertEqual(rv.json['username'], 'test')
        self.assertEqual(rv.json['pattern'], 'print')
        self.assertEqual(
            rv.json['matches'],
            mock_gists_for_user_generator.return_value[0]
        )

    @patch('gistapi.api.gists_for_user_generator')
    @patch('gistapi.api.GistMatcher._load_file_content')
    def test_search_no_match(
        self,
        mock_load_file_content,
        mock_gists_for_user_generator
    ):
        mock_gists_for_user_generator.return_value = [[
            {
                'id': '1234',
                'description': 'test gist',
                'files': {
                    'test.py': {
                        'raw_url': 'raw_url',
                        'type': 'text/plain'
                    }
                }
            }
        ]]

        mock_load_file_content.return_value = 'return "hello world"'

        rv = self.client.post('/api/v1/search', json={
            'username': 'test',
            'pattern': 'print'
        })
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['status'], 'success')
        self.assertEqual(rv.json['username'], 'test')
        self.assertEqual(rv.json['pattern'], 'print')
        self.assertEqual(rv.json['matches'], [])

    def test_api_fails_on_wrong_body(self):
        rv = self.client.post('/api/v1/search', json={
            'username': 'test'
        })
        self.assertEqual(rv.status_code, 400)

        rv = self.client.post('/api/v1/search', json={
            'pattern': 'test'
        })
        self.assertEqual(rv.status_code, 400)
