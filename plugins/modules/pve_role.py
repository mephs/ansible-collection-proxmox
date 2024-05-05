#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Mikhail Vorontsov (@mephs) <mvorontsov@tuta.io>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: pve_role
short_description: Manage Proxmox VE roles
description:
  - Allows to add, modify or remove Proxmox VE roles.
  - For more details on permission management see
    U(https://pve.proxmox.com/wiki/User_Management#pveum_permission_management).
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  append:
    description: Append defined privileges to existing ones instead of overwriting them.
    type: bool
    default: false
  name:
    description: Name of the role to manage.
    required: true
    type: str
    aliases: ['roleid']
  privs:
    description:
      - List of Proxmox privileges assign to this role.
      - You can specify multiple privileges by separating them with commas C(VM.Config.CPU,VM.Config.Disk).
      - All available privileges are listed here
        U(https://pve.proxmox.com/wiki/User_Management#pveum_permission_management).
    type: list
    elements: str
    aliases: ['priv']
  state:
    description:
      - If V(present) and the role does not exist, creates it.
      - If V(present) and the role exists, does nothing or updates its privileges.
      - If V(absent), removes the role.
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
- name: Create an empty role
  mephs.proxmox.pve_role:
    name: empty_role
    state: present
    api_host: node1
    api_user: root@pam
    api_password: Secret123

- name: Create a role with given privileges
  mephs.proxmox.pve_role:
    name: new_role
    state: present
    privs:
      - VM.Backup
      - VM.Clone
      - VM.Snapshot
    api_host: node1
    api_user: root@pam
    api_password: Secret123

- name: Add a privilege to a role
  mephs.proxmox.pve_role:
    name: new_role
    state: present
    priv: VM.Snapshot.Rollback
    append: true
    api_host: node1
    api_user: root@pam
    api_password: Secret123

- name: Overwrite privileges in a role
  mephs.proxmox.pve_role:
    name: new_role
    state: present
    privs:
      - VM.Config.CPU
      - VM.Config.Disk
      - VM.Config.Memory
      - VM.Config.Network
    append: false
    api_host: node1
    api_user: root@pam
    api_password: Secret123

- name: Remove a role
  mephs.proxmox.pve_role:
    name: new_role
    state: absent
    api_host: node1
    api_user: root@pam
    api_password: Secret123
'''

RETURN = r'''
state:
  description: State of the role.
  type: str
  returned: always
  sample: 'present'
role:
  description: Role current status.
  type: dict
  returned: always
  contains:
    privs:
      description: List of privileges on the role.
      type: list
      elements: str
      returned: on create and update
    roleid:
      description: Role name.
      returned: always
      type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text
from ..module_utils.proxmox import ProxmoxModule
from ..module_utils.proxmox import ansible_to_proxmox_bool
from ..module_utils.proxmox import check_list_match
from ..module_utils.proxmox import check_list_equal
from ..module_utils.proxmox import list_to_string
from ..module_utils.common_args import proxmox_auth_argument_spec
from ..module_utils.common_args import proxmox_auth_required_one_of
from ..module_utils.common_args import proxmox_auth_required_together


class PVERoleModule(ProxmoxModule):

    def __init__(self, module):
        super().__init__(module)
        self.roleid = self.module.params.get('name')
        self.privs = self.module.params.get('privs')
        self.append = self.module.params.get('append')
        self.state = self.module.params.get('state')

    def generate_output(self, changed=False):
        """
        Generate a structured output dictionary.

        This method constructs an output dictionary that includes the current state of the role,
        a boolean indicating whether the role was changed, and the role name. If the role
        state is 'present', it also includes the role privileges.

        Parameters:
        - changed (bool): A flag indicating whether the role was changed. Defaults to False.

        Returns:
        - dict: A dictionary containing the role state, change status, and details.
        """
        output = {'changed': changed, 'state': self.state, 'role': {'roleid': self.roleid}}
        if self.state == 'present':
            output['role'].update(privs=self.get_role(self.roleid).keys())
        return output

    def get_role(self, roleid):
        try:
            return self.proxmox_api.access.roles.get(roleid)
        except self.proxmoxer_exception:
            return None
        except Exception as e:
            self.module.fail_json(roleid=roleid, msg=to_text(e))

    def present_role(self):
        role = self.get_role(self.roleid)

        if role is None:
            return self._create_role()

        if self.append:
            update = not check_list_match(self.privs, list(role.keys()))
        else:
            update = not check_list_equal(self.privs, list(role.keys()))

        if update:
            return self._update_role()

        return self.generate_output(changed=False)

    def _create_role(self):
        if not self.module.check_mode:
            try:
                self.proxmox_api.access.roles.post(roleid=self.roleid, privs=list_to_string(self.privs))
            except Exception as e:
                self.module.fail_json(msg=to_text(e), roleid=self.roleid)

        return self.generate_output(changed=True)

    def _update_role(self):
        if not self.module.check_mode:
            try:
                self.proxmox_api.access.roles(self.roleid).put(
                    privs=list_to_string(self.privs),
                    append=ansible_to_proxmox_bool(self.append)
                )
            except Exception as e:
                self.module.fail_json(msg=to_text(e), roleid=self.roleid)

        return self.generate_output(changed=True)

    def absent_role(self):
        role = self.get_role(self.roleid)

        if role is not None:
            if not self.module.check_mode:
                try:
                    self.proxmox_api.access.roles(self.roleid).delete()
                except Exception as e:
                    self.module.fail_json(msg=to_text(e), roleid=self.roleid)

            return self.generate_output(changed=True)

        return self.generate_output(changed=False)


def main():
    argument_spec = proxmox_auth_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True, aliases=['roleid']),
        privs=dict(type='list', elements='str', default=[], aliases=['priv']),
        append=dict(type='bool', default=False),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=proxmox_auth_required_one_of(),
        required_together=proxmox_auth_required_together(),
        supports_check_mode=True,
    )

    proxmox = PVERoleModule(module)
    state = module.params.get('state')

    if state == "absent":
        result = proxmox.absent_role()
    else:
        result = proxmox.present_role()

    module.exit_json(**result)


if __name__ == '__main__':
    main()
