from setuptools import setup

name = "types-lupa"
description = "Typing stubs for lupa"
long_description = '''
## Typing stubs for lupa

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`lupa`](https://github.com/scoder/lupa) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
[Pyre](https://pyre-check.org/),
PyCharm, etc. to check code that uses `lupa`. This version of
`types-lupa` aims to provide accurate annotations for
`lupa==2.4.*`.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/lupa`](https://github.com/python/typeshed/tree/main/stubs/lupa)
directory.

This package was tested with
mypy 1.14.1,
pyright 1.1.389,
and pytype 2024.10.11.
It was generated from typeshed commit
[`38d2fe81fee593468d0738f89a5b5101a86f4e53`](https://github.com/python/typeshed/commit/38d2fe81fee593468d0738f89a5b5101a86f4e53).
'''.lstrip()

setup(name=name,
      version="2.4.0.20250112",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/lupa.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['lupa-stubs'],
      package_data={'lupa-stubs': ['__init__.pyi', 'lua51.pyi', 'lua52.pyi', 'lua53.pyi', 'lua54.pyi', 'luajit20.pyi', 'luajit21.pyi', 'version.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0",
      python_requires=">=3.9",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
