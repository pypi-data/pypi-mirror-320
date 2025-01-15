from setuptools import setup, find_packages

setup(
    name='pycuda_plus',
    version='0.1.0',
    description='User-friendly library to enhance PyCUDA functionality',
    author='Your Name',
    author_email='takuphilchan@gmail.com',
    url='https://github.com/takuphilchan/pycuda_plus',
    packages=find_packages(),
    install_requires=[
        'pycuda',
        # other dependencies
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
