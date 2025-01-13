from setuptools import setup, find_packages

setup(
    name="textfx",  # نام لایبرری
    version="0.1.0",  # نسخه لایبرری
    packages=find_packages(),  # پیدا کردن ماژول‌ها
    install_requires=[],  # وابستگی‌ها (مثلاً numpy یا pandas)
    description="textfx is a Python library for creating dynamic and visually engaging text effects.",
    author="Ilia Karimi",
    author_email="",
    url="https://github.com/iliakarimi/textfx",  # لینک به گیت‌هاب
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
