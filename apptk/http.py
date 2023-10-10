from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Union

try:
    import requests
except ImportError:
    raise RuntimeError("Library `requests` is required to use `apptk.http`.")

try:
    import cloudscraper
except ImportError:
    cloudscraper = None

# This default headers are "hard-coded" and will always apply to Client instances. They've been defined at this
# top-level to indicate that there is no intention that they should be over-ridden
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0",
}


class HttpMethod(Enum):
    OPTIONS = "options"
    GET = "get"
    HEAD = "head"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    TRACE = "trace"
    CONNECT = "connect"
    PATCH = "patch"


class HttpClient:
    """
    A wrapper around requests.Session with app-specific additions.

    The point is to allow people to be able to use this as requests.Session with a few changes:

    1) Additional initialization that is specific to this app.

    2) Provide custom wrappers for handling things like failed requests so that we can apply the
       same handling across the entire app in a central location.
    """

    _headers: dict = None
    _session: requests.Session = None

    def __init__(self, headers: dict = None, use_cloudscraper: bool = False) -> None:
        if use_cloudscraper:
            if cloudscraper is None:
                raise RuntimeError("Option `use_cloudscraper` requires the `cloudscraper` library to be installed.")
            self._session = cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "linux", "mobile": False}, ecdhCurve="secp384r1"
            )
        else:
            self._session = requests.Session()

        self._session.headers.update(DEFAULT_HEADERS)
        self._session.headers.update(self._headers or {})
        self._session.headers.update(headers or {})

    def __getattr__(self, item):
        return getattr(self._session, item)

    def download_file(self, url: str, filename: Union[str, Path], method: Union[HttpMethod, str] = "get", **kwargs):
        kwargs["stream"] = True

        if isinstance(method, str):
            try:
                method = HttpMethod[method.upper()]
            except KeyError:
                raise ValueError(f"Not a valid HttpMethod: {method}")

        method_func = getattr(self._session, method.value)

        with method_func(url, **kwargs) as response:
            response.raise_for_status()

            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    f.write(chunk)

            return filename


def fix_cookie_jar_file(orig_cookiejarfile):
    """
    Strip #HttpOnly from cookies since MozillaCookieJar doesn't support it.

    This bug was fixed in 2020, but doesn't look like it's in Python 3.9.

    Source: https://github.com/python/cpython/issues/46443#issuecomment-1093410833
    """
    with NamedTemporaryFile(mode="w+", delete=False) as cookiejar_fh:
        with open(orig_cookiejarfile, "r") as orig_cookiejar_fh:
            for line in orig_cookiejar_fh:
                cookiejar_fh.write(line[10:] if line.startswith("#HttpOnly_") else line)
            cookiejar_fh.seek(0)
        yield cookiejar_fh.name
