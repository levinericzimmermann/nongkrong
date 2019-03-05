from setuptools import setup

setup(
    name='nongkrong',
    version='0.0.001',
    license='GPL',
    description='Composition enviroment for experimental Javanese-like Gamelan ensemble.',
    author='Levin Eric Zimmermann',
    author_email='levin-eric.zimmermann@folkwang-uni.de',
    url='https://github.com/uummoo/nongkrong',
    packages=['nongkrong', 'nongkrong.forms', 'nongkrong.harmony', 'nongkrong.instruments',
              'nongkrong.metre', 'nongkrong.notation', 'nongkrong.render', 'nongkrong.tempo'],
    package_data={},
    include_package_data=True,
    setup_requires=[''],
    tests_require=['nose'],
    install_requires=[''],
    extras_require={},
    python_requires='>=3.6'
)
