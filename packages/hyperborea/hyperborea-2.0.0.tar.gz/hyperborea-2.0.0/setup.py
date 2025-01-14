import setuptools


def no_local_develop_scheme(version):
    if version.branch == "develop" and not version.dirty:
        return ""
    else:
        from setuptools_scm.version import get_local_node_and_date
        return get_local_node_and_date(version)


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="hyperborea",
    use_scm_version={'write_to': 'hyperborea/version.py',
                     'local_scheme': no_local_develop_scheme},
    setup_requires=['setuptools_scm<7.0'],
    author="Suprock Technologies, LLC",
    author_email="inquiries@suprocktech.com",
    description="Library for streaming and recording from Asphodel devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/suprocktech/hyperborea",
    packages=setuptools.find_packages(),
    keywords="asphodel suprock apd",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: OS Independent",
        "Topic :: System :: Hardware",
    ],
    python_requires=">=3.10",
    install_requires=[
        "asphodel",
        "numpy",
        "packaging",
        "PySide6-Essentials",
        "requests",
        "setproctitle",
    ],
    include_package_data=False,
)
