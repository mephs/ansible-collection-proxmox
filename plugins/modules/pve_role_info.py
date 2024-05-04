#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Mikhail Vorontsov (@mephs) <mvorontsov@tuta.io>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: pve_role_info
short_description: 
description:
  - 
options:
  name:
    description: Name of the role to manage.
    required: true
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
- name: Create an empty role
  mephs.proxmox.pve_role_info:
    roleid: empty_role
    state: present
    api_host: node1
    api_user: root@pam
    api_password: Secret123
'''

RETURN = r'''
name:
    description: Name of role.
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text
from ..module_utils.proxmox import ProxmoxModule
from ..module_utils.proxmox import proxmox_to_ansible_bool
from ..module_utils.proxmox import string_to_list
from ..module_utils.proxmox import remap_dictionary
from ..module_utils.common_args import proxmox_auth_argument_spec
from ..module_utils.common_args import proxmox_auth_required_one_of
from ..module_utils.common_args import proxmox_auth_required_together


class PVERoleInfoModule(ProxmoxModule):

    def __init__(self, module):
        super().__init__(module)

    def get_role(self, roleid):
        try:
            privs = self.proxmox_api.access.roles.get(roleid)
            return {'roles': [{'name': roleid, 'privs': privs.keys()}]}
        except Exception as e:
            self.module.fail_json(roleid=roleid, msg=to_text(e))

    def get_all_roles(self):
        try:
            roles = self.proxmox_api.access.roles.get()
            return {'roles': [self._ansible_format(role) for role in roles]}
        except Exception as e:
            self.module.fail_json(msg=to_text(e))

    @staticmethod
    def _ansible_format(role):
        roles_map = {'roleid': 'name'}
        role = remap_dictionary(role, roles_map)

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
