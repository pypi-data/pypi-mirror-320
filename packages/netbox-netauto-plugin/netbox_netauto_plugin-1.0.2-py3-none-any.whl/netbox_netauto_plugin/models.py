from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.conf import settings
from netbox.models import NetBoxModel
from netbox.models.features import *
from ipam.models import IPAddress
from utilities.querysets import RestrictedQuerySet

from . import validators
from . import choices

gitlab_repository_url = settings.PLUGINS_CONFIG.get('netbox_netauto_plugin', dict()).get('gitlab_repository_url')

class NetAutoModel(
    # NetBoxModel,
    ChangeLoggingMixin,
    CloningMixin,
    CustomFieldsMixin,
    CustomLinksMixin,
    CustomValidationMixin,
    TagsMixin,
    EventRulesMixin,
    models.Model
):
    objects = RestrictedQuerySet.as_manager()
    class Meta:
        abstract = True

class Profile(NetAutoModel):
    name = models.CharField(
        max_length=50
    )
    type = models.CharField(
        max_length=50,
        choices=choices.ProfileTypeChoices,
    )
    cluster = models.ForeignKey(
        to="dcim.VirtualChassis",
        on_delete=models.SET_NULL,
        related_name="profiles",
        null=True,
    )

    class Meta:
        ordering = ("type",)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'cluster'),
                name='%(app_label)s_%(class)s_unique_name_cluster'
            ),
        )

    def get_type_color(self):
        return choices.ProfileTypeChoices.colors.get(self.type)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(f"plugins:netbox_netauto_plugin:{self._meta.model_name.lower()}", args=[self.pk])
    


class Application(NetAutoModel):

    ritm = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="RITM"
    )
    name = models.CharField(
        max_length=30,
        unique=True
    )
    description = models.CharField(
        max_length=50,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=choices.ApplicationStatusChoices,
        default=choices.ApplicationStatusChoices.CREATE,
        editable=False
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
    )
    cluster = models.ForeignKey(
        to="dcim.VirtualChassis",
        on_delete=models.SET_NULL,
        related_name="%(class)s",
        null=True,
    )
    virtual_ip_address = models.ForeignKey(
        to="ipam.IPAddress",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+"
    )
    virtual_ip_address_string = models.CharField(
        max_length=18,
        blank=True,
        null=True,
        verbose_name="Virtual IP Address",
        validators=[validators.validate_cidr]
    )
    virtual_port = models.PositiveIntegerField(
        verbose_name="Virtual Port",
        default=443
    )
    member_ip_addresses = models.ManyToManyField(
        to="ipam.IPAddress",
        blank=True,
        related_name="+"
    )
    member_ip_addresses_string = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Member IP Addresses",
        validators=[validators.validate_cidr_list]
    )
    member_port = models.PositiveIntegerField(
        verbose_name="Member Port",
        default=80
    )

    # Profiles
    persistence_profile = models.ForeignKey(
        to=Profile,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Persistence",
        # limit_choices_to={"type": choices.ProfileTypeChoices.PERSISTENCE}
    )

    clone_fields = [
        "name",
        "description",
        "tenant",
        "cluster",
        "virtual_port",
        "member_port",
        "persistence_profile"
    ]

    class Meta:
        abstract = True

    def get_status_color(self):
        return choices.ApplicationStatusChoices.colors.get(self.status)
    
    def clean(self):
        super().clean()
        validators.AtLeastOneSetValidator({'virtual_ip_address'}, {'virtual_ip_address_string'})(self)
        # validators.AtLeastOneSetValidator({'member_ip_addresses'}, {'member_ip_addresses_string'})(self)
            
    def save(self, *args, **kwargs):
        if not self.virtual_ip_address:
            self.virtual_ip_address = IPAddress.objects.create(
                address=self.virtual_ip_address_string,
                )
        self.virtual_ip_address_string = None

        # BUG: member_ip_addresses are not being saved
        # if self.member_ip_addresses_string:
        #     ip_addresses = [IPAddress.objects.create(address=ip) for ip in self.member_ip_addresses_string.split(",")]
        #     self.member_ip_addresses.add(*ip_addresses)
        #     self.member_ip_addresses_string = None
        
        super().save(*args, **kwargs)

    def clone(self):
        attrs = super().clone()
        attrs['name'] = f"{attrs['name']} (copy)"
        return attrs

    def delete(self, using=None, keep_parents=False):
        self.status = choices.ApplicationStatusChoices.DELETE
        self.save(using=using, update_fields=['status'])

    def api_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    @property
    def merge_request_url(self):
        return f"{gitlab_repository_url}-/merge_requests?scope=all&state=opened&source_branch={self._meta.model_name.lower()}s/{self.pk}"
    
    @property
    def pipeline_url(self):
        return f"{gitlab_repository_url}-/pipelines?page=1&scope=all&source=trigger"


