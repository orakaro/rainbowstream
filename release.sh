# Packaging
python setup.py sdist bdist_wheel
# Check distribution package
twine check dist/*
# Upload to PyPi
twine upload dist/*
# Announce the latest version to Github
git push origin master
