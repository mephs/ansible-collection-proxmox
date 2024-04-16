# -*- coding: utf-8 -*-

# Copyright (c) 2020, Tristan Le Guern <tleguern at bouledef.eu>
# Copyright (c) 2024, Mikhail Vorontsov

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils.basic import env_fallback, missing_required_lib
from ansible.module_utils.compat.version import LooseVersion
import traceback


PROXMOXER_IMP_ERR = None


try:
    from proxmoxer import ProxmoxAPI
    from proxmoxer import __version__ as proxmoxer_version
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False
    PROXMOXER_IMP_ERR = traceback.format_exc()


def proxmox_auth_argument_spec():
    options = dict(
        pve_host=dict(type='str', fallback=(env_fallback, ['PROXMOX_HOST']), required=True, aliases=['api_host']),
        pve_port=dict(type='str', default='8006', fallback=(env_fallback, ['PROXMOX_PORT']), aliases=['api_port']),
        pve_user=dict(type='str', fallback=(env_fallback, ['PROXMOX_USER']), required=True, aliases=['api_user']),
        pve_password=dict(type='str', fallback=(env_fallback, ['PROXMOX_PASSWORD']), no_log=True, aliases=['api_password']),
        pve_token_id=dict(type='str', fallback=(env_fallback, ['PROXMOX_TOKEN']), no_log=False, aliases=['api_token_id', 'token_id']),
        pve_token_secret=dict(type='str', fallback=(env_fallback, ['PROXMOX_SECRET']), no_log=True, aliases=['api_token_secret', 'token_secret']),
        pve_validate_certs=dict(type='bool', default=False, aliases=['api_validate_certs', 'validate_certs'])
    )
    return options


def proxmox_to_ansible_bool(value):
    '''Convert Proxmox representation of a boolean to be ansible-friendly'''
    return True if value == 1 else False


def ansible_to_proxmox_bool(value):
    '''Convert Ansible representation of a boolean to be proxmox-friendly'''
    if value is None:
        return None

    if not isinstance(value, bool):
        raise ValueError("%s must be of type bool not %s" % (value, type(value)))

    return 1 if value else 0


class ProxmoxModule(object):
    """Base class for Proxmox modules"""
    def __init__(self, module):
        if not HAS_PROXMOXER:
            module.fail_json(msg=missing_required_lib('proxmoxer'), exception=PROXMOXER_IMP_ERR)

        self.module = module
        self.proxmoxer_version = proxmoxer_version
        self.proxmox_api = self._connect()
        # Test token validity
        try:
            self.proxmox_api.version.get()
        except Exception as e:
            module.fail_json(msg='%s' % e, exception=traceback.format_exc())

    def _connect(self):
        api_host = self.module.params['pve_host']
        api_port = self.module.params['pve_port']
        api_user = self.module.params['pve_user']
        api_password = self.module.params['pve_password']
        api_token_id = self.module.params['pve_token_id']
        api_token_secret = self.module.params['pve_token_secret']
        validate_certs = self.module.params['pve_validate_certs']

        auth_args = {'user': api_user}
        if api_password:
            auth_args['password'] = api_password
        else:
            if self.proxmoxer_version < LooseVersion('1.1.0'):
                self.module.fail_json('Using "token_name" and "token_value" require proxmoxer >= 1.1.0')
            auth_args['token_name'] = api_token_id
            auth_args['token_value'] = api_token_secret

        try:
            return ProxmoxAPI(api_host, port=api_port, verify_ssl=validate_certs, **auth_args)
        except Exception as e:
            self.module.fail_json(msg='%s' % e, exception=traceback.format_exc())
