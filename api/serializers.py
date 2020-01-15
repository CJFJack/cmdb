# _*_ coding:utf-8 _*_
from rest_framework import serializers
from assets.models import *


class HostSerializer(serializers.ModelSerializer):

    belongs_to_game_project = serializers.StringRelatedField()
    belongs_to_room = serializers.StringRelatedField()
    belongs_to_business = serializers.StringRelatedField()

    class Meta:
        model = Host
        fields = ('id', 'status', 'host_class', 'belongs_to_game_project',
                  'belongs_to_room', 'machine_type', 'belongs_to_business',
                  'platform', 'internal_ip', 'telecom_ip', 'unicom_ip',
                  'system', 'is_internet', 'sshuser', 'sshport',
                  'machine_model', 'cpu_num', 'cpu', 'ram', 'disk',
                  'host_comment')
