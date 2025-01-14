# fckafde-shortener

**fckafde-shortener** is a Python library for interacting with the [fckaf.de](https://fckaf.de/) URL shortener service, which supports anti-nazi initiatives in Germany. This library allows you to:

- Shorten URLs
- De-shorten fckaf.de URLs to reveal the original URL
- Generate forward URLs with appended information

## Installation

You can install the library via pip after uploading it to PyPI:
```bash
pip install fckafde-shortener
```

## Usage

### 1. Shorten a URL
Use the `shorten_url` function to shorten a long URL.
```python
from fckafde_shortener import shorten_url

short_url = shorten_url("https://example.com")
if short_url:
    print("Shortened URL:", short_url)
else:
    print("Failed to shorten URL.")
```

### 2. De-shorten a fckaf.de Short URL
Use the `de_shorten_url` function to retrieve the original URL from a fckaf.de short URL.
```python
from fckafde_shortener import de_shorten_url

original_url = de_shorten_url("https://fckaf.de/Xkp")
if original_url:
    print("Original URL:", original_url)
else:
    print("Failed to retrieve the original URL.")
```

### 3. Generate Forward URLs
Use the `generate_forward_url` function to append additional information to a URL retrieved from a fckaf.de short URL, which will be visible in the URL.
```python
from fckafde_shortener import generate_forward_url

forward_url = generate_forward_url("https://fckaf.de/Xkp", "some-info")
if forward_url:
    print("Forward URL:", forward_url)
else:
    print("Failed to generate forward URL.")
```

## Requirements
- Python 3.6 or newer
- `requests`
- `beautifulsoup4`

Install dependencies with:
```bash
pip install requests beautifulsoup4
```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.