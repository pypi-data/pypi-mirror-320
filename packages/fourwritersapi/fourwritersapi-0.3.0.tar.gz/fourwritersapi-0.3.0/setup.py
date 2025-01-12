from setuptools import setup, find_packages

setup(
    name="fourwritersapi",  # Имя библиотеки
    version="0.3.0",  # Версия
    description="First library for parsing 4writers.net",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="socalmy",
    author_email="sergeitoropov2003@gmail.com",
    url="https://github.com/socalmy/4writersAPI",  # Ссылка на проект
    license="MIT",  # Лицензия
    packages=find_packages(where="src"),  # Автоматический поиск пакетов
    package_dir={"": "src"},
    install_requires=[
        "envparse>=0.2.0",
        "certifi>=2024.8.30",
        "aiohttp>=3.11.10",
        "lxml>=5.3.0",
        "beautifulsoup4>=4.12.0",  # Вместо bs4 используйте корректное название
        "setuptools>=75.7.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Минимальная версия Python
)
