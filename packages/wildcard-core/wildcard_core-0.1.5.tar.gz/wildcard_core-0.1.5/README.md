# Wilcard Core Package

Build new version of package:

1. Modify `pyproject.toml` with new version number
2. Generate poetry lock file
```
poetry lock
```
3. Build and publish package to test PyPI
```
poetry publish --build -r test-pypi
```

Troubleshooting:

- *RuntimeError: Repository test.pypi is not defined*

    - Add repository to poetry config
    ```
    poetry config repositories.test-pypi https://test.pypi.org/legacy/
    ```
    - Create new token at https://test.pypi.org/manage/account/token/
    - Add token to poetry config
    ```
    poetry config pypi-token.test-pypi <your-token>
    ```

- *poetry.publishing.uploader.UploadError: HTTP Error 400: File already exists*

    - Check you've updated the version number in `pyproject.toml`

    - Try publishing again
    ```
    poetry publish --build -r test-pypi
    ```
    
    - If the error persists, clear the existing package files and try again.
    ```
    rm -rf dist/*
    ```
