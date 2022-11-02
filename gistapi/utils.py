import asyncio
import re
from typing import Generator, List
import aiohttp
import requests


def gists_for_user_generator(username: str):
    """Generator that yields gists for a given user"""
    url = f"https://api.github.com/users/{username}/gists"
    per_page = 100
    page = 1
    while True:
        response = requests.get(
            url, params={"per_page": per_page, "page": page})
        if not response.ok or not response.json():
            break
        yield response.json()
        page += 1


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

    async def _match(
        self,
        gists_generator: Generator[dict, None, None],
        limit=100,
        offset=0
    ) -> List[dict]:
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
            matching_gists = {}
            for gist_batch in gists_generator:
                print(len(gist_batch))
                tasks_gists = []
                for gist in gist_batch:
                    for file in gist['files'].values():
                        # Submit a task to the event loop
                        tasks.append(
                            self._loop.create_task(
                                self._load_file_content(
                                    file['raw_url'],
                                    session
                                )
                            )
                        )
                        tasks_gists.append(gist)

                # Gather the results
                results = await asyncio.gather(*tasks)

                # Check if the pattern is in the results with regex
                for i, result in enumerate(results):
                    if re.search(self._pattern, result):
                        matching_gists[tasks_gists[i]['id']] = tasks_gists[i]

                    print(len(matching_gists), limit, offset)
                    if len(matching_gists) >= limit + offset:
                        return list(matching_gists.values())[
                            offset:offset+limit
                        ]

                # Reset the tasks list
                tasks = []

            return list(matching_gists.values())[offset:offset+limit]

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

    def get_matching_gists(
        self,
        gists: List[dict],
        limit=100,
        offset=0
    ) -> List[dict]:
        """Matches the pattern against a list of gists.

        Args:
            gists (list): a list of gists

        Returns:
            A list of gists that match the pattern.
        """
        return self._loop.run_until_complete(self._match(gists, limit, offset))
