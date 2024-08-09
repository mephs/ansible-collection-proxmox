# mephs.proxmox

Ansible modules collection for managing Proxmox Virtual Environment.

## Tested with Ansible

Tested with the Ansible Core `>=2.15.0`, and the current development version of Ansible.

## External requirements

This collection requires the `proxmoxer` and `requests` python libraries.
To install these dependencies you have the following options:

1. Use the requirements.txt file to install all required packages:

    ```bash
    pip install -r requirements.txt
    ```

2. Alternatively, you can install the required packages directly:

    ```bash
    pip install requests "proxmoxer>=1.1.0"
    ```

## Included content

* `pve_role` module for managing PVE roles
* `pve_role_info` module for retrieve information about roles
* `pve_group` module for managing PVE groups
* `pve_group_info` module for retrieve information about groups

## Using this collection

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:

```bash
ansible-galaxy collection install mephs.proxmox
```

You can also include it in a `requirements.yml` file and install it
with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: mephs.proxmox
```

See [using Ansible collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more
details.

## License & Author

Created and maintained by Mikhail Vorontsov (@mephs) <mvorontsov@tuta.io>

GNU General Public License v3.0 or later

See [LICENSE](LICENSE) to see the full text.
