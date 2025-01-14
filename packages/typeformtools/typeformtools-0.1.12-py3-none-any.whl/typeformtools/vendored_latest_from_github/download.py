"""Utility script to download typing_extensions from GitHub and store it here - Olaf, 13 Jan 2025."""

import pathlib

import requests

__all__ = ['download_typing_extensions_from_github']


def download_typing_extensions_from_github() -> None:
    account = 'python'
    repository = 'typing_extensions'
    branch = 'main'
    module = 'typing_extensions'
    filename = f'{module}.py'

    def download() -> str:
        url = f'https://raw.githubusercontent.com/{account}/{repository}/refs/heads/{branch}/src/{filename}'
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def save(content: str) -> None:
        path = pathlib.Path(__file__).parent / filename
        if path.exists():
            raise FileExistsError(path)
        path.write_text(content, encoding='utf-8')

    save(download())


if __name__ == '__main__':
    download_typing_extensions_from_github()
