from setuptools import find_namespace_packages, setup

setup(
    name="emmet-api",
    use_scm_version={"root": "..", "relative_to": __file__},
    setup_requires=["setuptools_scm"],
    description="Emmet API Library",
    author="The Materials Project",
    author_email="feedback@materialsproject.org",
    long_description="see README",  # noqa: SIM115
    long_description_content_type="text/markdown",
    url="https://github.com/materialsproject/emmet",
    packages=find_namespace_packages(include=["emmet.*"]),
    install_requires=[
        "numpy<2",
        "emmet-core>=0.78.0rc1",
        "fastapi",
        "gunicorn",
        "boto3",
        "maggma[api]",
        "ddtrace",
        "setproctitle",
        "shapely",
        "asgi-logger",
        "pymatgen-analysis-alloys>=0.0.3",
        "pymatgen-analysis-defects>=2024.10.22",
    ],
    extras_require={
        "test": [
            "pre-commit",
            "pytest",
            "pytest-cov",
            "pycodestyle",
            "pydocstyle",
            "flake8",
            "mypy",
            "mypy-extensions",
            "types-setuptools",
            "types-requests",
            "wincertstore",
        ],
        "docs": [
            "mkdocs",
            "mkdocs-material<8.3",
            "mkdocs-material-extensions",
            "mkdocs-minify-plugin",
            "mkdocstrings",
            "mkdocs-awesome-pages-plugin",
            "mkdocs-markdownextradata-plugin",
            "mkdocstrings[python]",
            "livereload",
            "jinja2",
        ],
    },
    python_requires=">=3.9",
    license="modified BSD",
    zip_safe=False,
)
