from setuptools import setup, find_packages

version = '0.2.6'

install_requires = [
    "python-dateutil",
    "requests",
    "pyfiglet",
    "SQLAlchemy",
    "pysqlite",
    "twitter",
    "Pillow",
]

setup(name='rainbowstream',
      version=version,
      description="A smart and nice Twitter client on terminal.",
      long_description=open("./README.rst", "r").read(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: End Users/Desktop",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
          "Topic :: Utilities",
          "License :: OSI Approved :: MIT License",
      ],
      keywords='twitter, command-line tools, web 2.0, stream API',
      author='Vu Nhat Minh',
      author_email='nhatminh179@gmail.com',
      url='https://github.com/DTVD/rainbowstream',
      license='MIT License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=install_requires,
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      rainbowstream=rainbowstream.rainbow:fly
      """,
      )
