from setuptools import setup, find_packages

setup(
    name="db-connector-kr",
    version="0.1.2",
    author="Sanggu Lim",
    author_email="data.ai.lim39@gmail.com",
    description="A Python library for connecting to various databases.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lim39/dbconnector",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "snowflake-connector-python",        
        "pymysql",
        "pymssql"
    ],
    extras_require={
        "postgres": ["psycopg2-binary"],  # Optional dependency
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
