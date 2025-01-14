# Copyright 2018 Graham Binns <graham@outcoded.uk>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""Tests for importguardian."""

import os
import shutil
from tempfile import (
    mkdtemp,
    mkstemp,
)
from testtools import TestCase
from textwrap import dedent
from unittest import mock

from importguardian import importguardian


class FindImportsTestCase(TestCase):
    """Tests for importguardian.find_imports()."""

    def test_finds_simple_import_statements(self):
        # find_imports() will find and return simple import statements
        # (e.g. `import foo`).
        imports = importguardian.find_imports(
            dedent(
                """\
            import foo
            import bar, baz
            # This is not an import.
        """
            )
        )
        self.assertDictEqual(
            {
                "foo": set(),
                "bar": set(),
                "baz": set(),
            },
            imports,
        )

    def test_deduplicates_imports(self):
        # find_imports() will de-duplicate import lines so as to only
        # check each import once.
        imports = importguardian.find_imports(
            dedent(
                """\
            import foo
            import foo
            from foo import bar, baz
            from foo import bar
        """
            )
        )
        self.assertDictEqual(
            {
                "foo": {"bar", "baz"},
            },
            imports,
        )

    def test_finds_from_imports(self):
        # find_imports() will find imports in the form `from foo import
        # bar`.
        imports = importguardian.find_imports(
            dedent(
                """\
            from foo import bar, baz
        """
            )
        )
        self.assertDictEqual(
            {
                "foo": {"bar", "baz"},
            },
            imports,
        )

    def test_finds_parenthetic_multiline_imports(self):
        # find_imports() will find imports which are on multiple lines
        # using parenthesis.
        imports = importguardian.find_imports(
            dedent(
                """\
            from foo import (
                bar,
                baz,
            )
        """
            )
        )
        self.assertDictEqual(
            {
                "foo": {"bar", "baz"},
            },
            imports,
        )

    def test_finds_backslashed_multiline_imports(self):
        # find_imports() will find imports which are on multiple lines
        # using backslashes.
        imports = importguardian.find_imports(
            dedent(
                """\
            from foo import\
                bar, \
                baz \
        """
            )
        )
        self.assertDictEqual(
            {
                "foo": {"bar", "baz"},
            },
            imports,
        )

    def test_finds_imports_within_functions(self):
        # find_imports() will find imports which occur within functions
        # (for example when a developer is trying to avoid circular
        # imports.
        imports = importguardian.find_imports(
            dedent(
                """\
            def foo_bar_baz():
                import boing
                from foo import do_the_thing
                from spam import (
                    eggs,
                    ham,
                )
                from ham import\
                    jam, \
                    lovely_spam, \
                    wonderful_spam
        """
            )
        )
        self.assertDictEqual(
            {
                "boing": set(),
                "foo": {"do_the_thing"},
                "spam": {"eggs", "ham"},
                "ham": {"jam", "lovely_spam", "wonderful_spam"},
            },
            imports,
        )


class FindFilesTestCase(TestCase):
    """Tests for importguardian.find_files."""

    def test_finds_python_files_in_target_directory(self):
        # find_files() will find all the .py files in a given directory
        # and return a sorted list of the paths thereto.
        expected_files = []
        temp_dir_path = mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir_path))

        for _ in range(3):
            _, filename = mkstemp(suffix=".py", dir=temp_dir_path)
            expected_files.append(filename)

        found_files = importguardian.find_files(temp_dir_path)
        self.assertListEqual(sorted(expected_files), found_files)

    def test_finds_python_files_in_target_directory_recursively(self):
        # find_files() will search recursively in the target directory.
        expected_files = []
        temp_dir_path = mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir_path))

        for _ in range(3):
            child_temp_path = mkdtemp(dir=temp_dir_path)
            for _ in range(3):
                _, filename = mkstemp(suffix=".py", dir=child_temp_path)
                expected_files.append(filename)

        found_files = importguardian.find_files(temp_dir_path)
        self.assertListEqual(sorted(expected_files), found_files)


