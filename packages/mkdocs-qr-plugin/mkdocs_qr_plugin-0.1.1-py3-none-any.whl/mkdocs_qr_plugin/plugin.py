import logging

import mkdocs.utils
from mkdocs.plugins import BasePlugin

from mkdocs_qr_plugin.qr_image_generator import QRImageGenerator

log = logging.getLogger(f"mkdocs.plugins.{__name__}")
log.addFilter(mkdocs.utils.warning_filter)


class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class QRPlugin(BasePlugin):

    @staticmethod
    def get_qr_code_data(data: str, size: Size = None, reference: str = None) -> str:
        """
        Generates a QR code as an SVG string.

        Args: data: The data to be encoded in the QR code.
        Returns:str: The png string representing the QR code.
        """

        new_qr_generator = QRImageGenerator(data=data, size=size, reference=reference)

        return new_qr_generator.get_qr_code_base_64_data()

    def on_page_markdown(self,
                         markdown,
                         page,
                         config,
                         site_navigation=None,
                         **kwargs):
        import re

        def generate_image(match):
            title = match.group(1).strip()
            content = match.group(2).strip()

            base_64_qr_code = QRPlugin.get_qr_code_data(data=content, reference=title)

            image_tag = f'<img src="data:image/png;base64,{base_64_qr_code}" alt="{title}">'
            return image_tag

        markdown = re.sub(r":::QR\n(.*?)\n(.*?)\n:::", generate_image, markdown)

        return markdown
