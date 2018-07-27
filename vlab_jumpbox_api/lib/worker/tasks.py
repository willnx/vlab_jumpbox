# -*- coding: UTF-8 -*-
"""
Entry point logic for available backend worker tasks
"""
from celery import Celery
from celery.utils.log import get_task_logger

from vlab_jumpbox_api.lib import const
from vlab_jumpbox_api.lib.worker import vmware


app = Celery('jumpbox', backend='rpc://', broker=const.VLAB_MESSAGE_BROKER)
logger = get_task_logger(__name__)
logger.setLevel(const.VLAB_JUMPBOX_LOG_LEVEL.upper())


@app.task(name='jumpbox.show')
def show(username):
    """Obtain basic information about a user's jumpbox

    :Returns: Dictionary

    :param username: The name of the user who wants info about their default gateway
    :type username: String
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        info = vmware.show_jumpbox(username)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
        resp['content'] = info
    return resp


@app.task(name='jumpbox.create')
def create(username, network):
    """Deploy a new jumpbox

    :Returns: Dictionary

    :param username: The name of the user who wants to create a new default gateway
    :type username: String

    :param network: The name of the network the jumpbox connects to
    :type network: string
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        resp['content'] = vmware.create_jumpbox(username, network)
    except ValueError as doh:
        logger.error('Task Failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    logger.info('Task complete')
    return resp


@app.task(name='jumpbox.delete')
def delete(username):
    """Destory the user's jumpbox

    :Returns: Dictionary

    :param username: The name of the user who wants to create a new default gateway
    :type username: String
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    try:
        logger.info('Task starting')
        info = vmware.delete_jumpbox(username)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
        resp['content'] = info
    return resp
