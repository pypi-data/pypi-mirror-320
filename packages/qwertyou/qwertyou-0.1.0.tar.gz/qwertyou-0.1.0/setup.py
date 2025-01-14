from setuptools import setup, find_packages

setup(
    name="qwertyou",  # 패키지 이름
    version="0.1.0",  # 초기 버전
    description="A sample package named qwertyou",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="qwertyou",
    author_email="chjw1346@gmail.com",
    url="https://github.com/qw3rtyou",
    packages=find_packages(),
    classifiers=[   
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "qwertyou=qwertyou.main:main",  # CLI 명령어 정의
        ],
    },
)
