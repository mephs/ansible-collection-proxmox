#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Mikhail Vorontsov (@mephs) <mvorontsov@tuta.io>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: pve_group_info
short_description: Retrieve information about Proxmox VE groups
description:
  - Retrieve information about Proxmox VE groups.
options:
  name:
    description: Name of the group to be retrieved.
    type: str
    aliases: ['groupid']
extends_documentation_fragment:
  - mephs.proxmox.api_auth
  - mephs.proxmox.attributes
  - mephs.proxmox.attributes.info_module
author:
  - Mikhail Vorontsov (@mephs)
'''

EXAMPLES = r'''
- name: Get all proxmox groups
  mephs.proxmox.pve_group_info:
    api_host: node1
    api_user: root@pam
    api_password: Secret123
  register: _proxmox_groups
  
- name: Get the group details
  mephs.proxmox.pve_group_info:
    name: custom_group
    api_host: node1
    api_user: root@pam
    api_password: Secret123
  register: _custom_group_details
'''

RETURN = r'''
groups:
  description: List of groups.
  type: list
  elements: dict
  returned: always
  contains:
    comment:
      description:
        - Comment of the group.
        - Returns if added to a group.
      returned: on success
      type: str
    groupid:
      description:
        - Group name.
        - Returns V(null) if the group does not exist.
      returned: on success
      type: str
    users:
      description:
        - List of users in the group.
        - Returns if the group does exist.
      type: list
      elements: str
      returned: on success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text
from ..module_utils.proxmox import ProxmoxModule
from ..module_utils.common_args import proxmox_auth_argument_spec
from ..module_utils.common_args import proxmox_auth_required_one_of
from ..module_utils.common_args import proxmox_auth_required_together


class PVEGroupInfoModule(ProxmoxModule):

    def __init__(self, module):
        super().__init__(module)

    @staticmethod
    def generate_output(groupid=None, users=None, comment=None, groups=None):
        """
        Generate a structured output dictionary.

        Args:
        - groupid (str): Group name.
        - users (list): List of users in the group.
        - comment (str): Comment of the group.
        - groups (list): List of groups.

        Returns:
        - dict: A dictionary containing the groups.
        """
        if users is None:
            users = []

        if groups is not None:
            return {'groups': groups}

        if groupid is None:
            return {'groups': [{'groupid': None}]}

        if comment is None:
            return {'groups': [{'groupid': groupid, 'users': users}]}

        return {'groups': [{'groupid': groupid, 'users': users, 'comment': comment}]}

    def get_group(self, groupid):
        try:
            group = self.proxmox_api.access.groups.get(groupid)
            group['users'] = group.pop('members')
            return self.generate_output(groupid, **group)

        # Return None if group doesn't exist
        except self.proxmoxer_exception:
            return self.generate_output()

        # Fail with exception message
        except Exception as e:
            self.module.fail_json(groupid=groupid, msg=to_text(e))

    def get_all_groups(self):
        try:
            groups = self.proxmox_api.access.groups.get()
            return self.generate_output(groups=[group for group in groups])
        except Exception as e:
            self.module.fail_json(msg=to_text(e))


def main():
    argument_spec = proxmox_auth_argument_spec()
    argument_spec.update(
        name=dict(type='str', aliases=['groupid']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=proxmox_auth_required_one_of(),
        required_together=proxmox_auth_required_together(),
        supports_check_mode=True,
    )

    proxmox = PVEGroupInfoModule(module)
    groupid = module.params.get('name')

    if groupid:
        result = proxmox.get_group(groupid)
    else:
        result = proxmox.get_all_groups()

    module.exit_json(**result)


if __name__ == '__main__':
    main()
