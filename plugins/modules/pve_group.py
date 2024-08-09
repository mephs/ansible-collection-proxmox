#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Mikhail Vorontsov (@mephs) <mvorontsov@tuta.io>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: pve_group
short_description: Manage Proxmox VE groups
description:
  - Allows to create, modify or remove Proxmox VE groups.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  comment:
    description: Comment of the group.
    type: str
    default: ''
  name:
    description: Name of the group to manage.
    required: true
    type: str
    aliases: ['groupid']
  state:
    description:
      - If V(present) and the group does not exist, creates it.
      - If V(present) and the group exists, does nothing or updates it.
      - If V(absent), removes the group.
    type: str
    choices: ['present', 'absent']
    default: present
extends_documentation_fragment:
  - mephs.proxmox.api_auth
  - mephs.proxmox.attributes
author:
  - Mikhail Vorontsov (@mephs)
'''

EXAMPLES = r'''
- name: Create a group
  mephs.proxmox.pve_group:
    name: group1
    state: present
    comment: Test group
    api_host: node1
    api_user: root@pam
    api_password: Secret123

- name: Update comment on the group
  mephs.proxmox.pve_group:
    name: group1
    state: present
    comment: Test group with updated comment
    api_host: node1
    api_user: root@pam
    api_password: Secret123

- name: Remove a group
  mephs.proxmox.pve_group:
    name: group1
    state: absent
    api_host: node1
    api_user: root@pam
    api_password: Secret123
'''

RETURN = r'''
state:
  description: State of the group.
  type: str
  returned: always
  sample: 'present'
group:
  description: Group current status.
  type: dict
  returned: always
  contains:
    comment:
      description: Comment of the group.
      returned: on create and update
      type: str
    groupid:
      description: Group name.
      returned: always
      type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text
from ..module_utils.proxmox import ProxmoxModule
from ..module_utils.common_args import proxmox_auth_argument_spec
from ..module_utils.common_args import proxmox_auth_required_one_of
from ..module_utils.common_args import proxmox_auth_required_together


class PVERoleModule(ProxmoxModule):

    def __init__(self, module):
        super().__init__(module)
        self.groupid = self.module.params.get('name')
        self.comment = self.module.params.get('comment')
        self.state = self.module.params.get('state')

    def _generate_output(self, changed=False):
        """
        Generate a structured output dictionary.

        This method creates an output dictionary containing the current state of the group,
        a boolean indicating whether the role was changed, and the group name. If the role
        state is 'present', it also includes the group comments.

        Parameters:
        - changed (bool): A flag indicating whether the role was changed. Defaults to False.

        Returns:
        - dict: A dictionary containing the group state, change status, and details.
        """
        output = {'changed': changed, 'state': self.state, 'group': {'groupid': self.groupid}}
        if self.state == 'present':
            output['group'].update(comment=self.comment)
        return output

    def _get_group(self, groupid):
        try:
            return self.proxmox_api.access.groups.get(groupid)
        except self.proxmoxer_exception:
            return None
        except Exception as e:
            self.module.fail_json(groupid=groupid, msg=to_text(e))

    def present_group(self):
        group = self._get_group(self.groupid)

        if group is None:
            return self._create_group()

        if not (not self.comment and group.get('comment') is None) and self.comment != group['comment']:
            return self._update_group()

        return self._generate_output(changed=False)

    def _create_group(self):
        if not self.module.check_mode:
            try:
                self.proxmox_api.access.groups.post(groupid=self.groupid, comment=self.comment)
            except Exception as e:
                self.module.fail_json(msg=to_text(e), groupid=self.groupid)

        return self._generate_output(changed=True)

    def _update_group(self):
        if not self.module.check_mode:
            try:
                self.proxmox_api.access.groups(self.groupid).put(comment=self.comment)
            except Exception as e:
                self.module.fail_json(msg=to_text(e), groupid=self.groupid)

        return self._generate_output(changed=True)

    def absent_group(self):
        group = self._get_group(self.groupid)

        if group is not None:
            if not self.module.check_mode:
                try:
                    self.proxmox_api.access.groups(self.groupid).delete()
                except Exception as e:
                    self.module.fail_json(msg=to_text(e), groupid=self.groupid)

            return self._generate_output(changed=True)

        return self._generate_output(changed=False)


def main():
    argument_spec = proxmox_auth_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True, aliases=['groupid']),
        comment=dict(type='str', default=''),
        state=dict(type='str', default='present', choices=['present', 'absent'])
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=proxmox_auth_required_one_of(),
        required_together=proxmox_auth_required_together(),
        supports_check_mode=True
    )

    proxmox = PVERoleModule(module)
    state = module.params.get('state')

    if state == 'absent':
        result = proxmox.absent_group()
    else:
        result = proxmox.present_group()

    module.exit_json(**result)


if __name__ == '__main__':
    main()
