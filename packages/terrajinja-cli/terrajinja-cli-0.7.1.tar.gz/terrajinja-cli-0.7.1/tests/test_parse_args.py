import pytest

from src.terrajinja.cli.parse_args import ParseArgs, dotdict, parse_variables, KeyNotInPath


class ParseArgsNew(ParseArgs):
    def parse_args(self):
        """return all current parsable arguments"""
        return self.parser.parse_args()


class TestParseArgs:
    def test_dotdict_valid(self):
        path = "deep.deeper.right_string"
        dictionary = {
            'right_string': 'my_right',
            'shared_array': ["2", "3"],
            'deep': {
                'deeper': {
                    'right_string': 'my_right',
                    'shared_array': ["2", "3"]
                }
            }
        }
        result = dotdict(path, dictionary)
        assert result == 'my_right'

    def test_dotdict_invalid(self):
        path = "deep.non_existing.right_string"
        dictionary = {
            'right_string': 'my_right',
            'shared_array': ["2", "3"],
            'deep': {
                'deeper': {
                    'right_string': 'my_right',
                    'shared_array': ["2", "3"]
                }
            }
        }

        with pytest.raises(KeyNotInPath) as context:
            dotdict(path, dictionary)

        assert f"unable to parse dotted string" in str(context.value)

    def test_parse_variables_valid(self):
        path = "key1.$key2.key3.$key4"
        dictionary = {
            'key1': 'my_key1',
            'key2': 'my_key2',
            'key3': 'my_key3',
            'key4': 'my_key4',
        }
        result = parse_variables(path, dictionary)
        # only $ based keys should have been replaces with vars in dict
        assert result == 'key1.my_key2.key3.my_key4'

    def test_parse_variables_invalid(self):
        path = "key1.$key2.key3.$unaffected"
        dictionary = {
            'key1': 'my_key1',
            'key2': 'my_key2',
            'key3': 'my_key3',
            'key4': 'my_key4',
        }
        result = parse_variables(path, dictionary)
        # only $ based keys should have been replaces with vars in dict
        # unmatched keys are ignored
        assert result == 'key1.my_key2.key3.$unaffected'


if __name__ == "__main__":
    pytest.main()
