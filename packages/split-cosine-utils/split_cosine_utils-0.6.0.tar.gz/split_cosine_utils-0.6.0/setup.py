from setuptools import setup, find_packages

setup(
    name="split_cosine_utils",
    version="0.6.0",
    description="A utility package for data splitting and cosine similarity computations. With an emphasis on dataframe manipulation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Alfonso Esqueda",
    author_email="alfonso.esqueda.kc@gmail.com",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "scikit-learn"
    ],
    entry_points={
        "console_scripts": [
            "split-data=split_cosine_utils.scripts:split_data_main",
            "cosine-similarity=split_cosine_utils.scripts:cosine_similarity_main",
            "top-5-matches=split_cosine_utils.scripts:top_5_matches_main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
