from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import env_fallback

__metaclass__ = type


def proxmox_auth_argument_spec():
    options = dict(
        api_host=dict(type='str', fallback=(env_fallback, ['PROXMOX_HOST']), required=True),
        api_port=dict(type='str', default='8006', fallback=(env_fallback, ['PROXMOX_PORT'])),
        api_user=dict(type='str', fallback=(env_fallback, ['PROXMOX_USER']), required=True),
        api_password=dict(type='str', fallback=(env_fallback, ['PROXMOX_PASSWORD']), no_log=True),
        api_token_id=dict(type='str', fallback=(env_fallback, ['PROXMOX_TOKEN']), no_log=False,
                          aliases=['token_id']),
        api_token_secret=dict(type='str', fallback=(env_fallback, ['PROXMOX_SECRET']), no_log=True,
                              aliases=['token_secret']),
        api_validate_certs=dict(type='bool', default=False, aliases=['validate_certs'])
    )
    return options


def proxmox_auth_required_one_of():
    return [('api_password', 'api_token_secret')]


def proxmox_auth_required_together():
    return [('api_token_id', 'api_token_secret')]
