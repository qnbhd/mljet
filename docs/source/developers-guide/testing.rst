=======
Testing
=======

The test suite is run with the following command:

    $ pytest .

Tests directory has the following structure:

.. code::

    ├── conftest.py         -- Pytest configuration file
    ├── contrib             -- Tests for contrib modules
    ├── cookie              -- Tests for `cookie` module
    ├── functional          -- Functional tests
    ├── iomock.py           -- Mocks for IO
    ├── test_version.py     -- Version test
    └── utils               -- Tests for `utils` module


As metric for testing, we use code coverage.
We also occasionally run mutation testing to check for possible bugs in the test suite.
For mutation testing we use `cosmic-ray <https://cosmic-ray.readthedocs.io/en/latest/>`_.

As an additional library for testing we use `hypothesis <https://hypothesis.readthedocs.io/en/latest/>`_.
It allows us to write tests that generate random data and check that our code works correctly with it.
We believe that this approach is more effective than writing tests for specific cases.

~~~~~~~
IO Mock
~~~~~~~

This functionality requires a separate description.
It is used to mock the input and output streams.
It is used in the tests to check the correctness of the output of the program.

The main idea is to replace the standard input and output streams with the streams that are controlled by the test.
The test can write data to the input stream and read data from the output stream.

You can see file `iomock.py </tests/iomock.py>`_.

IOMock class mock the filesystem for testing purposes.

The filesystem is represented as a tree, where each node is a dict.
The keys are the names of the files and directories, and the values
are either dicts (for directories) or strings (for files).

The tree is stored in the `tree` attribute, and the root of the tree
is stored in the `start_point` attribute.

The `to_forward` argument is a list of paths to files that will be
copied to the mock filesystem. This is useful for testing code that
reads from the filesystem.

The `fs_tree` property returns a string representation of the tree.

After tests we can check that the tree is the same as the original one.

.. code:: python

    def test_default_iomock():
    """Test the default IO mock."""
        # Create a mock object
        mocker = DefaultIOMock()
        # Get into io-mock context
        with mocker:
            # write to file
            with open("test.txt", "w") as fo:
                fo.write("Hello, world!")
            # read from file
            with open("test.txt", "r") as fi:
                assert fi.read() == "Hello, world!"
            # write to binary file
            with open("model.pkl", "wb") as fo:
                fo.write(b"Hello, world!")
            # read from binary file
            with open("model.pkl", "rb") as fi:
                assert fi.read() == b"Hello, world!"
            # Create a directory
            Path("a/b/c").mkdir(parents=True, exist_ok=True)
            assert Path("test.txt").exists()
            assert Path("model.pkl").exists()
        assert (
            mocker.fs_tree
            == """|
        └── tests
        |    ├── a
        |        ├── b
        |            ├── c
        |    ├── model.pkl
        |    ├── test.txt
        """
        )
