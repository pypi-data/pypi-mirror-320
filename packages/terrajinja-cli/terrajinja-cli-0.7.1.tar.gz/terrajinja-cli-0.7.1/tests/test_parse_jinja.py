import os

import pytest

from src.terrajinja.cli.parse_jinja import ParseJinja, jinja_json_regex


class TestParseJinja:
    dir = os.path.dirname(os.path.abspath(__file__))

    def test_merge(self):
        left = {
            'left_string': 'my_left',
            'shared_array': ["1", "2"],
            'deep': {
                'deeper': {
                    'left_string': 'my_left',
                    'shared_array': ["1", "2"]
                }
            }
        }
        right = {
            'right_string': 'my_right',
            'shared_array': ["2", "3"],
            'deep': {
                'deeper': {
                    'right_string': 'my_right',
                    'shared_array': ["2", "3"]
                }
            }
        }
        parser = ParseJinja()
        merged = parser.merge(left, right)

        assert merged['left_string'] == 'my_left'
        assert merged['right_string'] == 'my_right'
        assert merged['deep']['deeper']['left_string'] == 'my_left'
        assert merged['deep']['deeper']['right_string'] == 'my_right'
        assert merged['shared_array'] == ["1", "2", "2", "3"]

    def test_get_yaml_filenames(self):
        parser = ParseJinja()
        files = parser.get_yaml_filenames(os.path.join(self.dir, 'config', 'parameters'))
        assert os.path.join(self.dir, 'config', 'parameters', 'test.yaml') in files

    def test_parse_file_parameters(self):
        parser = ParseJinja()
        y = parser.parse_file(os.path.join(self.dir, 'config', 'parameters', 'test.yaml'))
        assert len(y['array_of_choices']) == 3
        assert y['test_var'] == "my_var"
        assert y['path']['to']['custom_choice']['choices'][0] == "choice_A"

    def test_parse_file_templates(self):
        parser = ParseJinja()
        y = parser.parse_file(os.path.join(self.dir, 'config', 'templates', 'default_template_v0.0.1.yaml'),
                              {'test_var': 'my_test_var'})
        assert y['template']['my_string'] == "my_test_var"

    def test_parse_directory(self):
        parser = ParseJinja()
        y = parser.parse_directory(os.path.join(self.dir, 'config', 'parameters'))
        assert len(y['array_of_choices']) == 6
        assert y['test_var'] == "my_var"
        assert y['path']['to']['custom_choice']['choices'][0] == "choice_A"

    @pytest.mark.parametrize(
        "obj, path, match, replace, expected",
        [
            ('{"key": "value"}', 'key', 'a', 'B', '{"key": "vBlue"}'),
            ('{"key": "value"}', 'key', r'va(\w+)e', r'\1', '{"key": "lu"}'),
            ('{"key": {"sub": "value"}}', 'key.sub', r'va(\w+)e', r'\1', '{"key": {"sub": "lu"}}'),
            ('{"key": {"sub": {"sub2": "value"}}}', 'key.sub.sub2', r'va(\w+)e', r'\1',
             '{"key": {"sub": {"sub2": "lu"}}}'),
            ('{"key": { "array": [ "key:value" ]}}', 'key.array', r'key:(\w+)', r'\1', '{"key": {"array": ["value"]}}'),
        ],
    )
    def test_jinja_json_regex(self, obj, path, match, replace, expected):
        actual = jinja_json_regex(obj, path, match, replace)
        assert actual == expected

    @pytest.mark.parametrize(
        "obj, path, expected",
        [
            ('{"key": "value"}', 'key', '{}'),
            ('{"key": 10}', 'key', '{}'),
        ],
    )
    def test_jinja_json_regex_delete(self, obj, path, expected):
        actual = jinja_json_regex(obj, path, '', '', delete_key=True)
        assert actual == expected


if __name__ == "__main__":
    pytest.main()
