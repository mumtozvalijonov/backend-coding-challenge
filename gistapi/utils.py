import asyncio
import re
from typing import List
import aiohttp
import requests


def gists_for_user(username: str):
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    Args:
        username (string): the user to query gists for

    Returns:
        The dict parsed from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """
    gists_url = 'https://api.github.com/users/{username}/gists'\
        .format(username=username)
    response = requests.get(gists_url)
    return response.json()


class GistMatcher:
    """A class that can be used to match a pattern against a list of gists.

    Attributes:
        pattern (string): the pattern to match against
    """

    def __init__(self, loop: asyncio.AbstractEventLoop, pattern: str):
        """Initializes the GistMatcher class.

        Args:
            loop (asyncio.AbstractEventLoop): the event loop to use
            pattern (string): the pattern to match against
        """
        self._loop = loop
        self._pattern = pattern

    async def _match(self, gists: List[dict]) -> List[dict]:
        """Matches the pattern against a list of gists.

        Args:
            gists (List[dict]): the list of gists to match against

        Returns:
            List[dict]: the list of gists that match the pattern
        """

        # Create aiohttp session
        async with aiohttp.ClientSession(loop=self._loop) as session:
            # Create a list of futures
            tasks = []
            matching_gists = []
            for gist in gists:
                for file in gist['files'].values():
                    # Submit a task to the thread pool
                    # if the file is text based
                    if 'text' in file['type']:
                        tasks.append(
                            self._loop.create_task(
                                self._load_file_content(
                                    file['raw_url'],
                                    session
                                )
                            )
                        )

                # Gather the results
                results = await asyncio.gather(*tasks)

                # Check if the pattern is in the results with regex
                for result in results:
                    if re.search(self._pattern, result):
                        matching_gists.append(gist)
                        break

            return matching_gists

    async def _load_file_content(
        self,
        file_url: str,
        session: aiohttp.ClientSession
    ) -> str:
        """Loads the content of a file.

        Args:
            file_url (str): the URL of the file to load
            session (aiohttp.ClientSession): the session to use

        Returns:
            The content of the file.
        """
        async with session.get(file_url) as response:
            return await response.text()

    def get_matching_gists(self, gists: List[dict]) -> List[dict]:
        """Matches the pattern against a list of gists.

        Args:
            gists (list): a list of gists

        Returns:
            A list of gists that match the pattern.
        """
        return self._loop.run_until_complete(self._match(gists))
