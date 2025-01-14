from setuptools import setup

name = "types-polib"
description = "Typing stubs for polib"
long_description = '''
## Typing stubs for polib

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`polib`](https://github.com/izimobil/polib) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
[Pyre](https://pyre-check.org/),
PyCharm, etc. to check code that uses `polib`. This version of
`types-polib` aims to provide accurate annotations for
`polib==1.2.*`.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/polib`](https://github.com/python/typeshed/tree/main/stubs/polib)
directory.

This package was tested with
mypy 1.14.1,
pyright 1.1.389,
and pytype 2024.10.11.
It was generated from typeshed commit
[`1017916da27688566200b90b14bd457b76402f0e`](https://github.com/python/typeshed/commit/1017916da27688566200b90b14bd457b76402f0e).
'''.lstrip()

setup(name=name,
      version="1.2.0.20250114",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/polib.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['polib-stubs'],
      package_data={'polib-stubs': ['__init__.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0",
      python_requires=">=3.9",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
