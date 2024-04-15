# -*- coding: utf-8 -*-

# Copyright (c) Ansible project
# Copyright (c) 2024, Mikhail Vorontsov

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Common parameters for Proxmox VE modules
    DOCUMENTATION = r'''
options:
  api_host:
    description:
      - Specify the target host of the Proxmox VE cluster.
      - You can use E(PROXMOX_HOST) environment variable.
    type: str
    required: true
    aliases: ['api', 'host']

  api_user:
    description:
      - Specify the user to authenticate with.
      - You can use E(PROXMOX_USER) environment variable.
    type: str
    required: true
    aliases: ['user']

  api_password:
    description:
      - Specify the password to authenticate with.
      - You can use E(PROXMOX_PASSWORD) environment variable.
    type: str

  api_token_id:
    description:
      - Specify the token ID.
      - You can use E(PROXMOX_TOKEN) environment variable.
    type: str
    aliases: ['token_id', 'token']

  api_token_secret:
    description:
      - Specify the token secret.
      - You can use E(PROXMOX_SECRET) environment variable.
    type: str
    aliases: ['token_secret', 'secret']

  validate_certs:
    description:
      - If V(false), SSL certificates will not be validated.
      - This should only be used on personally controlled sites using self-signed certificates.
    type: bool
    default: false

requirements: [ 'proxmoxer >= 1.1.0', 'requests' ]
'''

    SELECTION = r'''
options:
  vmid:
    description:
      - Specifies the instance ID.
      - If not set the next available ID will be fetched from ProxmoxAPI.
    type: int

  node:
    description:
      - Proxmox VE node on which to operate.
      - Only required for O(state=present).
      - For every other states it will be autodiscovered.
    type: str

  pool:
    description:
      - Add the new VM to the specified pool.
    type: str
'''
