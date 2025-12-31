"""
BiliCache 安装配置
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bilicache",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="B站视频自动下载缓存工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bilicache",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "bilibili-api>=5.0.0",
        "aiohttp>=3.8.0",
        "tomli-w>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    # Note: main function is async, use: python main.py or python -m bilicache
    # entry_points={
    #     "console_scripts": [
    #         "bilicache=main:main",
    #     ],
    # },
)

