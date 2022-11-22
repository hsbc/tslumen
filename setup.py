from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

with open('requirements-extras.txt', 'r') as f:
    install_requires_extras = f.read().splitlines()


setup(
    python_requires='>=3.6.0',
    use_scm_version=True,
    packages=find_packages(),
    package_data={'tslumen': ['py.typed',
                              "templates/ipython/*",
                              "templates/html/*", "templates/html/static/*",
                              "templates/dashboard/*", "templates/dashboard/static/*"]},
    zip_safe=False,
    entry_points={'console_scripts': ['tslumen = tslumen.cli:main']},
    install_requires=install_requires,
    extras_require={'extras': install_requires_extras},
)
