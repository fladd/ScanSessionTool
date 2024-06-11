from setuptools import setup


def get_version():
    """Get version and version_info from scansessiontool/__meta__.py file."""

    import os
    module_path = os.path.join(os.path.dirname('__file__'), 'scansessiontool',
                               '__meta__.py')

    import importlib.util
    spec = importlib.util.spec_from_file_location('__meta__', module_path)
    meta = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(meta)

    return meta.__version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = 'ScanSessionTool',
    description = \
    'Scan Session Tool - ' \
    'A tool for (f)MRI scan session documentation and data archiving',
    author = 'Florian Krause, Nikos Kogias',
    author_email = 'florian.krause@donders.ru.nl, nikos.kogias@donders.ru.nl',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = 'https://fladd.github.io/ScanSessionTool/',
    version = get_version(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages = ['scansessiontool'],
    package_data = {'scansessiontool': ['help.txt', 'sst.yaml', 'sst_icon.ico',
                                        'sst_icon.png']},
    python_requires=">=3.6",
    setup_requires = ['wheel'],
    install_requires = ['pyYAML',
                        'pydicom'],
    entry_points = {
        'gui_scripts': [
            'scansessiontool = scansessiontool.__main__:run'
        ]
    }
)

