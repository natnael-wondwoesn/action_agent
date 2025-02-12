from setuptools import setup, find_packages

setup(
    name="action_agent",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "streamlit_extras",
        "langchain",
        "python-dotenv",
        "requests",
        "beautifulsoup4",
        "lxml",
    ],
)