class GetForbiddenImportsTestCase(TestCase):
    """Tests for importguardian.get_forbidden_imports()."""

    def test_returns_forbidden_imports_as_a_dict(self):
        # get_forbidden_imports() returns imports which are disallowed
        # according to configuration as list of tuples in the form
        # (import_location, forbidden_module_being_imported).
        temp_dir_path = mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir_path))

        forbidden_imports_config = {
            "forbidden_modules": {
                "module.which.be.forbidden": {
                    "forbidden_from": {
                        "forbidden.from.here",
                        "and.also.from.here",
                    }
                },
            }
        }

        os.makedirs(os.path.join(temp_dir_path, "forbidden", "from"))

        file_path = os.path.join(temp_dir_path, "forbidden", "from", "here.py")
        with open(file_path, "w") as file_:
            file_.write(
                dedent(
                    """\
                import module.which.be.forbidden
            """
                )
            )

        forbidden_imports = importguardian.get_forbidden_imports(
            forbidden_imports_config, file_path, temp_dir_path
        )
        self.assertListEqual(
            [
                (file_path, "module.which.be.forbidden"),
            ],
            forbidden_imports,
        )

    def test_detects_forbidden_imports_in_init_files(self):
        # get_forbidden_imports() will find forbidden imports in
        # __init__.py files.
        temp_dir_path = mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir_path))

        forbidden_imports_config = {
            "forbidden_modules": {
                "module.which.be.forbidden": {
                    "forbidden_from": [
                        "forbidden.from.here",
                        "and.also.from.here",
                    ]
                },
            }
        }

        os.makedirs(os.path.join(temp_dir_path, "and", "also", "from", "here"))
        file_path = os.path.join(
            temp_dir_path, "and", "also", "from", "here", "__init__.py"
        )
        with open(file_path, "w") as file_:
            file_.write(
                dedent(
                    """\
                from module.which.be import forbidden
            """
                )
            )

        forbidden_imports = importguardian.get_forbidden_imports(
            forbidden_imports_config, file_path, temp_dir_path
        )
        self.assertListEqual(
            [
                (file_path, "module.which.be.forbidden"),
            ],
            forbidden_imports,
        )

    def test_detects_imports_of_children_of_forbidden_modules(self):
        # If an import is made from some child point beneath a given
        # forbidden module, get_forbidden_imports() will detect it and
        # flag it.
        temp_dir_path = mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir_path))

        forbidden_imports_config = {
            "forbidden_modules": {
                "module.which": {
                    "forbidden_from": [
                        "forbidden.from.here",
                    ],
                },
            },
        }

        os.makedirs(os.path.join(temp_dir_path, "forbidden", "from"))
        file_path = os.path.join(temp_dir_path, "forbidden", "from", "here.py")

        with open(file_path, "w") as file_:
            file_.write(
                dedent(
                    """\
                from module.which.be import forbidden
            """
                )
            )

        forbidden_imports = importguardian.get_forbidden_imports(
            forbidden_imports_config, file_path, temp_dir_path
        )
        self.assertListEqual(
            [
                (file_path, "module.which.be.forbidden"),
            ],
            forbidden_imports,
        )

    def test_detects_wildcard_forbidden_from_locations(self):
        # If a module is forbidden from being imported in any module, as
        # indicated by a '*' in the config, such imports will be
        # reported by get_forbidden_imports().
        temp_dir_path = mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir_path))

        forbidden_imports_config = {
            "forbidden_modules": {
                "module.which.is.forbidden": {"forbidden_from": ["*"]},
            },
        }

        file_path = os.path.join(temp_dir_path, "this_is_not_allowed.py")

        with open(file_path, "w") as file_:
            file_.write(
                dedent(
                    """\
                from module.which.is.forbidden.from.anywhere import something
            """
                )
            )

        forbidden_imports = importguardian.get_forbidden_imports(
            forbidden_imports_config, file_path, temp_dir_path
        )
        self.assertListEqual(
            [(file_path, "module.which.is.forbidden.from.anywhere.something")],
            forbidden_imports,
        )

    def test_forbidden_from_locations_using_regular_expressions(self):
        # If a forbidden_from location is specified using a regular
        # expression, imports in locations which match those expressions
        # will be reported by get_forbidden_imports()
        temp_dir_path = mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir_path))

        forbidden_imports_config = {
            "forbidden_modules": {
                "module.which.is.forbidden": {
                    "forbidden_from": [".*_not_allow.*"]
                },
            },
        }

        file_path = os.path.join(temp_dir_path, "this_is_not_allowed.py")

        with open(file_path, "w") as file_:
            file_.write(dedent("""\
                from module.which.is.forbidden.from.anywhere import something
            """))

        forbidden_imports = importguardian.get_forbidden_imports(
            forbidden_imports_config, file_path, temp_dir_path)
        self.assertListEqual(
            [(file_path, "module.which.is.forbidden.from.anywhere.something")],
            forbidden_imports
        )

    def test_detects_wildcards_in_forbidden_import_declarations(self):
        # A forbidden import may be specified using wildcards (e.g. foo.bar.*).
        # get_forbidden_imports() will correctly identify these as referring to
        # the parent package or module (e.g. foo.bar).
        temp_dir_path = mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir_path))

        forbidden_imports_config = {
            "forbidden_modules": {
                "module.which.is.*": {"forbidden_from": ["*"]},
            },
        }

        file_path = os.path.join(temp_dir_path, "this_is_not_allowed.py")

        with open(file_path, "w") as file_:
            file_.write(
                dedent(
                    """\
                from module.which.is.forbidden.from.anywhere import something
            """
                )
            )

        forbidden_imports = importguardian.get_forbidden_imports(
            forbidden_imports_config, file_path, temp_dir_path
        )
        self.assertListEqual(
            [(file_path, "module.which.is.forbidden.from.anywhere.something")],
            forbidden_imports,
        )

    def test_detects_forbidden_imports_in_child_modules_of_import_from_locs(
            self):
        # If a module which is forbidden from being imported in a given
        # Python package is imported in a child module of that package,
        # it will be detected by get_forbidden_imports() and returned as
        # forbidden.
        temp_dir_path = mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir_path))

        forbidden_imports_config = {
            "forbidden_modules": {
                "forbidden.module": {
                    "forbidden_from": ["forbidden_from.parent"],
                },
            },
        }

        os.makedirs(os.path.join(temp_dir_path, "forbidden_from", "parent"))
        file_path = os.path.join(temp_dir_path, "forbidden_from", "parent", "child.py")

        with open(file_path, "w") as file_:
            file_.write(
                dedent(
                    """\
                from forbidden import module
            """
                )
            )

        forbidden_imports = importguardian.get_forbidden_imports(
            forbidden_imports_config, file_path, temp_dir_path
        )
        self.assertListEqual([(file_path, "forbidden.module")], forbidden_imports)

    def test_returns_empty_list_if_no_forbidden_imports_found(self):
        # If the Python module being analysed contains no forbidden
        # imports, get_forbidden_imports() will return an empty list.
        temp_dir_path = mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir_path))

        forbidden_imports_config = {
            "forbidden_modules": {
                "forbidden.module": {
                    "forbbiden_from": ["forbidden_from.parent"],
                },
            },
        }

        os.makedirs(os.path.join(temp_dir_path, "forbidden_from", "parent"))
        file_path = os.path.join(temp_dir_path, "forbidden_from", "parent", "child.py")

        with open(file_path, "w") as file_:
            file_.write(
                dedent(
                    """\
                from forbidden import other_module
            """
                )
            )

        forbidden_imports = importguardian.get_forbidden_imports(
            forbidden_imports_config, file_path, temp_dir_path
        )
        self.assertListEqual([], forbidden_imports)

    def test_returns_empty_list_if_no_forbidden_from_locations_specified(self):
        # If the Python module being analysed contains imports from a
        # module marked as forbidden, but which has no forbidden_from
        # modules listed, get_forbidden_imports() will return an empty
        # list.
        temp_dir_path = mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir_path))

        forbidden_imports_config = {
            "forbidden_modules": {"forbidden.module": {"forbidden_from": []}},
        }

        os.makedirs(os.path.join(temp_dir_path, "forbidden_from", "parent"))
        file_path = os.path.join(temp_dir_path, "forbidden_from", "parent", "child.py")

        with open(file_path, "w") as file_:
            file_.write(
                dedent(
                    """\
                from forbidden import module
            """
                )
            )

        forbidden_imports = importguardian.get_forbidden_imports(
            forbidden_imports_config, file_path, temp_dir_path
        )
        self.assertListEqual([], forbidden_imports)

    def test_returns_empty_list_if_no_forbidden_from_stanza_present(self):
        # If the Python module being analysed contains imports from a
        # module marked as forbidden, but which has no forbidden_from
        # stanza declared, get_forbidden_imports will return an empty list.
        temp_dir_path = mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir_path))

        forbidden_imports_config = {
            "forbidden_modules": {"forbidden.module": {}},
        }

        os.makedirs(os.path.join(temp_dir_path, "forbidden_from", "parent"))
        file_path = os.path.join(temp_dir_path, "forbidden_from", "parent", "child.py")

        with open(file_path, "w") as file_:
            file_.write(
                dedent(
                    """\
                from forbidden import module
            """
                )
            )

        forbidden_imports = importguardian.get_forbidden_imports(
            forbidden_imports_config, file_path, temp_dir_path
        )
        self.assertListEqual([], forbidden_imports)


