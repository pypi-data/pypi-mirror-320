#!/usr/bin/env python
from dataclasses import dataclass, field

from sshgen.models.metafields import MetaFieldsModel


@dataclass
class HostModel:
    host: str
    host_group: str
    ansible_host: str
    ansible_user: str
    ansible_port: int = 22
    meta_fields: MetaFieldsModel = field(default_factory=MetaFieldsModel)
