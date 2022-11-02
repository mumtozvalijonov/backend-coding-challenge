import asyncio
import unittest
from unittest.mock import patch

from gistapi.utils import GistMatcher, gists_for_user


class TestGistUtils(unittest.TestCase):

    @patch('requests.get')
    def test_get_gist(self, mock_get):

        expected_gist_list = [
            {
                'id': '1234',
                'description': 'test gist',
                'files': {
                    'test.py': {
                        'content': 'print("hello world")'
                    }
                }
            }
        ]
        mock_get.return_value.json.return_value = expected_gist_list

        gists = gists_for_user('test')
        mock_get.assert_called_with('https://api.github.com/users/test/gists')
        self.assertEqual(gists, expected_gist_list)

    @patch('gistapi.utils.GistMatcher._load_file_content')
    def test_get_matching_gists(self, mock_load_file_content):
        expected_gist_list = [
            {
                'id': '1234',
                'description': 'test gist',
                'files': {
                    'test.py': {
                        'type': 'text/plain',
                        'raw_url': 'raw_url'
                    }
                }
            }
        ]

        mock_load_file_content.return_value = 'print("hello world")'

        matcher = GistMatcher(asyncio.new_event_loop(), 'print')
        gists = matcher.get_matching_gists(expected_gist_list)
        self.assertEqual(gists, expected_gist_list)

    @patch('gistapi.utils.GistMatcher._load_file_content')
    def test_get_matching_gists_empty_list_on_missing_pattern(
        self,
        mock_load_file_content
    ):
        gist_list = [
            {
                'id': '1234',
                'description': 'test gist',
                'files': {
                    'test.py': {
                        'type': 'text/plain',
                        'raw_url': 'raw_url'
                    }
                }
            }
        ]

        mock_load_file_content.return_value = 'abcd'
        matcher = GistMatcher(asyncio.new_event_loop(), 'print')
        gists = matcher.get_matching_gists(gist_list)
        self.assertEqual(gists, [])

    def test_get_matching_gists_empty_list_on_nontext_files(self):
        gist_list = [
            {
                'id': '1234',
                'description': 'test gist',
                'files': {
                    'test.py': {
                        'type': 'image/png',
                        'raw_url': 'raw_url'
                    }
                }
            }
        ]

        matcher = GistMatcher(asyncio.new_event_loop(), 'print')
        gists = matcher.get_matching_gists(gist_list)
        self.assertEqual(gists, [])
