# Inbox4us Pos Printer

# Prepare install
pip install setuptools wheel twine

# Build:
python setup.py sdist bdist_wheel

# Publish:
twine upload dist/*
