# -*- coding: UTF-8 -*-
"""
A suite of tests for the functions in vmware.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vlab_jumpbox_api.lib.worker import vmware


class TestVMware(unittest.TestCase):
    """A set of test cases for the vmware.py module"""
    @classmethod
    def setUpClass(cls):
        vmware.logger = MagicMock()

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'vCenter')
    def test_show_jumpbox(self, fake_vCenter, fake_get_info):
        """``show_jumpbox`` returns a dictionary when everything works as expected"""
        fake_vm = MagicMock()
        fake_vm.name = 'jumpBox'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'worked': True}

        output = vmware.show_jumpbox(username='alice')
        expected = {'worked': True}

        self.assertEqual(output, expected)

    @patch.object(vmware, 'vCenter')
    def test_show_jumpbox_nothing(self, fake_vCenter):
        """``show_jumpbox`` returns an empty dictionary no jumpbox is found"""
        output = vmware.show_jumpbox(username='alice')
        expected = {}

        self.assertEqual(output, expected)

    @patch.object(vmware, 'time') # so tests run faster
    @patch.object(vmware, 'Ova')
    @patch.object(vmware, '_setup_jumpbox')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'vCenter')
    def test_create_jumpbox(self, fake_vCenter, fake_deploy_from_ova, fake_get_info,
            fake_setup_jumpbox, fake_Ova, fake_time):
        """``create_jumpbox`` returns the new jumpbox's info when everything works"""
        fake_Ova.return_value.networks = ['vLabNetwork']
        fake_vCenter.return_value.__enter__.return_value.networks = {'someNetwork': vmware.vim.Network(moId='asdf')}
        fake_get_info.return_value = {'worked' : True}

        output = vmware.create_jumpbox(username='alice',
                                       network='someNetwork')
        expected = {'worked': True}

        self.assertEqual(output, expected)

    @patch.object(vmware, 'time') # so tests run faster
    @patch.object(vmware, 'Ova')
    @patch.object(vmware, '_setup_jumpbox')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'vCenter')
    def test_create_jumpbox_valueError(self, fake_vCenter, fake_deploy_from_ova, fake_get_info,
            fake_setup_jumpbox, fake_Ova, fake_time):
        """``create_jumpbox`` raises ValueError if the requested network does not exist"""
        fake_Ova.return_value.networks = ['vLabNetwork']
        fake_vCenter.return_value.__enter__.return_value.networks = {'theNetworks': vmware.vim.Network(moId='asdf')}
        fake_get_info.return_value = {'worked' : True}

        with self.assertRaises(ValueError):
            vmware.create_jumpbox(username='alice', network='someNetwork')

    @patch.object(vmware, 'consume_task')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'vCenter')
    def test_delete_jumpbox(self, fake_vCenter, fake_power, fake_consume_task):
        """``delete_jumpbox`` powers off the VM then deletes it"""
        fake_vm = MagicMock()
        fake_vm.name = 'jumpBox'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder

        vmware.delete_jumpbox(username='alice')

        self.assertTrue(fake_power.called)
        self.assertTrue(fake_vm.Destroy_Task.called)

    @patch.object(vmware, 'consume_task')
    @patch.object(vmware.virtual_machine, 'run_command')
    def test_setup_jumpbox(self, fake_run_command, fake_consume_task):
        """``_setup_jumpbox`` returns None when everything works as expected"""
        fake_vcenter = MagicMock()
        fake_vm = MagicMock()
        fake_result = MagicMock()
        fake_result.exitCode = 0
        fake_run_command.return_value = fake_result

        result = vmware._setup_jumpbox(username='alice', vcenter=fake_vcenter, the_vm=fake_vm)
        expected = None

        self.assertEqual(result, expected)

    @patch.object(vmware, 'consume_task')
    @patch.object(vmware.virtual_machine, 'run_command')
    def test_setup_jumpbox_failure(self, fake_run_command, fake_consume_task):
        """``_setup_jumpbox`` Raises RuntimeError if unable to configure the VM"""
        fake_vcenter = MagicMock()
        fake_vm = MagicMock()
        fake_result = MagicMock()
        fake_result.exitCode = 1
        fake_run_command.return_value = fake_result

        with self.assertRaises(RuntimeError):
            vmware._setup_jumpbox(username='alice', vcenter=fake_vcenter, the_vm=fake_vm)


if __name__ == '__main__':
    unittest.main()
