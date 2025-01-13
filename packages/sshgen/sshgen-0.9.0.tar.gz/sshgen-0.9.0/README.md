# sshgen

SSH configuration generator based on your Ansible hosts YAML file.

Current version: v0.9.0

## Table of Contents

<!-- TOC -->
* [sshgen](#sshgen)
  * [Table of Contents](#table-of-contents)
  * [Features](#features)
  * [Installation](#installation)
    * [Using pip](#using-pip)
    * [Using pipx](#using-pipx)
  * [Usage](#usage)
  * [License](#license)
  * [Changelog](#changelog)
<!-- TOC -->

## Features

1. Generates a `config` file to merge with your existing SSH configuration or include as a separate `.conf` file (since v0.6.0).
2. Custom configuration for ssh-agent.
3. Custom SSH aliases for quick connections.
4. Skip selected hosts from results file.

## Installation

### Using pip

```shell
pip install --user git+https://github.com/pythoninja/sshgen@v0.9.0
```

Or

```shell
pip install --user sshgen
```

### Using pipx

```shell
pipx install git+https://github.com/pythoninja/sshgen@v0.9.0
```

Or just run without installing:

```shell
pipx run sshgen
```

[(Go to top)](#table-of-contents)

## Usage

Before using this tool, make sure you have an Ansible `hosts.yml` in your current working directory.

Consider the following example `hosts.yml` file, which defines 2 host groups with a total of 4 hosts:

```yaml
group1: # host_group
  hosts:
    host1: # host
      ansible_host: 127.0.0.1
      ansible_user: root
      _meta:
        _auth_type: IdentityAgent
        _auth_path: ~/.1password/agent.sock
        _aliases: [ "base", "another-alias" ]
        _skip: false

    host2:
      ansible_host: 127.0.0.2
      ansible_user: manager
      ansible_password:
      ansible_port: 19020
      _meta:
        _skip: true

group2:
  hosts:
    host3:
      ansible_host: 172.19.0.1
      ansible_user: postgres
      ansible_password:
      ansible_port: 19222

    host4:
        ansible_host: 172.99.99.99
        ansible_user: postgres
        _meta:
          _auth_type: IdentityAgent
          _auth_path: ~/.1password/agent.sock
          _aliases: [ "base", "another-alias" ]
          _skip: false
```

To use `sshgen`, you can either invoke it as a Python module using `python -m sshgen --help` or directly use the
command `sshgen --help`.

By default, `sshgen` looks for the `hosts.yml` file in your current working directory. To generate the SSH
configuration, run the following command:

```shell
sshgen generate
```

To display addition logs (verbose mode), add `--verbose` flag:

```
sshgen --verbose generate
```

Or use `SSHGEN_DEBUG=1` (`SSHGEN_VERBOSE=1`) environment variable (since v0.5.0):

```shell
SSHGEN_DEBUG=1 sshgen generate
```

After executing the command, you will see the following output:

```text
[2024-03-10 10:00:00] [INFO] - Generated SSH config file was saved to /my_dir/config
[2024-03-10 10:00:00] [INFO] - Total processed hosts: 3, total skipped hosts: 1
```

Check the file contents `cat /my_dir/config`:

```
Host host1 base another-alias # group1
    HostName 127.0.0.1
    User root
    Port 22
    IdentityAgent ~/.1password/agent.sock

Host host3  # group2
    HostName 172.19.0.1
    User postgres
    Port 19222
    IdentityFile ~/.ssh/ssh_key
    IdentitiesOnly yes

Host host4 postgres-server # group2
    HostName 172.99.99.99
    User postgres
    Port 22
    IdentityAgent ~/.1password/agent.sock
```

If you run using verbose mode, you should see additional information:

<details><summary>Verbose output example</summary>
<p>

```text
[2024-03-10 10:00:00] [DEBUG] - Loading ansible hosts file: /home/user/code/python/sshgen/examples/hosts.yml
[2024-03-10 10:00:00] [DEBUG] - Total hosts found (include skipped): 4
[2024-03-10 10:00:00] [DEBUG] - Using template file /home/user/code/python/sshgen/sshgen/templates/ssh_config.template to generate ssh config
[2024-03-10 10:00:00] [DEBUG] - Filtering hosts where _skip metafield was defined
[2024-03-10 10:00:00] [DEBUG] - Host host1 should be skipped: False
[2024-03-10 10:00:00] [DEBUG] - Host host2 should be skipped: True
[2024-03-10 10:00:00] [DEBUG] - Host host3 should be skipped: False
[2024-03-10 10:00:00] [DEBUG] - Host host4 should be skipped: False
[2024-03-10 10:00:00] [DEBUG] - Processing host1 from group group1
[2024-03-10 10:00:00] [DEBUG] - Adding SSH port 22 for host host1
[2024-03-10 10:00:00] [DEBUG] - Adding aliases ['base', 'another-alias'] for host host1
[2024-03-10 10:00:00] [DEBUG] - Adding custom auth methods for host host1
[2024-03-10 10:00:00] [DEBUG] - Processing host3 from group group2
[2024-03-10 10:00:00] [DEBUG] - Adding SSH port 19222 for host host3
[2024-03-10 10:00:00] [DEBUG] - Processing host4 from group group2
[2024-03-10 10:00:00] [DEBUG] - Adding SSH port 22 for host host4
[2024-03-10 10:00:00] [DEBUG] - Adding aliases ['base', 'another-alias'] for host host4
[2024-03-10 10:00:00] [DEBUG] - Adding custom auth methods for host host4
[2024-03-10 10:00:00] [INFO] - Generated SSH config file was saved to /home/user/code/python/sshgen/config
[2024-03-10 10:00:00] [DEBUG] - Skipped hosts list: 127.0.0.2
[2024-03-10 10:00:00] [INFO] - Total processed hosts: 3, total skipped hosts: 1
```

</p>
</details>

There are two ways to use the generated file:
1. Copy and insert the output into your `~/.ssh/config` file.
2. Copy file to the conf directory, e.g. `~/.ssh/config.d/00-custom.conf` (if it's not exist, create one).
Edit your `~/.ssh/config` and add `Include` directive **to the top**:

```
#### Custom configuration

Include ~/.ssh/config.d/*.conf

#### End of custom configuration
```

After that, you can use any of the defined aliases to SSH
into the corresponding hosts. For example, running `ssh base` will connect you to the host with the IP address 127.0.0.1
as the root user and utilizing 1password as your SSH agent.

For more examples, please refer to the [examples](https://github.com/pythoninja/sshgen/tree/master/examples) directory.

[(Go to top)](#table-of-contents)

## License

There are no specific requirements for usage and distribution. For more information, refer to
the [LICENSE](https://github.com/pythoninja/sshgen/blob/master/LICENSE).

[(Go to top)](#table-of-contents)

## Changelog

For the changelog, please see [CHANGELOG.md](https://github.com/pythoninja/sshgen/blob/master/CHANGELOG.md).

[(Go to top)](#table-of-contents)
