#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Mikhail Vorontsov

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: role

short_description: Manage Proxmox roles

version_added: 0.0.1

description:
  - Allows to add, modify or remove Proxmox roles via the Proxmox VE API.
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
    description:
      - If V(true), add the specified O(privileges) to the role.
      - If V(false), only specified O(privileges) will be added to the role,
        removing any other privileges.
    type: bool

  name:
    description: A name of the role.
    required: true
    type: str
    aliases: ['roleid']

  privileges:
    description:
      - List of Proxmox privileges assign to this role.
    type: list
    elements: str
    aliases: ['privs']

  state:
    description: Whether the role should be present or absent.
    type: str
    choices: ['present', 'absent']
    default: present

extends_documentation_fragment:
  - rusmephist.proxmox.proxmox.documentation

author:
  - Mikhail Vorontsov (@RusMephist)
'''

EXAMPLES = r'''
- name: Create an empty role
  rusmephist.proxmox.role:
    name: empty_role
    state: present
    pve_host: node1
    pve_user: root@pam
    pve_password: Secret123

- name: Create a role with given privileges
  rusmephist.proxmox.role:
    name: new_role
    state: present
    privileges:
      - VM.Backup
      - VM.Clone
      - VM.Snapshot
    pve_host: node1
    pve_user: root@pam
    pve_password: Secret123

- name: Update a role with given privileges
  rusmephist.proxmox.role:
    name: new_role
    state: present
    append: true
    privileges: VM.Snapshot.Rollback
    pve_host: node1
    pve_user: root@pam
    pve_password: Secret123

- name: Replace privileges in a role
  rusmephist.proxmox.role:
    name: new_role
    state: present
    append: false
    privileges: VM.Config.CPU, VM.Config.Disk, VM.Config.Memory, VM.Config.Network
    pve_host: node1
    pve_user: root@pam
    pve_password: Secret123

- name: Remove a role
  rusmephist.proxmox.role:
    name: new_role
    state: absent
    pve_host: node1
    pve_user: root@pam
    pve_password: Secret123

- name: Create a role on a host with a custom port
  rusmephist.proxmox.role:
    name: new_role
    state: present
    privileges: VM.Backup
    pve_host: node1
    pve_port: 35489
    pve_user: root@pam
    pve_password: Secret123
    pve_token_id: token
    pve_token_secret: f22f7c87-b26f-4697-b621-53b91344bf7c

- name: Create a role using a token
  rusmephist.proxmox.role:
    name: new_role
    state: present
    privileges: VM.Backup
    pve_host: node1
    pve_user: root@pam
    pve_token_id: token
    pve_token_secret: f22f7c87-b26f-4697-b621-53b91344bf7c
'''

RETURN = r'''
# TODO
# original_message:
#     description: The original name param that was passed in.
#     type: str
#     returned: always
#     sample: 'hello world'
# message:
#     description: The output message that the test module generates.
#     type: str
#     returned: always
#     sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text
from ..module_utils.proxmox import ProxmoxModule
from ..module_utils.proxmox import ansible_to_proxmox_bool
from ..module_utils.proxmox import check_list_match
from ..module_utils.proxmox import check_list_equal
from ..module_utils.proxmox import proxmox_auth_argument_spec
from ..module_utils.proxmox import proxmox_auth_required_one_of
from ..module_utils.proxmox import proxmox_auth_required_together


class ProxmoxRoleModule(ProxmoxModule):

    def __init__(self, module):
        super().__init__(module)

    def present_role(self, **result):
        privs = self.module.params.get('privileges')
        roleid = self.module.params.get('name')
        append = self.module.params.get('append')
        role = self.get_role(roleid, ignore_missing=True)

        result['privs'] = privs

        if role is None:
            result = self._create_role(**result)
        else:
            if not check_list_match(privs, list(role.keys())):
                result = self._update_role(**result)

            if not check_list_equal(privs, list(role.keys())) and not append:
                result = self._update_role(**result)

        return result

    def _create_role(self, **result):
        roleid = self.module.params.get('name')
        privs = self.module.params.get('privileges')

        result['changed'] = True

        if not self.module.check_mode:
            try:
                self.proxmox_api.access.roles.post(roleid=roleid, privs=privs)
            except Exception as e:
                result['changed'] = False
                self.module.fail_json(msg=to_text(e), **result)

        return result

    def _update_role(self, **result):
        roleid = self.module.params.get('name')
        privs = self.module.params.get('privileges')
        append = self.module.params.get('append')

        result['append'] = append
        result['changed'] = True

        if not self.module.check_mode:
            try:
                self.proxmox_api.access.roles(roleid).put(privs=privs, append=ansible_to_proxmox_bool(append))
            except Exception as e:
                result['changed'] = False
                self.module.fail_json(msg=to_text(e), **result)

        return result

    def absent_role(self, **result):
        roleid = self.module.params.get('name')
        role = self.get_role(roleid, ignore_missing=True)

        if role is not None:
            result['changed'] = True

            if not self.module.check_mode:
                try:
                    self.proxmox_api.access.roles(roleid).delete()
                except Exception as e:
                    self.module.fail_json(msg=to_text(e), **result)

        return result


def main():
    argument_spec = proxmox_auth_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True, aliases=['roleid']),
        privileges=dict(type='list', elements='str', aliases=['privs']),
        append=dict(type='bool', default=False),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=proxmox_auth_required_one_of(),
        required_together=proxmox_auth_required_together(),
        supports_check_mode=True,
    )

    result = {
        'changed': False,
        'roleid': module.params.get('name'),
        'state': module.params.get('state')
    }

    proxmox = ProxmoxRoleModule(module)
    state = module.params.get('state')

    if state == "absent":
        result = proxmox.absent_role(**result)
    else:
        result = proxmox.present_role(**result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
