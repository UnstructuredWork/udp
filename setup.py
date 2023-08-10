from setuptools import setup, find_packages

setup(
    name='udp',
    version='0.1.0',
    author="SungHyun Nam",
    author_email="tjdgus6255@keti.re.kr",
    packages=find_packages(),
    py_modules=['udp.stereo_client, udp.rgbd_client'],
    python_requires='>=3.7',
    install_requires=[
        'opencv-python',
        'opencv-contrib-python',
        'pynvjpeg',
    ]
)