class GetPythonModulePathFromFile(TestCase):
    """Tests for importguardian.get_python_module_path_for_file()."""

    def test_returns_python_module_path_as_list(self):
        # Given a filename which is under the passed PythonPath,
        # get_python_module_path_for_file() will return a list
        # containing the fully-qualified Python module path split into
        # its individual parts.
        test_path = "/foo/bar/baz/bang/bong.py"
        python_path = "/foo/bar/"

        extracted_path = importguardian.get_python_module_path_for_file(
            test_path, python_path
        )
        self.assertListEqual(extracted_path, ["baz", "bang", "bong"])

    def test_correctly_evaluates_missing_trailing_slash_on_python_path(self):
        # If the passed `python_path` value has no trailing slash,
        # get_python_module_path_for_file() will still return the
        # correct module path.
        test_path = "/foo/bar/baz/bang/bong.py"
        python_path = "/foo/bar"

        extracted_path = importguardian.get_python_module_path_for_file(
            test_path, python_path
        )
        self.assertListEqual(extracted_path, ["baz", "bang", "bong"])

    def test_leaves_off_init_part_if_passed(self):
        # If the passed file path ends with __init__.py, this will be
        # disregarded and not included in the returned module path.
        test_path = "/foo/bar/baz/bang/bong/__init__.py"
        python_path = "/foo/bar"

        extracted_path = importguardian.get_python_module_path_for_file(
            test_path, python_path
        )
        self.assertListEqual(extracted_path, ["baz", "bang", "bong"])

    def test_handles_multiple_python_paths(self):
        # `python_path` can be a colon-delimited string (as with
        # PYTHONPATH). If so, get_python_module_path_for_file() will try
        # each path within that string individually.
        test_path = "/foo/bar/baz/bang/bong.py"
        python_path = "/foo/baz:/foo/bar"

        extracted_path = importguardian.get_python_module_path_for_file(
            test_path, python_path
        )
        self.assertListEqual(extracted_path, ["baz", "bang", "bong"])

    def test_raises_error_if_file_not_on_any_python_path(self):
        # If the file path does not contain any of the passed python
        # paths, get_python_module_path_for_file() will raise a
        # ValueError, since it can't calculate the module name
        # confidently.
        test_path = "/foo/bar/baz/bang/bong.py"
        python_path = "/spam/eggs:/ham/jam"

        self.assertRaises(
            ValueError,
            importguardian.get_python_module_path_for_file,
            test_path,
            python_path,
        )


