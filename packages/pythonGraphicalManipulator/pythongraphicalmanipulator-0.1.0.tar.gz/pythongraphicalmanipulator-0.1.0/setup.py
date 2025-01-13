from setuptools import setup, find_packages

setup(
    name='pythonGraphicalManipulator',
    version='0.1.0',
    description='A python library for graphical image manipulation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Dharyansh Achlas',
    url='https://github.com/salchaD-27/pythonGraphicalManipulator.git',
    packages=find_packages(),
    install_requires=[
        'Pillow>=9.0.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)