from setuptools import setup, find_packages

setup(
    name='workflow_builder',
    version='0.1',
    author='Ifilk',
    author_email='suanxc@yeah.net',
    url='https://github.com/Ifilk/WorkflowBuilder',
    description='A tool for building and executing workflows',
    long_description=open('README.txt').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'toml',
    ],
    python_requires='>=3.6',
)