class MainTestCase(TestCase):
    """Tests for importguardian.main()."""

    def test_calls_get_forbidden_imports_for_all_files_under_target_dir(self):
        # main() will call get_forbidden_imports() for each file under
        # the target directory passed to it in the TARGET command-line
        # argument.
        temp_dir_path = mkdtemp()
        importguardian.PYTHON_PATH = temp_dir_path

        file_paths = sorted(
            path for _, path in [mkstemp(dir=temp_dir_path) for _ in range(3)]
        )
        config = {
            "forbidden_modules": {
                "foo.bar.baz": {
                    "*",
                },
            },
        }
        mock_args = mock.Mock(target=temp_dir_path, python_path=temp_dir_path)

        self.patch(importguardian, "get_args", lambda: mock_args)
        self.patch(importguardian, "get_config", lambda x: config)
        self.patch(importguardian, "find_files", lambda x: file_paths)
        self.patch(importguardian, "get_forbidden_imports", mock.Mock(return_value=[]))

        importguardian.main()
        importguardian.get_forbidden_imports.assert_has_calls(
            [mock.call(config, file_path, temp_dir_path) for file_path in file_paths]
        )

    def test_outputs_forbidden_imports_to_stderr(self):
        # main() will return any forbidden imports returned by
        # get_forbidden_imports() to stderr.
        temp_dir_path = mkdtemp()
        importguardian.PYTHON_PATH = temp_dir_path

        file_paths = sorted(
            path for _, path in [mkstemp(dir=temp_dir_path) for _ in range(3)]
        )
        config = {
            "forbidden_modules": {
                "foo.bar.baz": {
                    "*",
                },
            },
        }
        mock_args = mock.Mock(target=temp_dir_path, python_path=temp_dir_path)

        self.patch(importguardian.sys.stderr, "write", mock.MagicMock())
        self.patch(importguardian.sys, "exit", mock.MagicMock())

        self.patch(importguardian, "get_args", lambda: mock_args)
        self.patch(importguardian, "get_config", lambda x: config)
        self.patch(importguardian, "find_files", lambda x: file_paths)
        self.patch(
            importguardian,
            "get_forbidden_imports",
            mock.Mock(
                return_value=[
                    ("file_{}".format(char), "foo.bar.baz.{}".format(char))
                    for char in ["A", "B", "C"]
                ]
            ),
        )

        importguardian.main()

        importguardian.sys.stderr.write.assert_has_calls(
            [
                mock.call(
                    "foo.bar.baz.{} may not be imported in file_{}\n".format(char, char)
                )
                for char in ["A", "B", "C"]
            ]
        )

    def test_calls_sys_exit_if_forbidden_imports_exist(self):
        # main() will exit with a status code of '1' if there are
        # forbidden imports.
        temp_dir_path = mkdtemp()
        importguardian.PYTHON_PATH = temp_dir_path

        file_paths = sorted(
            path for _, path in [mkstemp(dir=temp_dir_path) for _ in range(3)]
        )
        config = {
            "forbidden_modules": {
                "foo.bar.baz": {
                    "*",
                },
            },
        }
        mock_args = mock.Mock(target=temp_dir_path, python_path=temp_dir_path)

        self.patch(importguardian.sys.stderr, "write", mock.MagicMock())
        self.patch(importguardian.sys, "exit", mock.MagicMock())

        self.patch(importguardian, "get_args", lambda: mock_args)
        self.patch(importguardian, "get_config", lambda x: config)
        self.patch(importguardian, "find_files", lambda x: file_paths)
        self.patch(
            importguardian,
            "get_forbidden_imports",
            mock.Mock(
                return_value=[
                    ("file_{}".format(char), "foo.bar.baz.{}".format(char))
                    for char in ["A", "B", "C"]
                ]
            ),
        )

        importguardian.main()
        importguardian.sys.exit.assert_called_once_with(1)

    def test_does_not_call_sys_exit_if_no_forbidden_imports_exist(self):
        # main() will not call sys.exit() if there are no forbidden
        # imports found.
        temp_dir_path = mkdtemp()
        importguardian.PYTHON_PATH = temp_dir_path

        file_paths = sorted(
            path for _, path in [mkstemp(dir=temp_dir_path) for _ in range(3)]
        )
        config = {
            "forbidden_modules": {
                "foo.bar.baz": {
                    "*",
                },
            },
        }
        mock_args = mock.Mock(target=temp_dir_path, python_path=temp_dir_path)

        self.patch(importguardian.sys.stderr, "write", mock.MagicMock())
        self.patch(importguardian.sys, "exit", mock.MagicMock())

        self.patch(importguardian, "get_args", lambda: mock_args)
        self.patch(importguardian, "get_config", lambda x: config)
        self.patch(importguardian, "find_files", lambda x: file_paths)
        self.patch(importguardian, "get_forbidden_imports", mock.Mock(return_value=[]))

        importguardian.main()
        importguardian.sys.exit.assert_not_called()

    def test_exits_with_helpful_error_if_config_file_does_not_exist(self):
        # If importguardian.json does not exist on disk, main() will
        # exit with error code 2 and will print an error to the
        # terminal.
        self.patch(
            importguardian,
            "get_args",
            lambda: mock.MagicMock(config_file="foobarbaz.blah"),
        )
        self.patch(
            importguardian,
            "get_config",
            mock.MagicMock(side_effect=FileNotFoundError("No such file!")),
        )
        self.patch(importguardian.sys, "exit", mock.MagicMock())
        self.patch(importguardian.sys.stderr, "write", mock.MagicMock())
        importguardian.main()

        importguardian.sys.stderr.write.assert_has_calls(
            [
                mock.call(
                    "Couldn't find config file at foobarbaz.blah. Does the file "
                    "exist?"
                )
            ],
            any_order=True,
        )
        importguardian.sys.exit.assert_called_once_with(2)
