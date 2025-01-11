from setuptools import setup, find_packages
setup(
    name='addition-package-yuwenjun',
    version='0.1.0',
    description='A simple package to add two numbers',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='yuwenjun',
    author_email='1214294908@qq.com',
    url='https://github.com/your_username/addition_package',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
)