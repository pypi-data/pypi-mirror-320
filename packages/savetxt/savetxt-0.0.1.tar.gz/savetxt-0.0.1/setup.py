from setuptools import setup, find_packages
setup(
    name='savetxt',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'Pandas'
    ],
    entry_points={
        'console_scripts': [
            'savetxt = savetxt.savetxt:cli'
        ],
    },
)
