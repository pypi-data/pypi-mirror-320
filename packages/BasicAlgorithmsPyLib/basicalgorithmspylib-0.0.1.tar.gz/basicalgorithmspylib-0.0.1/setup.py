from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r') as f:
        return f.read()

setup(
    name='BasicAlgorithmsPyLib',
    version='0.0.1',
    author='MindlessMuse666',
    author_email='mindlessmuse.666@gmail.com',
    description='The "BasicAlgorithmsPyLib" library this is a cozy place for the most common algorithms.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/MindlessMuse666/basic-algorithms',
    packages=find_packages(),
    install_requires=['requests>=2.25.1'],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='python algorithms algorithms-library first-library sorting searching data-structures',
    project_urls={
        'GitHub': 'https://github.com/MindlessMuse666'
    },
    python_requires='>=3.6'
)