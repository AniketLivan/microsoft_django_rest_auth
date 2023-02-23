from rest_framework import  serializers
from django.contrib.auth.models import User


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','password','first_name', 'last_name', 'email')
        extra_kwargs = {
            'password':{'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], password = validated_data['password']  , first_name=validated_data['first_name'],  last_name=validated_data['last_name'], email=validated_data["email"])
        return user