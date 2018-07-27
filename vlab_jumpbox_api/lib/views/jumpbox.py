# -*- coding: UTF-8 -*-
"""
This module defines the RESTful API for working with the jumpbox in your lab
"""
import ujson
from flask import current_app
from flask_classy import request
from vlab_inf_common.views import TaskView
from vlab_inf_common.vmware import vCenter, vim
from vlab_api_common import describe, get_logger, requires, validate_input


from vlab_jumpbox_api.lib import const


logger = get_logger(__name__, loglevel=const.VLAB_JUMPBOX_LOG_LEVEL)


class JumpboxView(TaskView):
    """API end point for creating/deleting showing info about your jumpbox"""
    route_base = '/api/1/inf/jumpbox'
    DELETE_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
                     "description": "Destroy your jumpbox"
                    }
    GET_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
                  "description": "Obtain information about your jump box"
                 }
    POST_SCHEMA = { "$schema": "http://json-schema.org/draft-04/schema#",
                    "type": "object",
                    "description": "Create a new Jumpbox",
                    "properties": {
                        "network": {
                            "description": "The name of the network the jumpbox connects to",
                            "type": "string"
                        }
                    },
                    "required": ["network"]
                  }

    @requires(verify=False)
    @describe(post=POST_SCHEMA, delete=DELETE_SCHEMA, get_args=GET_SCHEMA)
    def get(self, *args, **kwargs):
        """Obtain a info about the jumpbox a user owns"""
        username = kwargs['token']['username']
        resp = {'user' : username}
        task = current_app.celery_app.send_task('jumpbox.show', [username])
        resp['content'] = {'task-id': task.id}
        return ujson.dumps(resp), 200

    @requires(verify=False) # XXX remove verify=False before commit
    @validate_input(schema=POST_SCHEMA)
    def post(self, *args, **kwargs):
        """Create a new gateway"""
        username = kwargs['token']['username']
        resp = {'user' : username}
        network = kwargs['body']['network']
        task = current_app.celery_app.send_task('jumpbox.create', [username, network])
        resp['content'] = {'task-id': task.id}
        return ujson.dumps(resp), 200

    @requires(verify=False) # XXX remove verify=False before commit
    def delete(self, *args, **kwargs):
        """Delete a gateway"""
        username = kwargs['token']['username']
        resp = {'user' : username}
        task = current_app.celery_app.send_task('jumpbox.delete', [username])
        resp['content'] = {'task-id': task.id}
        return ujson.dumps(resp), 200
