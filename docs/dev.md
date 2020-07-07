## Vscode

Install python extension `ms-python.python` for python support in vscode and `njpwerner.autodocstring` for auto generation of docstring. Vscode [language specific config](https://code.visualstudio.com/docs/getstarted/settings#_language-specific-editor-settings).
Follow tutorial at https://code.visualstudio.com/docs/python/python-tutorial#_prerequisites

### Linting

- Enable linting by going to command palette: `Python: Enable Linting`

```
pip install pylint
pylint --generate-rcfile > .pylintrc # this generates the default lintrc file.
```

### Dependency management

This project uses Pipfile, instead of requirements.txt for a number of reason. Refer [Pipfile](https://github.com/pypa/pipfile) and [tutorial](https://realpython.com/pipenv-guide/).

```
pip install pipenv
```

### Testing

- pytest is used. It supports giving the configuration in the setup.cfg, tox.ini, pytest.ini and pyproject.toml. Refer [here](https://docs.pytest.org/en/latest/customize.html). And just to simply things, we will be using `tox.ini` with all the `ini` format configuration for all the tools.

## Relative imports used in this project

Refer [here](https://napuzba.com/a/import-error-relative-no-parent).
