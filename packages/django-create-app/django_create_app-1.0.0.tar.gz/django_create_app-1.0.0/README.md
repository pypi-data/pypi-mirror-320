# Django Create App

This Django package customizes the `startapp` command to create new apps inside a directory specified by the `DEFAULT_APPS_DIR` setting in your `settings.py`. This ensures that all your Django apps are neatly organized within a designated folder structure, helping you maintain a cleaner project structure.

## Features

-   Modifies the `startapp` command to create apps inside a configurable directory (`DEFAULT_APPS_DIR`) in `settings.py`.
-   Simplifies managing apps within large Django projects by keeping them inside a specific directory.
-   Reduces the need to manually move apps after they are created.

## Installation

To install the package, add it to your project’s `requirements.txt` or run the following command:

```bash
pip install django-create-app
```

## Configuration

1. Install the `django-create-app` like any python packages.

    ```sh
    pip install django-create-app
    ```

2. Update `settings.py`

    Add `DEFAULT_APPS_DIR` variable inside your settings.py. This will define the directory where all the apps are to be included. If you left undeclared, "apps" will be used by default.

    ```python
    # settings.py
    ...
    DEFAULT_APPS_DIR = "apps"
    ...
    ```

3. Now, you can use modified `startapp` command to create new apps inside `DEFAULT_APPS_DIR` directory.

```

```
