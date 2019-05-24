from setuptools import setup

setup(
    name='nongkrong',
    version='0.0.001',
    license='GPL',
    description='Composition enviroment for experimental Javanese-like Gamelan ensemble.',
    author='Levin Eric Zimmermann',
    author_email='levin-eric.zimmermann@folkwang-uni.de',
    url='https://github.com/uummoo/nongkrong',
    packages=['nongkrong', 'nongkrong.score', 'nongkrong.harmony', 'nongkrong.instruments',
              'nongkrong.metre', 'nongkrong.delays', 'nongkrong.render', 'nongkrong.render.sound', 'nongkrong.render.sound.synthesis', 'nongkrong.tempo', 'nongkrong.tools', 'nongkrong.interfunctions'],
    package_data={'': ['nongkrong/render/sound/synthesis/12edo']},
    include_package_data=True,
    setup_requires=[''],
    tests_require=['nose'],
    install_requires=[''],
    extras_require={},
    python_requires='>=3.6'
)
