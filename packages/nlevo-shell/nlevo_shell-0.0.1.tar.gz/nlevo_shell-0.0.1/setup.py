from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="nlevo-shell",
    version="0.0.1",
    author="nextlab",
    author_email="jay101@nextlab.co.kr",
    description="Shell module for evo.C",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    setup_requires=["setuptools==70.0.0", "wheel==0.43.0"],
    install_requires=[
        "numpy==1.26.4",
        "joblib==1.4.2",
        "paramiko==3.4.1",
        "adbutils==2.8.0",
        "kombu>=5.4.2",
        "pika>=1.3.2",
        "redis>=5.1.0",
        "clickhouse-connect>=0.8.1",
        "pure-python-adb==0.3.0.dev0",
        "retry>=0.9.2",
        "nlevo>=0.0.14",
        "iterators>=0.2.0",
        "pydantic==1.10.15",
        "Pillow>=10.1.0",
    ],
    python_requires=">=3.10",
    packages=find_packages(),
)
