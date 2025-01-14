import logging

import mkdocs.utils
import yaml
from mkdocs.plugins import BasePlugin

from mkdocs_qr_plugin.qr_image_generator import QRImageGenerator, Size, ImageType, CodeType, QRData, SizeStandard

log = logging.getLogger(f"mkdocs.plugins.{__name__}")
log.addFilter(mkdocs.utils.warning_filter)


class QRPlugin(BasePlugin):

    @staticmethod
    def get_image_tag(data: str, size: Size | SizeStandard = SizeStandard.SMALL, reference: str = None, title: str = None) -> str:
        """
        Generates a QR code as an SVG string.

        Args: data: The data to be encoded in the QR code.
        Returns:str: The png string representing the QR code.
        """

        new_qr_generator = QRImageGenerator(code_type=CodeType.QR, output_type=ImageType.SVG, size=size)

        qr_data = QRData(data=data,
                         reference=reference,
                         title=title)

        return new_qr_generator.get_html_tag(qr_data=qr_data)

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

            image_tag = QRPlugin.get_image_tag(data=content, reference=title, size=SizeStandard.MEDIUM)
            return image_tag

        def generate_image_yaml(match):

            try:
                data = yaml.safe_load(match.group(1).strip())

                size = None
                if data.get('width') and data.get('height'):
                    size = Size(data['width'], data['height'])

                if not data.get('data'):
                    raise ValueError("Missing data")

                image_tag = QRPlugin.get_image_tag(data=data['data'], title=data.get('title'), reference=data.get('reference'), size=size)
                return image_tag
            except yaml.YAMLError as exc:
                return f"<b>Error parsing YAML: {exc}</b>"
            except ValueError as exc:
                return f"<b>Missing value: {exc}</b>"

        markdown = re.sub(r":::QR[\n`](.*?)[\n`](.*?)[\n`]:::", generate_image, markdown)
        # markdown = re.sub(r":::QR`(.*?)`(.*?):::", generate_image, markdown)

        markdown = re.sub(r"`{3,}barcode\n([^`]+)\n`{3,}", generate_image_yaml, markdown)

        # page.

        return markdown