class HTTPApplication(Application):

    #Profiles
    http = models.ForeignKey(
        to=Profile,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        verbose_name="HTTP Profile",
        # limit_choices_to={"type": choices.ProfileTypeChoices.HTTP}
    )
    tcp_wan = models.ForeignKey(
        to=Profile,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        verbose_name="TCP WAN",
        # limit_choices_to={"type": choices.ProfileTypeChoices.TCP}
    )
    tcp_lan = models.ForeignKey(
        to=Profile,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        verbose_name="TCP LAN",
        # limit_choices_to={"type": choices.ProfileTypeChoices.TCP}
    )

    # Client SSL profile
    client_ssl_profile = models.ForeignKey(
        to=Profile,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Client SSL Profile",
        # limit_choices_to={"type": choices.ProfileTypeChoices.CLIENT_SSL}
    )
    client_ssl_server_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Server name (SNI)"
    )
    client_ssl_certificate = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Client certificate"
    )
    client_ssl_auth_mode = models.CharField(
        max_length=50,
        choices=choices.ClientSSLAuthModeChoices,
        default=choices.ClientSSLAuthModeChoices.REQUIRED,
        blank=True,
        verbose_name="Authentication mode"
    )
    client_ssl_cert_authority = models.CharField(
        max_length=255,
        choices=choices.ClientSSLCertAuthorityChoices,
        default=choices.ClientSSLCertAuthorityChoices.BUNDLE,
        blank=True,
        verbose_name="Trusted CA bundle"
    )


    server_ssl_profile = models.ForeignKey(
        to=Profile,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Server SSL Profile",
        # limit_choices_to={"type": choices.ProfileTypeChoices.SERVER_SSL}
    )
    oneconnect_profile = models.ForeignKey(
        to=Profile,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        verbose_name="OneConnect Profile",
        # limit_choices_to={"type": choices.ProfileTypeChoices.ONECONNECT}
    )
    
    # Health Monitor
    health_monitor_profile = models.ForeignKey(
        to=Profile,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Health Monitor",
        # limit_choices_to={"type": choices.ProfileTypeChoices.HEALTH_MONITOR}
    )
    send_string = models.CharField(
        max_length=50,
        blank=True
    )
    receive_string = models.CharField(
        max_length=50,
        blank=True
    )
    interval = models.PositiveIntegerField(
        default=5,
        blank=True
    )
    timeout = models.PositiveIntegerField(
        default=16,
        blank=True
    )

    clone_fields = Application.clone_fields + [
        "tcp_wan",
        "tcp_lan",
        "http",
        "client_ssl_profile",
        "client_ssl_certificate",
        "client_ssl_auth_mode",
        "client_ssl_cert_authority",
        "server_ssl_profile",
        "oneconnect_profile",
        "health_monitor_profile",
        "send_string",
        "receive_string",
        "interval",
        "timeout"
    ]
    
    class Meta:
        abstract = True

    def get_absolute_url(self):
        return reverse("plugins:netbox_netauto_plugin:httpapplication", args=[self.pk])
    
    def get_client_ssl_auth_mode_color(self):
        return choices.ClientSSLAuthModeChoices.colors.get(self.client_ssl_auth_mode)
    
    def clean(self):
        super().clean()
        validators.AtLeastOneSetValidator({'health_monitor_profile'}, {'send_string', 'receive_string', 'interval', 'timeout'})(self)


class FlexApplication(HTTPApplication):
    
    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_netauto_plugin:flexapplication", args=[self.pk])
    

class L4Application(Application):
    fastl4 = models.ForeignKey(
        to=Profile,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        verbose_name="Fast L4 Profile",
        # limit_choices_to={"type": choices.ProfileTypeChoices.FASTL4}
    )
        
    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_netauto_plugin:l4application", args=[self.pk])


class mTLSApplication(HTTPApplication):
    redirect_from_http = models.BooleanField(
        default=True,
        verbose_name="Redirect from HTTP",
        help_text="Redirect from HTTP to HTTPS"
    )

    clone_fields = HTTPApplication.clone_fields + [
        "redirect_from_http"
        ]

    class Meta:
        ordering = ("name",)
        verbose_name = "mTLS Application"
        verbose_name_plural = "mTLS Applications"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_netauto_plugin:mtlsapplication", args=[self.pk])
    
    def clean(self):
        super().clean()
        validators.AtLeastOneSetValidator({'client_ssl_profile'}, {'client_ssl_certificate', 'client_ssl_auth_mode', 'client_ssl_cert_authority'})(self)
