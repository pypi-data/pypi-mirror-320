import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='fond-utils',
      version='0.0.1',
      description='Utilities for parsing and manipulating the FOND planning language.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/AI-Planning/fond-utils',
      author='Sebastian Sardina, Christian Muise',
      license='MIT',
      packages=['fondutils'],
      scripts=['bin/fond-utils'],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX :: Linux",
      ],
      python_requires='>=3.8',
      include_package_data=True,
      install_requires=['pddl'],
      zip_safe=False)
