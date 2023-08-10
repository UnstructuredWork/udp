from setuptools import setup, find_packages

setup(
    name='udp',
    version='0.1.0',
    author="SungHyun Nam",
    author_email="tjdgus6255@keti.re.kr",
    url="https://github.com/UnstructuredWork",
    packages=find_packages(where='udp'),
    python_requires='>=3.7',
    install_requires=[
        'opencv-python',
        'opencv-contrib-python',
        'pynvjpeg',
    ]
)





