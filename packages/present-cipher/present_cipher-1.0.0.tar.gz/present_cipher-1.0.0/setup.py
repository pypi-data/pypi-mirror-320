from setuptools import setup, find_packages

setup(
    name="present_cipher",
    version="1.0.0",
    description="A Python implementation of the PRESENT block cipher",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/present_cipher",  # Укажите свой репозиторий
    packages=find_packages(),
    install_requires=[],  # Здесь указывайте зависимости, если они есть
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
