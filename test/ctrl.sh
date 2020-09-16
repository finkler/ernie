#!/bin/bash
case "$1" in
  clean)
    rm -rf build/ dist/ ernie.egg-info/
    find . -name __pycache__ -prune -exec rm -r {} \;
    ;;
  make)
    python3 setup.py sdist bdist_wheel
    ;;
  purge)
    rm -rf .venv/
    ;;
  upload)
    python3 -m twine upload --repository testpypi dist/*
    ;;
  venv)
    python3 -m venv .venv/
    ;;
  *)
    source .venv/bin/activate
    pip install --upgrade .
    deactivate
esac

