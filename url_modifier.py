from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


class URLModifier:
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.query_params = parse_qs(self.parsed_url.query)

    def modify_param(self, key, value=None):
        self.query_params[key] = [value]
        return self.get_modified_url()

    def remove_param(self, key):
        if key in self.query_params:
            del self.query_params[key]
        return self.get_modified_url()

    def get_modified_url(self):
        modified_query = urlencode(self.query_params, doseq=True)
        modified_url = urlunparse(
            (
                self.parsed_url.scheme,
                self.parsed_url.netloc,
                self.parsed_url.path,
                self.parsed_url.params,
                modified_query,
                self.parsed_url.fragment,
            )
        )
        return modified_url
