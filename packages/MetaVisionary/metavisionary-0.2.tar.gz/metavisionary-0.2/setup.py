from setuptools import setup, find_packages

with open("Readme.md", "r") as f:
    description = f.read() 

setup(
    name='MetaVisionary',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'tensorflow',
        'numpy',
        'scikit-learn'
    ],
    entry_points={
        'console_scripts': [
            'meta_visionary=meta_visionary.few_shot_meta.py:main'
        ]
    },
    author='Subhayu Dutta',
    description='Meta Learning (ProtoMAML) Package',
    long_description=description,  
    long_description_content_type='text/markdown',
    url='https://github.com/subhayudutta/FewShotLearning',
)
