# -*- coding: utf-8 -*-

# Copyright (c) 2024, Mikhail Vorontsov (@RusMephist) <mvorontsov@tuta.io>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):
    # Common parameters for Proxmox VE modules
    DOCUMENTATION = r'''
options:
  pve_host:
    description:
      - Target host of the Proxmox VE cluster.
      - FQDN or IP Address.
      - You can use E(PROXMOX_HOST) environment variable.
    type: str
    required: true
    aliases: ['api_host']

  pve_port:
    description:
      - Target port for the connection.
      - You can use E(PROXMOX_PORT) environment variable.
    type: str
    default: 8006
    aliases: ['api_port']

  pve_user:
    description:
      - Specify the user for authentication.
      - You can use E(PROXMOX_USER) environment variable.
    type: str
    required: true
    aliases: ['api_user']

  pve_password:
    description:
      - Specify the password for authentication.
      - Either this or O(pve_token_id) must be specified.
      - You can use E(PROXMOX_PASSWORD) environment variable.
    type: str
    aliases: ['api_password']

  pve_token_id:
    description:
      - Specify the token ID.
      - Either this or O(pve_password) must be specified.
      - Should be used with O(pve_token_secret).
      - You can use E(PROXMOX_TOKEN) environment variable.
    type: str
    aliases: ['api_token_id', 'token_id']

  pve_token_secret:
    description:
      - Specify the token secret.
      - Should be used with O(pve_token_id).
      - You can use E(PROXMOX_SECRET) environment variable.
    type: str
    aliases: ['api_token_secret', 'token_secret']

  pve_validate_certs:
    description:
      - If V(false), SSL certificates will not be validated.
      - This should only be used on personally controlled sites using self-signed certificates.
    type: bool
    default: false
    aliases: ['api_validate_certs', 'validate_certs']

requirements: [ 'proxmoxer >= 1.1.0', 'requests' ]
'''
