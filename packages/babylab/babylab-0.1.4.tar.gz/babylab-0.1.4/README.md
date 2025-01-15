# babylab-redcap

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/NeuroDevComp/babylab-redcap/pytest.yml)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/NeuroDevComp/babylab-redcap)
![PyPI - License](https://img.shields.io/pypi/l/babylab)
![PyPI - Status](https://img.shields.io/pypi/status/babylab)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/babylab)
![GitHub Tag](https://img.shields.io/github/v/tag/NeuroDevComp/babylab-redcap)
![PyPI - Version](https://img.shields.io/pypi/v/babylab)

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Updating](#updating)
- [License](#license)

## Installation

You will need Python, ideally Python [3.12.7](https://www.python.org/downloads/release/python-3127/). If you are using Windows, you can install Python from the [App store](https://apps.microsoft.com/detail/9ncvdn91xzqp?hl=en-us&gl=US) or using the terminal via the `winget` command:

```bash
winget install -e --id Python.Python.3.12
```

Once Python is installed, [open your terminal](https://www.youtube.com/watch?v=8Iyldhkrh7E) and run this command:

```bash
python -m pip install flask pywin32 python-dotenv babylab
```

## Usage

To run the app in your browser, run the following command in your terminal:

```bash
python -m flask --app babylab.app run
```

Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000). Log in with your API authentication token, and you should be ready to go!

## Updating

To update the app, run the following line of code in your terminal:

```bash
python -m pip install --upgrade babylab
```

## License

`babylab-redcap` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
