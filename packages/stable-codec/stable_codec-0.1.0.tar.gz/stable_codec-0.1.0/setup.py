from setuptools import setup, find_packages

setup(
    name='stable-codec',
    version='0.1.0',
    author='Stability AI',
    author_email='julian.parker@stability.ai',
    description='Stable Codec: A series of codec models for speech and audio',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Stability-AI/stable-codec/',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=['packaging',
                      'wheel',
                      'torch==2.4',
                      'torchaudio==2.4',
                      'stable-audio-tools==0.0.17',
                      'pytorch-lightning==2.1',
                      'prefigure==0.0.9']
)