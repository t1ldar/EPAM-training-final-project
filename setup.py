"""
A setuptools based setup module.
"""
from setuptools import setup, find_packages

setup(
    name="rssreaderproject",
    version='0.6.0',
    description="RSS reader for all human beings",
    author="Ildar Galin",
    author_email="ildar.f.galin@gmail.com",
    packages=find_packages(),
    package_data={'': ['html_template.html']},
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml",
        "python-dateutil",
        "fpdf2",
        "Jinja2",
        "xhtml2pdf",
        "Pygments",
        "Pillow",
        "EbookLib",
        "colorlog",
        "ansicolors"
    ],
    entry_points={
        "console_scripts": ['rss_reader=rss_parser.rss_reader:main']
    }
)
