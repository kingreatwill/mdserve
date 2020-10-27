import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


NAME = "mdserve"
VERSION = "0.0.1"
requirements = [
    n.strip() for n in read('requirements.txt').split('\n') if n.strip()
]
setup(
    name=NAME,
    version=VERSION,
    license='MIT',
    description="Markdown server.",
    author="kingreatwill",
    author_email="350840291@qq.com",
    url="https://github.com/openjw/mdserve",
    keywords=["markdown"],
    packages=find_packages(),
    package_data={'': ['*.css', '*.ico']},
    install_requires=requirements,
    include_package_data=True,
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'mdserve = mdserve.__main__:main'
        ]
    },
)
"""
python setup.py check
python setup.py sdist bdist_wheel
# python setup.py install
twine upload dist/mdserve-0.0.1*
"""
