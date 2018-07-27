# -*- coding: UTF-8 -*-
"""Business logic for backend worker tasks"""
import time
import os.path
from celery.utils.log import get_task_logger
from vlab_inf_common.vmware import vCenter, Ova, vim, virtual_machine, consume_task

from vlab_jumpbox_api.lib import const


logger = get_task_logger(__name__)
logger.setLevel(const.VLAB_JUMPBOX_LOG_LEVEL.upper())

COMPONENT_NAME = 'jumpBox'


def show_jumpbox(username):
    """Obtain basic information about the user's Jumpbox

    :Returns: Dictionary

    :param username: The user requesting info about their jumpbox
    :type username: String
    """
    info = {}
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        for vm in folder.childEntity:
            if vm.name == COMPONENT_NAME:
                info = virtual_machine.get_info(vcenter, vm)
                break
    return info


def delete_jumpbox(username):
    """Unregister and destroy the user's jumpbox

    :Returns: None

    :param username: The user who wants to delete their jumpbox
    :type username: String
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        for entity in folder.childEntity:
            if entity.name == COMPONENT_NAME:
                logger.debug('powering off VM')
                virtual_machine.power(entity, state='off')
                delete_task = entity.Destroy_Task()
                logger.debug('blocking while VM is being destroyed')
                consume_task(delete_task)


def create_jumpbox(username, network, image_name='jumpBox-Ubuntu18.04.ova'):
    """Make a new jumpbox so a user can connect to their lab

    :Returns: Dictionary

    :param username: The user who wants to delete their jumpbox
    :type username: String

    :param network: The name of the network the jumpbox connects to
    :type network: string
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        ova = Ova(os.path.join(const.VLAB_JUMPBOX_IMAGES_DIR, image_name))
        try:
            network_map = vim.OvfManager.NetworkMapping()
            network_map.name = ova.networks[0]
            try:
                network_map.network = vcenter.networks[network]
            except KeyError:
                raise ValueError('No such network named {}'.format(network))
            the_vm = virtual_machine.deploy_from_ova(vcenter, ova, [network_map],
                                                     username, 'jumpBox', logger)
        finally:
            ova.close()
        _setup_jumpbox(vcenter, the_vm, username)
        # VMTools will be ready long before the full network stack is up.
        # Pause for a moment here so we can return an IP
        time.sleep(70)
        return virtual_machine.get_info(vcenter, the_vm)


def _setup_jumpbox(vcenter, the_vm, username):
    """Configure the Jumpbox for the end user

    :Returns: None

    :param vcenter: The instantiated connection to vCenter
    :type vcenter: vlab_inf_common.vmware.vCenter

    :param the_vm: The new gateway
    :type the_vm: vim.VirtualMachine
    """
    # Add the note about the type & version of Jumpbox being used
    spec = vim.vm.ConfigSpec()
    spec.annotation = 'ubuntu=18.04'
    task = the_vm.ReconfigVM_Task(spec)
    consume_task(task)
    # Create an admin user with the same username as the end-user
    cmd = '/usr/bin/sudo'
    # SHA 512 version of the letter 'a' (plus the $6$ to denote SHA 512)
    pw = '$6$qM5mj4O0$x8l6R4T4sH1HJgYt9dw3n2pYO8E0Rs/sqlCfts5/p8o8ZK8aBjfHRlh37xnxIfPZBp.ErfBgnSJcauzP2mxBx.'
    args = "/usr/sbin/useradd --shell /bin/bash --password '{1}' --create-home --groups sudo --home-dir /home/{0} {0} ".format(username, pw)
    result = virtual_machine.run_command(vcenter,
                                         the_vm,
                                         cmd,
                                         user='administrator',
                                         password='a',
                                         arguments=args)
    if result.exitCode:
        error = 'Failed to create user {} in newly deployed jumpbox'.format(username)
        raise RuntimeError(error)
    # Disable the administrator account so peeps don't use it
    # nothing will hash to the letter "a" this is pretty effective account disabling
    cmd2 = '/usr/bin/sudo'
    args2 = "/usr/sbin/usermod --password 'a' administrator"

    # once the account is disabled, all attempts to check the status will also fail
    virtual_machine.run_command(vcenter,
                                the_vm,
                                cmd,
                                user='administrator',
                                password='a',
                                arguments=args)
