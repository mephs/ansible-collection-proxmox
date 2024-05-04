#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Mikhail Vorontsov (@mephs) <mvorontsov@tuta.io>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: role

short_description: Manage Proxmox VE roles

version_added: 1.0.0

description:
  - Allows to add, modify or remove Proxmox VE roles.
  - For more details on permission management see
    U(https://pve.proxmox.com/wiki/User_Management#pveum_permission_management).

attributes:
  check_mode:
    support: full
    description: Can run in check_mode and return changed status prediction without modifying target

  diff_mode:
    support: none
    description: Will return details on what has changed (or possibly needs changing in check_mode), when in diff mode

options:
  append:
    description: Append defined privileges to existing ones instead of overwriting them.
    type: bool
    default: false

  privs:
    description:
      - List of Proxmox privileges assign to this role.
      - You can specify multiple privileges by separating them with commas C(VM.Config.CPU,VM.Config.Disk).
      - All available privileges are listed here
        U(https://pve.proxmox.com/wiki/User_Management#pveum_permission_management).
    type: list
    elements: str
    aliases: ['priv']

  roleid:
    description: Name of the role to manage.
    required: true
    type: str
    aliases: ['name']

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

author:
  - Mikhail Vorontsov (@mephs)
'''

EXAMPLES = r'''
- name: Create an empty role
  mephs.proxmox.role:
    roleid: empty_role
    state: present
    api_host: node1
    api_user: root@pam
    api_password: Secret123

- name: Create a role with given privileges
  mephs.proxmox.role:
    roleid: new_role
    state: present
    privs:
      - VM.Backup
      - VM.Clone
      - VM.Snapshot
    api_host: node1
    api_user: root@pam
    api_password: Secret123

- name: Add a privilege to a role
  mephs.proxmox.role:
    roleid: new_role
    state: present
    priv: VM.Snapshot.Rollback
    append: true
    api_host: node1
    api_user: root@pam
    api_password: Secret123

- name: Overwrite privileges in a role
  mephs.proxmox.role:
    roleid: new_role
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
  mephs.proxmox.role:
    name: new_role
    state: absent
    api_host: node1
    api_user: root@pam
    api_password: Secret123
'''

RETURN = r'''
append:
    description: Whether or not to append the new privileges.
    type: bool
    returned: on update
privs:
    description: List of privileges.
    type: list
    returned: always
    sample: ["VM.Config.CPU", "VM.Config.Memory"]
privs_current:
    description: List of privileges of role after update.
    type: list
    returned: on update
    sample: ["VM.Allocate", "VM.Config.CPU", "VM.Config.Memory"]
privs_previous:
    description: List of privileges of role before update.
    type: list
    returned: on update
    sample: ["VM.Allocate"]
roleid:
    description: Name of role.
    type: str
    returned: always
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


class ProxmoxRoleModule(ProxmoxModule):

    def __init__(self, module):
        super().__init__(module)
        self.roleid = self.module.params.get('roleid')
        self.privs = self.module.params.get('privs')
        self.append = self.module.params.get('append')

    def present_role(self):
        role = self.get_role(self.roleid, ignore_missing=True)

        if role is None:
            return self._create_role()

        old_privs = list(role.keys())
        new_privs = self.privs if not self.append else list(set(old_privs + self.privs))

        if self.append:
            update = not check_list_match(self.privs, old_privs)
        else:
            update = not check_list_equal(self.privs, old_privs)

        if update:
            return self._update_role(old_privs, new_privs)

        return {'changed': False, 'roleid': self.roleid, 'privs': self.privs, 'old_privs': old_privs,
                'new_privs': new_privs, 'append': self.append, 'msg': "role %s not changed" % self.roleid}

    def _create_role(self):
        if not self.module.check_mode:
            try:
                self.proxmox_api.access.roles.post(roleid=self.roleid, privs=list_to_string(self.privs))
            except Exception as e:
                self.module.fail_json(msg=to_text(e), roleid=self.roleid, privs=self.privs)

        return {'changed': True, 'roleid': self.roleid, 'privs': self.privs, 'msg': "role %s created" % self.roleid}

    def _update_role(self, old_privs, new_privs):
        if not self.module.check_mode:
            try:
                self.proxmox_api.access.roles(self.roleid).put(privs=list_to_string(self.privs),
                                                               append=ansible_to_proxmox_bool(self.append))
            except Exception as e:
                self.module.fail_json(msg=to_text(e), roleid=self.roleid, privs=self.privs, old_privs=old_privs,
                                      new_privs=new_privs, append=self.append)

        return {'changed': True, 'roleid': self.roleid, 'privs': self.privs, 'old_privs': old_privs,
                'new_privs': new_privs, 'append': self.append, 'msg': "role %s updated" % self.roleid}

    def absent_role(self):
        role = self.get_role(self.roleid, ignore_missing=True)

        if role is not None:
            if not self.module.check_mode:
                try:
                    self.proxmox_api.access.roles(self.roleid).delete()
                except Exception as e:
                    self.module.fail_json(msg=to_text(e), roleid=self.roleid)

            return {'changed': True, 'roleid': self.roleid, 'msg': "role %s deleted" % self.roleid}

        return {'changed': False, 'roleid': self.roleid, 'msg': "role %s not found" % self.roleid}


def main():
    argument_spec = proxmox_auth_argument_spec()
    argument_spec.update(
        roleid=dict(type='str', required=True, aliases=['name']),
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

    proxmox = ProxmoxRoleModule(module)
    state = module.params.get('state')

    if state == "absent":
        result = proxmox.absent_role()
    else:
        result = proxmox.present_role()

    module.exit_json(**result)


if __name__ == '__main__':
    main()
