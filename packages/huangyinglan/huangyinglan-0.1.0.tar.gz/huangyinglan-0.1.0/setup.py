from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import setup
from setuptools import find_packages


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    #name="パッケージ名",
    name="huangyinglan",
    version="0.1.0",
    #version="#:",
    license="ライセンス",
    #description="パッケージの説明",
    long_description=open("README.md").read(),  # 長い説明
    long_description_content_type='text/markdown',  # 長い説明のフォーマット
    author="Keigun Rin",    # 作者の名前
    author_email="",    # 作者のメールアドレス
    url="https://github.com/rinkeigun/svg",    # プロジェクトのURL
    packages=find_packages("src"),  # パッケージを自動的に見つけて含める
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    install_requires=_requires_from_file('requirements.txt'),
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-cov"],
    classifiers=[  # パッケージの分類情報
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Pythonのバージョン制限

    package_data={
        '': ['*.txt', '*.rst'],
        'my_package': ['data/*.dat'],
    },
    # scripts=['bin/my_script.py'],
    entry_points={
        'console_scripts': [
            'my_command=my_package.module:function_name',
        ],
    },

)


"""
name
version
description
long_description
author
author_email
maintainer
maintainer_email
url
download_url
packages
py_modules
scripts
ext_modules
classifiers
distclass
script_name
script_args
options
license
keywords
platforms
cmdclass
data_files
package_dir
obsoletes
provides
requires
command_packages
command_options
package_data
include_package_data
libraries
headers
ext_package
include_dirs
password
fullname
**attrs
"""