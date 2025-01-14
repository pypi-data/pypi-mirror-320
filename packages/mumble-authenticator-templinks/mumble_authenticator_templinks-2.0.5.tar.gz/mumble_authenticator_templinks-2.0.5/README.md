# Alliance Auth - Mumble Temp Links Authenticator

This is a thoroughly reviewed version of the Authenticator.

Major changes:

- Utilized [poetry](https://python-poetry.org) for project management.
- Codebase is now modular, split into several files for better organization.
- Configuration is managed through YAML files and/or environment variables. See [examples](examples/).
- Implemented [diskcache](https://pypi.org/project/diskcache) to cache avatars.
- Utilized [diskcache](https://pypi.org/project/diskcache) to cache specific database queries, allowing the authenticator to function even if the database connection is unavailable.
- Added Docker support. See [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml).
- Included connection check to ensure proper ICE server functionality.
- Added Prometheus metrics for monitoring.

## Important Warning

It is **highly discouraged** to run this container with multiple networks, as shown below:

```yaml
networks:
  network_alpha:
  network_omega:
```

This setup can lead to issues where the callback announcement:

```python
self.adapter = ice.createObjectAdapterWithEndpoints(
    "Callback.Client", f"tcp -h {host} -p {port}"
)
```

might use the wrong network interface. Consequently, the Mumble server could attempt to connect to an address that is unreachable from the given network. This can cause unpredictable behavior and connectivity issues.

## Requirements

The authenticator is designed to work in conjunction with the following applications:

- [Alliance Auth](https://gitlab.com/allianceauth/allianceauth)
- [Mumble Temp Links](https://github.com/Solar-Helix-Independent-Transport/allianceauth-mumble-temp)

## Configuration

The application can be configured using either YAML files or environment variables. The structure of environment variables corresponds to the structure of the YAML configuration file.

For example, given the following YAML configuration:

```yaml
database:
  host: 127.0.0.1
  name: alliance_auth
```

You can set the equivalent environment variables as:

```bash
MA__DATABASE__HOST=127.0.0.1
MA__DATABASE__NAME=alliance_auth
```

Similarly, for a more complex configuration such as:

```yaml
ice_properties:
  - "Ice.ThreadPool.Server.Size = 5"
```

You can set the corresponding environment variable as:

```bash
MA__ICE_PROPERTIES__0="Ice.ThreadPool.Server.Size = 5"
```

### Environment Variable Syntax

- The variable names are constructed by converting YAML keys to uppercase and replacing nested keys with double underscores (`__`).
- Arrays (lists) are represented using index numbers (`0`, `1`, etc.) in the environment variable names.
- All environment variable names should be prefixed with `MA__` to avoid conflicts with other environment variables.

## See also:

- [Mubmle Authenticator](https://gitlab.com/allianceauth/mumble-authenticator)
- [Mumble scripts](https://github.com/mumble-voip/mumble-scripts/tree/master)
- [ICE docs](https://doc.zeroc.com/ice/latest/)
