# device values prometheus exporter

Access Gardena Smartsystem device values in prometheus format

# Disclaimer

This is not an official Gardena project, use own your own risk!

## Getting Started

1.  python3.10 -m venv env
2.  . env/bin/activate
3.  pip install -U poetry
4.  poetry install --no-root --with dev
5.  cp config.yaml.example config.yaml
6.  # edit config.yaml
7.  uvicorn gardena_smartsystem_prometheus_exporter.serve:app


## Config

By default the app looks for a config.yaml in the project folder,
to overwrite the path to the config set the environment variable `SGPE_CONFIG_FILE`.
While the example is a yaml file, json is also supported.
