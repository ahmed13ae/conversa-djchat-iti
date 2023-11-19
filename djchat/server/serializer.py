from rest_framework import serializers
from account.models import Account
from .models import Category, Channel, Server


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = "__all__"


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = "__all__"
        extra_kwargs = {
            'name': {'required': False},
            'owner': {'required': False},
            'category': {'required': False},
        }
    member = serializers.PrimaryKeyRelatedField(many=True, queryset=Account.objects.all())

    def __init__(self, *args, **kwargs):
        # Set 'required' to False for 'name', 'owner', 'category' fields if it's a partial update (PATCH request)
        if 'partial' in kwargs and kwargs['partial']:
            for field_name in ['name', 'owner', 'category']:
                self.fields[field_name].required = False

        super(ServerSerializer, self).__init__(*args, **kwargs)



class ServerListSerializer(serializers.ModelSerializer):
    num_members = serializers.SerializerMethodField()
    channel_server = ChannelSerializer(many=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = Server
        exclude = ("member",)

    def get_num_members(self, obj):
        if hasattr(obj, "num_members"):
            return obj.num_members
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        num_members = self.context.get("num_members")
        if not num_members:
            data.pop("num_members", None)
        return data
