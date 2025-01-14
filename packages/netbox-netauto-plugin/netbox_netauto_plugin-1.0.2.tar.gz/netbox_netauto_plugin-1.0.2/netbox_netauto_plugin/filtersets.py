import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from extras.filters import TagFilter
from . import models, choices

class ProfileFilterSet(NetBoxModelFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=choices.ProfileTypeChoices
    )
    tags = TagFilter(
        field_name="tags__id",
        to_field_name="id",
    )
    
    class Meta:
        model = models.Profile
        fields = (
            "name", "type", "cluster", "tags"
        )
    
    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)
    
    def filter_by_type(self, queryset, name, value):
        return queryset.filter(type__in=value)

class FlexApplicationFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = models.FlexApplication
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
            "tcp_wan",
            "tcp_lan",
            "persistence_profile",
            "health_monitor_profile",
            "send_string",
            "receive_string",
            "interval",
            "timeout"
        )

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)

class L4ApplicationFilterSet(NetBoxModelFilterSet):
    
    class Meta:
        model = models.L4Application
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
            "fastl4",
            "persistence_profile"
        )

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)

class mTLSApplicationFilterSet(NetBoxModelFilterSet):
    
    class Meta:
        model = models.mTLSApplication
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
            "tcp_wan",
            "tcp_lan",
            "persistence_profile",
            "health_monitor_profile",
            "send_string",
            "receive_string",
            "interval",
            "timeout"
        )

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)