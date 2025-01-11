from setuptools import setup, find_packages

setup(
    name="uLLMpy",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'ujson',
        'urequests',
    ],
    author="RiviaRammer",
    author_email="RiviaRammer@gmail.com",
    description="MicroPython library for LLM access on MCU",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/RiviaRammer/uLLMpy",  # 替换为你自己的GitHub链接
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.7',
)

