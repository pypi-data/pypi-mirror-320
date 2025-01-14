from setuptools import setup, find_packages

setup(
    name="whisper_speaker_id", 
    version="1.0.1",
    description="Whisper Speaker Identification: A Python library for multiligual speaker identification and speaker embedding generation.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jakaria Emon",
    author_email="jakariaemon1521@gmail.com",
    url="https://github.com/jakariaemon/WSI",  
    packages=find_packages(),
    install_requires=[
        "torch>=2.5.0",
        "torchaudio>=2.5.0",
        "transformers>=4.47.1",
        "scipy>=1.11.4",
    ],
    python_requires=">=3.9",
    license="CC BY-NC-SA 4.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)
