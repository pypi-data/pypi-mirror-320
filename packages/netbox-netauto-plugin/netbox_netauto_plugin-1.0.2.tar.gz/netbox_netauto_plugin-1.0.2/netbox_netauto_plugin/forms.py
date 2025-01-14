from django import forms
from ipam.models import IPAddress
from tenancy.models import Tenant
from dcim.models import VirtualChassis
from extras.models import Tag
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet, TabbedGroups, InlineFields, ObjectAttribute
from utilities.forms import add_blank_choice
from django.conf import settings

from . import models
from . import choices
from .utils import get_initial_ip, get_choices


class ProfileForm(NetBoxModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        query_params={'color': settings.PLUGINS_CONFIG['netbox_netauto_plugin']['default_pillar_color']},
        label='Pillar',
    )
    class Meta:
        model = models.Profile
        fields = ("name", "type", "cluster", "tags")

class ProfileFilterForm(NetBoxModelFilterSetForm):
    model = models.Profile
    # fieldsets = (
    #     FieldSet(
    #         "name",
    #         "type",
    #         "cluster",
    #         "tags",
    #         name="Profile Details"
    #     ),
    # )

class ApplicationForm(NetBoxModelForm):
    ritm = forms.ChoiceField(
        label="RITM",
        required=False,
        choices=(),
    )
    name = forms.CharField(
        label="Name",
        required=True,
    )
    description = forms.CharField(
        label="Description",
        required=False,
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        selector=True,
    )
    cluster = DynamicModelChoiceField(
        queryset=VirtualChassis.objects.all(),
        # TODO test this query_params={"members__tenant": "$tenant"},
        required=False,
        selector=True,
    )
    virtual_ip_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        query_params={'tenant_id': '$tenant'},
        required=False,
        selector=True,
        label="Virtual IP Address",
        help_text="Select the destination IP address."
    )
    virtual_ip_address_string = forms.CharField(
        label="Virtual IP Address",
        required=False,
        help_text="Enter the destination IP address with a mask. Initial value is the first available IP address in the VIP prefix.",
    )
    member_ip_addresses = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        selector=True,
        label="Pool member IP Addresses",
        help_text="Select the member IP addresses."
    )
    member_ip_addresses_string = forms.CharField(
        label="Pool member IP Addresses",
        required=False,
        help_text="Enter the member IP addresses with a mask separated by commas. Example: '1.1.1.1/24, 2.2.2.2/24'",
    )
    send_string = forms.CharField(
        label="Send String",
        required=False,
    )
    receive_string = forms.CharField(
        label="Receive String",
        required=False,
    )
    persistence_profile = DynamicModelChoiceField(
        queryset=models.Profile.objects.all(),
        query_params={
            'type': choices.ProfileTypeChoices.PERSISTENCE,
            'cluster': '$cluster',
            'tags': '$tags'
        },
        label="Persistence Profile",
        required=False,
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        query_params={'color': settings.PLUGINS_CONFIG['netbox_netauto_plugin']['default_pillar_color']},
        label='Pillar',
    )

    class Meta:
        fields = (
            "ritm", 
            "name", 
            "description", 
            "tenant", 
            "cluster", 
            "virtual_ip_address", 
            "virtual_ip_address_string", 
            "virtual_port", 
            "member_ip_addresses", 
            "member_ip_addresses_string", 
            "member_port", 
            "persistence_profile", 
            "tags"
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['virtual_ip_address_string'] = get_initial_ip() if self.instance._state.adding else None
        self.fields['ritm'].choices = add_blank_choice(get_choices())

    # on form submission set status to New -> leads to triggering pipeline
    # where as setting status to other values over API does not trigger pipeline
    def save(self, *args, **kwargs):
        if not self.instance._state.adding:
            self.instance.status = choices.ApplicationStatusChoices.UPDATE
        return super().save(*args, **kwargs)


class HTTPApplicationForm(ApplicationForm):

    tcp_wan = DynamicModelChoiceField(
        queryset=models.Profile.objects.all(),
        query_params={
            'type': choices.ProfileTypeChoices.TCP,
            'cluster': '$cluster',
            'tags': '$tags'
        },
        label="TCP WAN Profile",
    )
    tcp_lan = DynamicModelChoiceField(
        queryset=models.Profile.objects.all(),
        query_params={
            'type': choices.ProfileTypeChoices.TCP,
            'cluster': '$cluster',
            'tags': '$tags'
        },
        label="TCP LAN Profile",
    )
    http = DynamicModelChoiceField(
        queryset=models.Profile.objects.all(),
        query_params={
            'type': choices.ProfileTypeChoices.HTTP,
            'cluster': '$cluster',
            'tags': '$tags'
        },
        label="HTTP Profile",
    )
    client_ssl_profile = DynamicModelChoiceField(
        queryset=models.Profile.objects.all(),
        query_params={
            'type': choices.ProfileTypeChoices.CLIENT_SSL,
            'cluster': '$cluster',
            'tags': '$tags'
        },
        label="Client SSL Profile",
        required=False,
    )
    server_ssl_profile = DynamicModelChoiceField(
        queryset=models.Profile.objects.all(),
        query_params={
            'type': choices.ProfileTypeChoices.SERVER_SSL,
            'cluster': '$cluster',
            'tags': '$tags'
        },
        label="Server SSL Profile",
        required=False,
    )
    oneconnect_profile = DynamicModelChoiceField(
        queryset=models.Profile.objects.all(),
        query_params={
            'type': choices.ProfileTypeChoices.ONECONNECT,
            'cluster': '$cluster',
            'tags': '$tags'
        },
        label="OneConnect Profile",
    )
    health_monitor_profile = DynamicModelChoiceField(
        queryset=models.Profile.objects.all(),
        query_params={
            'type': choices.ProfileTypeChoices.HEALTH_MONITOR,
            'cluster': '$cluster',
            'tags': '$tags'
        },
        label="Health Monitor Profile",
        required=False,
    )
    
    class Meta(ApplicationForm.Meta):
        fields = ApplicationForm.Meta.fields + (
            "tcp_wan", 
            "tcp_lan",
            "http", 
            "client_ssl_profile", 
            "server_ssl_profile", 
            "oneconnect_profile", 
            "health_monitor_profile", 
            "send_string", 
            "receive_string", 
            "interval", 
            "timeout", 
            "client_ssl_server_name",
            "client_ssl_certificate", 
            "client_ssl_auth_mode", 
            "client_ssl_cert_authority",
        )

class FlexApplicationForm(HTTPApplicationForm):
    client_ssl_profile = DynamicModelChoiceField(
        queryset=models.Profile.objects.all(),
        query_params={
            'type': choices.ProfileTypeChoices.CLIENT_SSL,
            'cluster': '$cluster',
            'tags': '$tags'
        },
        label="Client SSL Profile",
    )

    fieldsets = (
        FieldSet(
            "name",
            "tenant", 
            "tags",
            "cluster",
            TabbedGroups(
                FieldSet("virtual_ip_address", name="IP Address Object"),
                FieldSet("virtual_ip_address_string", name="CIDR String"),
            ),
            "virtual_port", 
            TabbedGroups(
                FieldSet("member_ip_addresses", name="IP Address Objects"),
                FieldSet("member_ip_addresses_string", name="CIDR List"),
            ),
            "member_port",
            "description",
            name="Application Details"
        ),
        FieldSet(
            "tcp_wan", 
            "tcp_lan",
            "persistence_profile", 
            "http", 
            "client_ssl_profile",
            "server_ssl_profile", 
            "oneconnect_profile",
            name="Profiles"
        ),
        FieldSet(
            TabbedGroups(
                FieldSet("health_monitor_profile", name="Existing"),
                FieldSet("send_string", "receive_string", "interval", "timeout", name="Custom"),
            ),
            name="Health Monitor"
        )
    )

    class Meta(HTTPApplicationForm.Meta):
        model = models.FlexApplication

class FlexApplicationFilterForm(NetBoxModelFilterSetForm):
    model = models.FlexApplication


class L4ApplicationForm(ApplicationForm):
    fastl4 = DynamicModelChoiceField(
        queryset=models.Profile.objects.all(),
        query_params={
            'type': choices.ProfileTypeChoices.FASTL4,
            'cluster': '$cluster',
            'tags': '$tags'
        },
        label="FastL4 Profile",
    )

    fieldsets = (
        FieldSet(
            "name",
            "tenant", 
            "tags",
            "cluster",
            TabbedGroups(
                FieldSet("virtual_ip_address", name="IP Address Object"),
                FieldSet("virtual_ip_address_string", name="CIDR String"),
            ),
            "virtual_port", 
            TabbedGroups(
                FieldSet("member_ip_addresses", name="IP Address Objects"),
                FieldSet("member_ip_addresses_string", name="CIDR List"),
            ),
            "member_port",
            "description",
            name="Application Details"
        ),
        FieldSet(
            "fastl4",
            "persistence_profile", 
            name="Profiles"
        ),
    )

    class Meta(ApplicationForm.Meta):
        model = models.L4Application
        fields = ApplicationForm.Meta.fields + (
            "fastl4",
        )

class L4ApplicationFilterForm(NetBoxModelFilterSetForm):
    model = models.L4Application


class mTLSApplicationForm(HTTPApplicationForm):
    fieldsets = (
        FieldSet(
            "name",
            "tenant", 
            "tags",
            "cluster",
            TabbedGroups(
                FieldSet("virtual_ip_address", name="IP Address Object"),
                FieldSet("virtual_ip_address_string", name="CIDR String"),
            ),
            "virtual_port", 
            TabbedGroups(
                FieldSet("member_ip_addresses", name="IP Address Objects"),
                FieldSet("member_ip_addresses_string", name="CIDR List"),
            ),
            "member_port",
            "redirect_from_http",
            "description",
            name="Application Details"
        ),
        FieldSet(
            "tcp_wan", 
            "tcp_lan",
            "persistence_profile", 
            "http", 
            "server_ssl_profile", 
            "oneconnect_profile",
            name="Profiles"
        ),
        FieldSet(
            TabbedGroups(
                FieldSet("client_ssl_profile", name="Existing"),
                FieldSet("client_ssl_certificate", "client_ssl_auth_mode", "client_ssl_cert_authority", "client_ssl_server_name", name="Custom")
            ),
            name="Client SSL Profile"
        ),
        FieldSet(
            TabbedGroups(
                FieldSet("health_monitor_profile", name="Existing"),
                FieldSet("send_string", "receive_string", "interval", "timeout", name="Custom"),
            ),
            name="Health Monitor"
        )
    )

    class Meta(HTTPApplicationForm.Meta):
        model = models.mTLSApplication
        fields = HTTPApplicationForm.Meta.fields + (
            "redirect_from_http",
        )

class mTLSApplicationFilterForm(NetBoxModelFilterSetForm):
    model = models.mTLSApplication

    