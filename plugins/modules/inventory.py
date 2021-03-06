#!/usr/bin/python
# -*- coding: utf-8 -*-
# © 2022 BNC Business Network Communications AG
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible module to interact with Semaphore's inventories
"""

from __future__ import absolute_import, division, print_function


# pylint: disable=invalid-name
__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.0",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: inventory
short_description: Ansible module to interact with Semaphore's inventories
description:
  - Creates, updates or removes inventory from Semaphore's project
author:
  - Alexandre Georges <alexandre.georges@bnc.ch> (@mageo)
options:
  type:
    type: str
    description: Type of inventory
    required: true
    choices:
      - static
      - file
  inventory:
    type: str
    description: Content of inventory or path to inventory file
    required: True
extends_documentation_fragment:
  - bnc.semaphore.component
  - bnc.semaphore.project_component
"""

EXAMPLES = r"""
---
# Creates a file inventory in project with ID 1
- name: Create inventory
  bnc.semaphore.inventory:
    name: Test inventory
    state: present
    url: http://localhost:3000/api
    token: XXXX
    type: file
    inventory: /tmp/inventory.yml
"""

# pylint: disable=import-error,wrong-import-position
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bnc.semaphore.plugins.module_utils.inventory import (
    SemaphoreInventory,
)


def main():
    """
    Main function
    """

    # Ansible module
    module = AnsibleModule(
        argument_spec=SemaphoreInventory.argument_spec
    )

    # Defer to project class
    semaphore = SemaphoreInventory(module)
    semaphore.handle()


if __name__ == "__main__":
    main()
