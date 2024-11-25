from urllib.parse import urlparse

import pandas


def extract_domain(url):
    if pandas.notna(url):
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc

        # Remove any port number
        domain = netloc.split(":")[0]

        # Split the domain by '.' and handle cases with subdomains
        parts = domain.split(".")
        if len(parts) >= 2:
            return ".".join(
                parts[-2:]
            )  # Last two parts are the main domain and suffix
        return domain

    return "Unknown"


# Test the function
url = "http://AzulEye.github.io/HomogeneousSetsFinder"
print(extract_domain(url))  # Output should be 'github.io'
