from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):

        groups = [g.name for g in user.groups.all()]

        role = 'admin' if 'admin' in groups else 'user'
        role = 'performer' if 'service_employee' in groups else role

        token = super().get_token(user)
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['role'] = role
        return token
