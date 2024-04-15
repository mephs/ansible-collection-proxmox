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
    For more details on permission management see U(https://pve.proxmox.com/wiki/User_Management#pveum_permission_management).

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
    description: List of Proxmox privileges assign to this role.
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
    api_host: node1
    api_user: root@pam
    api_password: Secret123

- name: Create a role with given privileges
  rusmephist.proxmox.role:
    name: role1
    state: present
    privileges:
      - VM.Backup
      - VM.Clone
      - VM.Snapshot
    api_host: node1
    api_user: root@pam
    api_password: Secret123

- name: Update a role with given privileges
  rusmephist.proxmox.role:
    name: role1
    state: present
    append: true
    privileges: VM.Snapshot.Rollback
    api_host: node1
    api_user: root@pam
    api_password: Secret123

- name: Replace privileges in a role
  rusmephist.proxmox.role:
    name: role1
    state: present
    privileges: VM.Config.CPU, VM.Config.Disk, VM.Config.Memory, VM.Config.Network
    api_host: node1
    api_user: root@pam
    api_token_id: token
    api_token_secret: f22f7c87-b26f-4697-b621-53b91344bf7c

- name: Remove a role
  rusmephist.proxmox.role:
    name: role1
    state: absent
    api_host: node1
    api_user: root@pam
    api_password: Secret123
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
from ansible_collections.rusmephist.proxmox.plugins.module_utils.proxmox import (
    ProxmoxModule,
    ansible_to_proxmox_bool,
    proxmox_auth_argument_spec
)


class ProxmoxRoleModule(ProxmoxModule):

    def is_role_existing(self, roleid):
        try:
            roles = self.proxmox_api.access.roles.get()
            for role in roles:
                if role['roleid'] == roleid:
                    return True
            return False
        except Exception as e:
            self.module.fail_json(msg="Unable to retrieve roles: {0}".format(e))

    def create_role(self, roleid, privs):
        if self.module.check_mode:
            return

        try:
            self.proxmox_api.access.roles.post(roleid=roleid, privs=privs)
        except Exception as e:
            self.module.fail_json(msg="Failed to create role with ID {0}: {1}".format(roleid, e))

    def update_role(self, roleid, privs, append):
        if self.module.check_mode:
            return

        try:
            self.proxmox_api.access.roles(roleid).put(privs=privs, append=append)
        except Exception as e:
            self.module.fail_json(msg="Failed to create role with ID {0}: {1}".format(roleid, e))

    def delete_role(self, roleid):
        if not self.is_role_existing(roleid):
            self.module.exit_json(changed=False, roleid=roleid, msg="Role {0} doesn't exist".format(roleid))

        if self.module.check_mode:
            return

        try:
            self.proxmox_api.access.roles(roleid).delete()
        except Exception as e:
            self.module.fail_json(msg="Failed to delete role with ID {0}: {1}".format(roleid, e))


def main():

    module_args = proxmox_auth_argument_spec()
    module_args.update(
        name=dict(type='str', required=True, aliases=['roleid']),
        privileges=dict(type='list', elements='str', aliases=['privs']),
        append=dict(type='bool'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[('api_password', 'api_token_secret')],
        required_together=[('api_token_id', 'api_token_secret')],
        required_by={'append': 'privileges'},
        supports_check_mode=True,
    )

    roleid = module.params['name']
    privs = module.params['privileges']
    append = ansible_to_proxmox_bool(module.params['append'])
    state = module.params['state']

    proxmox = ProxmoxRoleModule(module)

    if state == "present":
        if proxmox.is_role_existing(roleid):
            proxmox.update_role(roleid, privs, append)
            module.exit_json(changed=True, roleid=roleid, msg="Role {0} successfully updated".format(roleid))
        else:
            proxmox.create_role(roleid, privs)
            module.exit_json(changed=True, roleid=roleid, msg="Role {0} successfully created".format(roleid))
    else:
        proxmox.delete_role(roleid)
        module.exit_json(changed=True, roleid=roleid, msg="Role {0} successfully deleted".format(roleid))


if __name__ == '__main__':
    main()
