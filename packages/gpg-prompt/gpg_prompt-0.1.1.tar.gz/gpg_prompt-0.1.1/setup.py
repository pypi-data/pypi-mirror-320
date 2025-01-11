from setuptools import setup, find_packages

setup(
    name="gpg-prompt",
    version="0.1.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
        ]
    },
    entry_points={
    'console_scripts': [
            'fzf-gpg=gpg_prompt.fzf:main',
            'rofi-gpg=gpg_prompt.rofi:main',
        ],
    },
    package_data={
        'gpg_prompt': ['db/*.json', 'icon.png'],
    },
    author="ubuntupunk",
    author_email="ubuntupunk@gmail.com",
    description="A gpg command prompter and manual browser using rofi/fzf",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ubuntupunk/gpg-prompt",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
)
