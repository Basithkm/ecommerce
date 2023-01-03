from djoser.serializers import UserSerializer as BaseUserSearilaizer, UserCreateSerializer   as BaseUserCreationSerializer
from store.models import Customer



class UserCreateSerializer(BaseUserCreationSerializer):
    class Meta(BaseUserCreationSerializer.Meta):
        fields = ['id','username','password','email','first_name','last_name']



class UserSerializer(BaseUserSearilaizer):
    class Meta(BaseUserSearilaizer.Meta):
        fields = ['id','username','email','first_name','last_name']
