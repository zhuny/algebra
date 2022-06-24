from setuptools import setup

setup(
    name='algebra',
    version='0.0.1',
    description='Symbolic Algebra Implementation',
    url='git@github.com:zhuny/algebra',
    author='Jihun Yang',
    author_email='zhuny936772@gmail.com',
    license='unlicense',
    packages=['algebra'],
    package_dir={
        'algebra': 'algebra'
    },
    zip_safe=False,
    test_suite='algebra.tests',
    tests_require=[],
)
