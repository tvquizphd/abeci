import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Natural Language :: English",
    "Intended Audience :: Science/Research",
    "Topic :: Text Processing :: Linguistic",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

setuptools.setup(
    name="abeci",
    version="1.0.4",
    author="TVQuizPhD",
    long_description=long_description,
    author_email="tvquizphd@email.com",
    description="Find perfect pangrams",
    url="https://github.com/tvquizphd/abeci",
    long_description_content_type="text/markdown",
    entry_points=dict(console_scripts=[
        'abeci-pangrams = abeci.pangrams:pangramsCli'
    ]),
    packages=setuptools.find_packages('src'),
    package_data={'': ['./src/abeci/typo/data/*.txt']},
    package_dir={'':'src'},
    install_requires=['abeci'],
    classifiers=classifiers
)
