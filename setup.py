from setuptools import setup, find_packages

requires = [
    "pastedeploy",
    "six",
]

try:
    import argparse
except ImportError:
    requires.append("argparse")

tests_require = [
    "nose",
    "coverage",
]

points = {
    "console_scripts": [
        "wsgirunner=wsgirunner.commands:main",
    ],
    "paste.server_factory": [
        "wsgiref=wsgirunner.server:wsgiref_server_factory",
    ],
}

setup(
    name="wsgirunner",
    version="0.0",
    author="Atsushi Odagiri",
    author_email="aodagx@gmail.com",
    install_requires=requires,
    tests_require=tests_require,
    extras_require={
        "testing": tests_require,
        "dev": ["tox"],
    },
    packages=find_packages("src"),
    package_dir={'': 'src'},
    test_suite="wsgirunner",
    entry_points=points,
)
