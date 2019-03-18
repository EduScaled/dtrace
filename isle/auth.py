from django.conf import settings
from social_core.backends.oauth import BaseOAuth2
from social_core.utils import handle_http_errors
from isle.models import UserContextRole, Tag, ContextRole


def update_user(strategy, details, user=None, backend=None, *args, **kwargs):
    data = kwargs['response']
    if user:
        user.email = data['email']
        user.username = data['username']
        user.first_name = data['firstname']
        user.last_name = data['lastname']
        user.second_name = data.get('secondname', '') or ''
        user.icon = data.get('image') or {}
        user.unti_id = data.get('unti_id')
        user.leader_id = data.get('leader_id') or ''
        user.save()
        update_roles(user, data.get('roles'))


def update_roles(user, roles):
    if not isinstance(roles, dict):
        return
    context_roles = {(i.context_uuid, i.tag_id): i.id for i in ContextRole.objects.iterator()}
    current_tags = dict(Tag.objects.values_list('slug', 'id'))
    user_context_roles = []
    for context_uuid, tags in roles.items():
        for tag in tags:
            current_tag_id = current_tags.get('slug')
            if not current_tag_id:
                current_tag_id = Tag.objects.get_or_create(slug=tag)[0].id
                current_tags[tag] = current_tag_id
            current_context_role_id = context_roles.get((context_uuid, current_tag_id))
            if not current_context_role_id:
                # если нужный контекст еще не подтянулся в uploads, соответствующая роль для
                # него все равно будет создана
                current_context_role_id = ContextRole.objects.get_or_create(
                    context_uuid=context_uuid, tag_id=current_tag_id)[0].id
                context_roles[(context_uuid, current_tag_id)] = current_context_role_id
            user_context_roles.append(UserContextRole.objects.update_or_create(
                user=user, role_id=current_context_role_id, defaults={'is_active': True}
            )[0].id)
    UserContextRole.active_objects.filter(user=user).exclude(id__in=user_context_roles).update(is_active=False)


class UNTIBackend(BaseOAuth2):
    name = 'unti'
    ID_KEY = 'unti_id'
    AUTHORIZATION_URL = '{}/oauth2/authorize'.format(settings.SSO_UNTI_URL)
    ACCESS_TOKEN_URL = '{}/oauth2/access_token'.format(settings.SSO_UNTI_URL)
    USER_DATA_URL = '{url}/oauth2/access_token/{access_token}/'
    DEFAULT_SCOPE = []
    REDIRECT_STATE = False
    ACCESS_TOKEN_METHOD = 'POST'

    PIPELINE = (
        'social_core.pipeline.social_auth.social_details',
        'social_core.pipeline.social_auth.social_uid',
        'social_core.pipeline.social_auth.auth_allowed',
        'social_core.pipeline.social_auth.social_user',
        'social_core.pipeline.user.create_user',
        'isle.auth.update_user',
        'social_core.pipeline.social_auth.associate_user',
        'social_core.pipeline.social_auth.load_extra_data',
        'social_core.pipeline.user.user_details',
    )

    skip_email_verification = True

    def auth_url(self):
        return '{}&auth_entry={}'.format(
            super(UNTIBackend, self).auth_url(),
            self.data.get('auth_entry', 'login')
        )

    @handle_http_errors
    def auth_complete(self, *args, **kwargs):
        """Completes loging process, must return user instance"""
        self.strategy.session.setdefault('{}_state'.format(self.name),
                                         self.data.get('state'))
        next_url = getattr(settings, 'SOCIAL_NEXT_URL', '/')
        self.strategy.session.setdefault('next', next_url)
        return super(UNTIBackend, self).auth_complete(*args, **kwargs)

    def pipeline(self, pipeline, pipeline_index=0, *args, **kwargs):
        """
        Hack for using in open edx our custom DEFAULT_AUTH_PIPELINE
        """
        self.strategy.session.setdefault('auth_entry', 'register')
        return super(UNTIBackend, self).pipeline(
            pipeline=self.PIPELINE, pipeline_index=pipeline_index, *args, **kwargs
        )

    def get_user_details(self, response):
        """ Return user details from SSO account. """
        return response

    def user_data(self, access_token, *args, **kwargs):
        """ Grab user profile information from SSO. """
        return self.get_json(
            '{}/users/me'.format(settings.SSO_UNTI_URL),
            params={'access_token': access_token},
            headers={'Authorization': 'Bearer {}'.format(access_token)},
        )

    def do_auth(self, access_token, *args, **kwargs):
        """Finish the auth process once the access_token was retrieved"""
        data = self.user_data(access_token)
        data['access_token'] = access_token
        kwargs.update(data)
        kwargs.update({'response': data, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)
