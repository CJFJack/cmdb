# -*- encoding: utf-8 -*-

from django.db.models.signals import pre_delete
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from myworkflows.models import SVNWorkflow
from myworkflows.models import ServerPermissionWorkflow
from myworkflows.models import FailureDeclareWorkflow
from myworkflows.models import StateObjectUserRelation
from myworkflows.models import WorkflowStateEvent
from myworkflows.models import Wifi
from myworkflows.models import ComputerParts
from myworkflows.models import ClientHotUpdate
from myworkflows.models import ServerHotUpdate
from myworkflows.models import VersionUpdate
from myworkflows.models import Machine
from myworkflows.models import ProjectAdjust
from myworkflows.models import MysqlWorkflow


@receiver(pre_delete, sender=SVNWorkflow)
def clear_state_object_user_relation(sender, **kwargs):
    obj = kwargs['instance']
    ctype = ContentType.objects.get_for_model(obj)

    StateObjectUserRelation.objects.filter(content_type=ctype, object_id=obj.id).delete()
    WorkflowStateEvent.objects.filter(content_type=ctype, object_id=obj.id).delete()


@receiver(pre_delete, sender=ServerPermissionWorkflow)
def clear_ser_perm(sender, **kwargs):
    obj = kwargs['instance']
    ctype = ContentType.objects.get_for_model(obj)

    StateObjectUserRelation.objects.filter(content_type=ctype, object_id=obj.id).delete()
    WorkflowStateEvent.objects.filter(content_type=ctype, object_id=obj.id).delete()


@receiver(pre_delete, sender=FailureDeclareWorkflow)
def clear_failure_decalre(sender, **kwargs):
    obj = kwargs['instance']
    ctype = ContentType.objects.get_for_model(obj)

    StateObjectUserRelation.objects.filter(content_type=ctype, object_id=obj.id).delete()
    WorkflowStateEvent.objects.filter(content_type=ctype, object_id=obj.id).delete()


@receiver(pre_delete, sender=ClientHotUpdate)
def clear_hot_update(sender, **kwargs):
    obj = kwargs['instance']
    ctype = ContentType.objects.get_for_model(obj)

    StateObjectUserRelation.objects.filter(content_type=ctype, object_id=obj.id).delete()
    WorkflowStateEvent.objects.filter(content_type=ctype, object_id=obj.id).delete()


@receiver(pre_delete, sender=Wifi)
def clear_wifi(sender, **kwargs):
    obj = kwargs['instance']
    ctype = ContentType.objects.get_for_model(obj)

    StateObjectUserRelation.objects.filter(content_type=ctype, object_id=obj.id).delete()
    WorkflowStateEvent.objects.filter(content_type=ctype, object_id=obj.id).delete()


@receiver(pre_delete, sender=ComputerParts)
def clear_computer_parts(sender, **kwargs):
    obj = kwargs['instance']
    ctype = ContentType.objects.get_for_model(obj)

    StateObjectUserRelation.objects.filter(content_type=ctype, object_id=obj.id).delete()
    WorkflowStateEvent.objects.filter(content_type=ctype, object_id=obj.id).delete()


@receiver(pre_delete, sender=ServerHotUpdate)
def clear_hot_update_server(sender, **kwargs):
    obj = kwargs['instance']
    ctype = ContentType.objects.get_for_model(obj)

    StateObjectUserRelation.objects.filter(content_type=ctype, object_id=obj.id).delete()
    WorkflowStateEvent.objects.filter(content_type=ctype, object_id=obj.id).delete()


@receiver(pre_delete, sender=VersionUpdate)
def clear_version_update_server(sender, **kwargs):
    obj = kwargs['instance']
    ctype = ContentType.objects.get_for_model(obj)

    StateObjectUserRelation.objects.filter(content_type=ctype, object_id=obj.id).delete()
    WorkflowStateEvent.objects.filter(content_type=ctype, object_id=obj.id).delete()


@receiver(pre_delete, sender=Machine)
def clear_machine(sender, **kwargs):
    obj = kwargs['instance']
    ctype = ContentType.objects.get_for_model(obj)

    StateObjectUserRelation.objects.filter(content_type=ctype, object_id=obj.id).delete()
    WorkflowStateEvent.objects.filter(content_type=ctype, object_id=obj.id).delete()


@receiver(pre_delete, sender=ProjectAdjust)
def clear_project_adjust(sender, **kwargs):
    obj = kwargs['instance']
    ctype = ContentType.objects.get_for_model(obj)

    StateObjectUserRelation.objects.filter(content_type=ctype, object_id=obj.id).delete()
    WorkflowStateEvent.objects.filter(content_type=ctype, object_id=obj.id).delete()


@receiver(pre_delete, sender=MysqlWorkflow)
def clear_mysql_workflow(sender, **kwargs):
    obj = kwargs['instance']
    ctype = ContentType.objects.get_for_model(obj)

    StateObjectUserRelation.objects.filter(content_type=ctype, object_id=obj.id).delete()
    WorkflowStateEvent.objects.filter(content_type=ctype, object_id=obj.id).delete()
