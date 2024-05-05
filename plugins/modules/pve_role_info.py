#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Mikhail Vorontsov (@mephs) <mvorontsov@tuta.io>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: pve_role_info
short_description: Retrieve information about Proxmox VE roles
description:
  - Retrieve information about Proxmox VE roles.
options:
  name:
    description: Name of the role to be retrieved.
    type: str
    aliases: ['roleid']
extends_documentation_fragment:
  - mephs.proxmox.api_auth
  - mephs.proxmox.attributes
  - mephs.proxmox.attributes.info_module
author:
  - Mikhail Vorontsov (@mephs)
'''

EXAMPLES = r'''
- name: Get all proxmox roles
  mephs.proxmox.pve_role_info:
    api_host: node1
    api_user: root@pam
    api_password: Secret123
  register: _proxmox_roles
  
- name: Get the role details
  mephs.proxmox.pve_role_info:
    name: custom_role
    api_host: node1
    api_user: root@pam
    api_password: Secret123
  register: _custom_role_details
'''

RETURN = r'''
roles:
  description: List of roles.
  type: list
  elements: dict
  returned: always
  contains:
    privs:
      description:
        - List of privileges on the role.
        - Returns V(null) if the role does not exist.
      type: list
      elements: str
      returned: on success
    roleid:
      description:
        - Role name.
        - Returns V(null) if the role does not exist.
      returned: on success
      type: str
    special:
      description:
        - Predefined role flag.
        - Returns if O(name) is not specified.
      returned: on success
      type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text
from ..module_utils.proxmox import ProxmoxModule
from ..module_utils.proxmox import proxmox_to_ansible_bool
from ..module_utils.proxmox import string_to_list
from ..module_utils.common_args import proxmox_auth_argument_spec
from ..module_utils.common_args import proxmox_auth_required_one_of
from ..module_utils.common_args import proxmox_auth_required_together


class PVERoleInfoModule(ProxmoxModule):

    def __init__(self, module):
        super().__init__(module)

    @staticmethod
    def generate_output(roleid=None, privs=None, roles=None):
        """
        Generate a structured output dictionary.

        If roles is provided, it is used directly. Otherwise, a single role
        dictionary is constructed using roleid and privs.

        Parameters:
        - roleid (str): The role name.
        - privs (list): The privileges of a role.
        - roles (list): A list of role dictionaries.

        Returns:
        - dict: A dictionary containing the roles.
        """
        if roles is None:
            output = {'roles': [{'roleid': roleid, 'privs': privs}]}
        else:
            output = {'roles': roles}

        return output

    def get_role(self, roleid):
        try:
            privs = self.proxmox_api.access.roles.get(roleid)
            return self.generate_output(roleid, privs.keys())
        except self.proxmoxer_exception:
            return self.generate_output()
        except Exception as e:
            self.module.fail_json(roleid=roleid, msg=to_text(e))

    def get_all_roles(self):
        try:
            roles = self.proxmox_api.access.roles.get()
            return self.generate_output(roles=[self._ansible_format(role) for role in roles])
        except Exception as e:
            self.module.fail_json(msg=to_text(e))

    @staticmethod
    def _ansible_format(role):
        if 'special' in role:
            role['special'] = proxmox_to_ansible_bool(role['special'])
        if 'privs' in role:
            role['privs'] = string_to_list(role['privs'])

        return role


def main():
    argument_spec = proxmox_auth_argument_spec()
    argument_spec.update(
        name=dict(type='str', aliases=['roleid'])
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=proxmox_auth_required_one_of(),
        required_together=proxmox_auth_required_together(),
        supports_check_mode=True,
    )

    proxmox = PVERoleInfoModule(module)
    roleid = module.params.get('name')

    if roleid:
        result = proxmox.get_role(roleid)
    else:
        result = proxmox.get_all_roles()

    module.exit_json(**result)


if __name__ == '__main__':
    main()
