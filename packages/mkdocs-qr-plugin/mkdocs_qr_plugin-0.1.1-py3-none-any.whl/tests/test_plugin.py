import os
import tempfile
import pytest

from mkdocs.structure.files import File
from mkdocs.structure.pages import Page
from mkdocs_qr_plugin.plugin import QRPlugin


@pytest.fixture
def temp_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def config(temp_directory):
    return {"docs_dir": temp_directory}


@pytest.fixture
def site_navigation():
    return []


@pytest.fixture
def page(temp_directory):
    os.mkdir(os.path.join(temp_directory, "test"))
    file_path = os.path.join(temp_directory, "test", "test.md")
    with open(file_path, "w", encoding="utf8") as f:
        f.write("# Heading identifiers in HTML")
    with open(os.path.join(temp_directory, "demo (t).md"), "w", encoding="utf8") as f:
        f.write("# Demo Page")
    with open(os.path.join(temp_directory, "image.png"), "w", encoding="utf8") as f:
        f.write("# Image Page")
    with open(os.path.join(temp_directory, "image (1).png"), "w", encoding="utf8") as f:
        f.write("# Image Page")
    with open(os.path.join(temp_directory, "41m+ZoNoWqL._AC_UF894,1000_QL80_.jpg"), "w", encoding="utf8") as f:
        f.write("# Image Page")
    os.mkdir(os.path.join(temp_directory, "software"))
    with open(
        os.path.join(temp_directory, "software", "git_flow.md"), "w", encoding="utf8"
    ) as f:
        f.write("# Git Flow")

    return Page(
        title="Test Page",
        file=File(file_path, temp_directory, temp_directory, False),
        config={},
    )

@pytest.fixture
def converter(temp_directory, config, site_navigation, page):
    def c(markdown):
        plugin = QRPlugin()
        return plugin.on_page_markdown(markdown, page, config, site_navigation)

    return c

###############################################################################{}
## Text Links
###############################################################################{}

def test_converts_basic_link(converter):
    value = ''':::QR
title
content
:::'''
    result = '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZAAAAGQAQAAAACoxAthAAACSUlEQVR4nO2cXW7qMBBGZ75USt/oDmAndGehO2t3QnZQ3kCCztXYCYG24makeyE/33lKHB8llixrPB5QkygIG0IlCsKGUImCsCFUoiBsCJUoCBtCJQrChlCJgrAhVKJg3opY4utb01Yqb1pfhcRV7jvYsYDKjBVpZ3KZL8ze80wWSU1StO1bzuQElcErtarqi1+ddOVr8kFf/W7n7c8P/LC+oHdPKtNTnn5rLKxe+Zq8/1dvAZUgiAoyB2VpWtguL7D/7y23wM2nVH4CCYNpKkuPaD/bu7R9Syy8fT+usfQFvXtSGYty0IbXHPS+NU9ObfvqQR/WHwT6Uplo0KvfjpNrrU7qFzaisYDKjBW5TA5Xx6tHpb37Vu4642ZMqYUBlSjWkKLanNZtA+DmenGetcZpKVSGrZgu8jmFyEcKERzP9JpZrVpw+3YGEgZU7p/p3b2sTYtjrdVGShNRX5NT2JCSv4MeC6jMWJHLc+RNkVNqzdnxvq2IWPMcuQMSBlSi2C/4lqzymZpKHT5lzaC3AxIGVO4WKtilaiLLbZMZyxGw2uF5+GMBlSCYolJ2JWe5aAd5+9akzMp2dycjGEt/EOhLZXwlZw0eXeiTLOzNZzVP3zJUxpGI6ErO9Mv3berFkylOXm6HPhYq01ZOeTXtQgVPBH/o5uEfdhv85TmV2f3O4thlHbpc2flADnf5MFAJgqgg0y85Ey8Dztu3VHKWmmquyQkqw1SUf10SBFFBqIQBlSCICkIlDKgEQVQQKmFAJQiiglAJM1jlDziVRpllLcdFAAAAAElFTkSuQmCC" alt="title">'
    assert converter(value) == result

