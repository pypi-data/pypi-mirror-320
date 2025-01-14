import os

import pytest

from src.terrajinja.cli.parser import ParseConfig


class TestParser:
    dir = os.path.dirname(os.path.abspath(__file__))

    def test_parse_templates_order_1(self):
        parser = ParseConfig(custom_args=["deploy"])
        parameters = {
            'templates': {
                "default_template": "0.0.1",
                "additional_template": "0.0.1"
            }

        }
        dictionary = parser.parse_templates(os.path.join(self.dir, 'config', 'templates'), parameters)
        assert dictionary['original'] == 'additional'

    def test_parse_templates_order_2(self):
        parser = ParseConfig(custom_args=["deploy"])
        parameters = {
            'templates': {
                "additional_template": "0.0.1",
                "default_template": "0.0.1"
            }

        }
        dictionary = parser.parse_templates(os.path.join(self.dir, 'config', 'templates'), parameters)
        assert dictionary['original'] == 'original'


if __name__ == "__main__":
    pytest.main()
