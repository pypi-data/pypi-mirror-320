from setuptools import setup, find_packages

setup(
    name="qwertyou1",  # 패키지 이름
    version="0.1.1",  # 초기 버전
    description="A sample package named qwertyou11",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="qwertyou1",
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
            "qwertyou1=qwertyou1.main:main",  # CLI 명령어 정의
            "hello=qwertyou1.main:hi",  # CLI 명령어 정의
        ],
    },
)
