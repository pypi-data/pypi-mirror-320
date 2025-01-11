import logging
import httpx

from gyvatukas.exceptions import GyvatukasException

_logger = logging.getLogger("gyvatukas")


class GithubCom:
    """
    🚨 Consider passing your api token, otherwise you will be rate limited to 60 requests per hour.
    See: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#about-primary-rate-limits

    Uses versioned ratio'd GitHub api.
    See: https://docs.github.com/en/rest?apiVersion=2022-11-28
    """

    RATE_LIMIT_PER_SECOND_UNAUTHENTICATED = 60 / 3600  # 60 requests per hour.
    RATE_LIMIT_PER_SECOND_AUTH = 5000 / 3600  # 5000 requests per hour.

    GITHUB_API_VERSION = "2022-11-28"  # Latest as of 2024-01.
    URL_API_MARKDOWN_CONVERT = "https://api.github.com/markdown"

    def __init__(self, api_token: str = None):
        self.api_token = api_token

    @staticmethod
    def _get_api_version_header() -> dict:
        """GitHub wants us to send api version. We comply.

        See: https://docs.github.com/en/rest/about-the-rest-api/api-versions?apiVersion=2022-11-28
        """
        return {
            "X-GitHub-Api-Version": GithubCom.GITHUB_API_VERSION,
        }

    def _get_api_auth_header(self) -> dict:
        """Return auth header for GitHub API if api_token is set."""
        if self.api_token:
            return {
                "Authorization": f"Bearer {self.api_token}",
            }
        return {}

    def convert_md_to_html(self, text: str, fancy_gfm_mode: bool = False) -> str:
        """Convert markdown to HTML using Github API.
        Extremely inefficient, but hey, no need to install markdown parsing library and internet is already
        mostly bot traffic anyway.

        See: https://docs.github.com/en/rest/reference/markdown
        """
        response = httpx.post(
            url=self.URL_API_MARKDOWN_CONVERT,
            json={
                "mode": "gfm" if fancy_gfm_mode else "markdown",
                "text": text,
            },
            headers={
                "Accept": "application/vnd.github+json",
                **self._get_api_version_header(),
                **self._get_api_auth_header(),
            },
            timeout=15,
        )
        if response.status_code == 200:
            return response.text

        _logger.error(
            "Failed to convert markdown to HTML!",
            extra={
                "text": text,
                "fancy_gfm_mode": fancy_gfm_mode,
                "response_status_code": response.status_code,
                "response_text": response.text,
            },
        )
        raise GyvatukasException("Failed to convert markdown to HTML!")


if __name__ == "__main__":
    gh = GithubCom()
    print(gh.convert_md_to_html("# Hello, world!"))

# todo: Different clients Auth and NoAuth since Auth has more available Apis and different allowances.
