# RandomPi v2.0.2

RandomPi is a simple package that uses the PyPi api to get a random python package.

## Authors

- [**Wyatt Johnson**](https://github.com/realendie)

## Install

```bash
  pip install RandomPi
```

## Commands

```bash
    get_random_pi
    get_random_info
    get_project_info
```

## PyPi Index Api

```http
   GET /simple/ HTTP/1.1
   Host: pypi.org
   Accept: application/vnd.pypi.simple.v1+html
```

## PyPi Json Api

```http
    GET /pypi/sampleproject/json HTTP/1.1
    Host: pypi.org
    Accept: application/json
```

## License

[**Apache-2.0**](https://www.apache.org/licenses/LICENSE-2.0)
