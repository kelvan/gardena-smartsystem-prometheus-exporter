# gardena smartsystem prometheus exporter

Access Gardena Smartsystem device values in prometheus format

# Disclaimer

This is not an official Gardena project, use at your own risk!

## Getting Started

1.  poetry install --no-root --with dev
2.  cp config.yaml.example config.yaml
3.  edit config.yaml
4.  poetry run uvicorn gardena_smartsystem_prometheus_exporter.serve:app


## Config

By default the app looks for a config.yaml in the project folder,
to overwrite the path to the config set the environment variable `SGPE_CONFIG_FILE`.
While the example is a yaml file, json is also supported.

For more settings (logging, ...) see gardena_smartsystem_prometheus_exporter/config.py
Example to set the log level use `SGPE_LOG_LEVEL`

**Beware:** nested parameters like `SGPE_LOG_FILE.FILENAME` probably won't work when set using `export`,
defining them in .env or as docker env should work.
