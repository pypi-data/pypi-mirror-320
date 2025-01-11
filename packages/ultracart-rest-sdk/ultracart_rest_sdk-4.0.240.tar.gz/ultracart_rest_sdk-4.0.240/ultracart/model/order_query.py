"""
    UltraCart Rest API V2

    UltraCart REST API Version 2  # noqa: E501

    The version of the OpenAPI document: 2.0.0
    Contact: support@ultracart.com
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from ultracart.model_utils import (  # noqa: F401
    ApiTypeError,
    ModelComposed,
    ModelNormal,
    ModelSimple,
    cached_property,
    change_keys_js_to_python,
    convert_js_args_to_python_args,
    date,
    datetime,
    file_type,
    none_type,
    validate_get_composed_info,
    OpenApiModel
)
from ultracart.exceptions import ApiAttributeError



class OrderQuery(ModelNormal):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.

    Attributes:
      allowed_values (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          with a capitalized key describing the allowed value and an allowed
          value. These dicts store the allowed enum values.
      attribute_map (dict): The key is attribute name
          and the value is json key in definition.
      discriminator_value_class_map (dict): A dict to go from the discriminator
          variable value to the discriminator class name.
      validations (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          that stores validations for max_length, min_length, max_items,
          min_items, exclusive_maximum, inclusive_maximum, exclusive_minimum,
          inclusive_minimum, and regex.
      additional_properties_type (tuple): A tuple of classes accepted
          as additional properties values.
    """

    allowed_values = {
        ('current_stage',): {
            'ACCOUNTS_RECEIVABLE': "Accounts Receivable",
            'PENDING_CLEARANCE': "Pending Clearance",
            'FRAUD_REVIEW': "Fraud Review",
            'REJECTED': "Rejected",
            'SHIPPING_DEPARTMENT': "Shipping Department",
            'COMPLETED_ORDER': "Completed Order",
            'QUOTE_REQUEST': "Quote Request",
            'QUOTE_SENT': "Quote Sent",
            'LEAST_COST_ROUTING': "Least Cost Routing",
            'UNKNOWN': "Unknown",
        },
        ('payment_method',): {
            'AFFIRM': "Affirm",
            'AMAZON': "Amazon",
            'AMAZON_SC': "Amazon SC",
            'CASH': "Cash",
            'CHECK': "Check",
            'COD': "COD",
            'CREDIT_CARD': "Credit Card",
            'ECHECK': "eCheck",
            'LOANHERO': "LoanHero",
            'MONEY_ORDER': "Money Order",
            'PAYPAL': "PayPal",
            'PURCHASE_ORDER': "Purchase Order",
            'QUOTE_REQUEST': "Quote Request",
            'UNKNOWN': "Unknown",
            'WIRE_TRANSFER': "Wire Transfer",
            'VENMO': "Venmo",
            'APPLE_PAY': "Apple Pay",
            '_GOOGLE_PAY': " Google Pay",
        },
        ('query_target',): {
            'ORIGIN': "origin",
            'CACHE': "cache",
        },
    }

    validations = {
        ('cc_email',): {
            'max_length': 100,
        },
        ('city',): {
            'max_length': 32,
        },
        ('company',): {
            'max_length': 50,
        },
        ('country_code',): {
            'max_length': 2,
        },
        ('email',): {
            'max_length': 100,
        },
        ('first_name',): {
            'max_length': 30,
        },
        ('last_name',): {
            'max_length': 30,
        },
        ('phone',): {
            'max_length': 25,
        },
        ('postal_code',): {
            'max_length': 20,
        },
        ('rma',): {
            'max_length': 30,
        },
        ('screen_branding_theme_code',): {
            'max_length': 10,
        },
        ('state_region',): {
            'max_length': 32,
        },
    }

    @cached_property
    def additional_properties_type():
        """
        This must be a method because a model may have properties that are
        of type self, this must run after the class is loaded
        """
        return (bool, date, datetime, dict, float, int, list, str, none_type,)  # noqa: E501

    _nullable = False

    @cached_property
    def openapi_types():
        """
        This must be a method because a model may have properties that are
        of type self, this must run after the class is loaded

        Returns
            openapi_types (dict): The key is attribute name
                and the value is attribute type.
        """
        return {
            'cc_email': (str,),  # noqa: E501
            'channel_partner_code': (str,),  # noqa: E501
            'channel_partner_order_id': (str,),  # noqa: E501
            'city': (str,),  # noqa: E501
            'company': (str,),  # noqa: E501
            'country_code': (str,),  # noqa: E501
            'creation_date_begin': (str,),  # noqa: E501
            'creation_date_end': (str,),  # noqa: E501
            'current_stage': (str,),  # noqa: E501
            'custom_field_1': (str,),  # noqa: E501
            'custom_field_10': (str,),  # noqa: E501
            'custom_field_2': (str,),  # noqa: E501
            'custom_field_3': (str,),  # noqa: E501
            'custom_field_4': (str,),  # noqa: E501
            'custom_field_5': (str,),  # noqa: E501
            'custom_field_6': (str,),  # noqa: E501
            'custom_field_7': (str,),  # noqa: E501
            'custom_field_8': (str,),  # noqa: E501
            'custom_field_9': (str,),  # noqa: E501
            'customer_profile_oid': (int,),  # noqa: E501
            'email': (str,),  # noqa: E501
            'first_name': (str,),  # noqa: E501
            'item_id': (str,),  # noqa: E501
            'last_name': (str,),  # noqa: E501
            'order_id': (str,),  # noqa: E501
            'payment_date_begin': (str,),  # noqa: E501
            'payment_date_end': (str,),  # noqa: E501
            'payment_method': (str,),  # noqa: E501
            'phone': (str,),  # noqa: E501
            'postal_code': (str,),  # noqa: E501
            'purchase_order_number': (str,),  # noqa: E501
            'query_target': (str,),  # noqa: E501
            'refund_date_begin': (str,),  # noqa: E501
            'refund_date_end': (str,),  # noqa: E501
            'rma': (str,),  # noqa: E501
            'screen_branding_theme_code': (str,),  # noqa: E501
            'shipment_date_begin': (str,),  # noqa: E501
            'shipment_date_end': (str,),  # noqa: E501
            'shipped_on_date_begin': (str,),  # noqa: E501
            'shipped_on_date_end': (str,),  # noqa: E501
            'state_region': (str,),  # noqa: E501
            'storefront_host_name': (str,),  # noqa: E501
            'total': (float,),  # noqa: E501
        }

    @cached_property
    def discriminator():
        return None


    attribute_map = {
        'cc_email': 'cc_email',  # noqa: E501
        'channel_partner_code': 'channel_partner_code',  # noqa: E501
        'channel_partner_order_id': 'channel_partner_order_id',  # noqa: E501
        'city': 'city',  # noqa: E501
        'company': 'company',  # noqa: E501
        'country_code': 'country_code',  # noqa: E501
        'creation_date_begin': 'creation_date_begin',  # noqa: E501
        'creation_date_end': 'creation_date_end',  # noqa: E501
        'current_stage': 'current_stage',  # noqa: E501
        'custom_field_1': 'custom_field_1',  # noqa: E501
        'custom_field_10': 'custom_field_10',  # noqa: E501
        'custom_field_2': 'custom_field_2',  # noqa: E501
        'custom_field_3': 'custom_field_3',  # noqa: E501
        'custom_field_4': 'custom_field_4',  # noqa: E501
        'custom_field_5': 'custom_field_5',  # noqa: E501
        'custom_field_6': 'custom_field_6',  # noqa: E501
        'custom_field_7': 'custom_field_7',  # noqa: E501
        'custom_field_8': 'custom_field_8',  # noqa: E501
        'custom_field_9': 'custom_field_9',  # noqa: E501
        'customer_profile_oid': 'customer_profile_oid',  # noqa: E501
        'email': 'email',  # noqa: E501
        'first_name': 'first_name',  # noqa: E501
        'item_id': 'item_id',  # noqa: E501
        'last_name': 'last_name',  # noqa: E501
        'order_id': 'order_id',  # noqa: E501
        'payment_date_begin': 'payment_date_begin',  # noqa: E501
        'payment_date_end': 'payment_date_end',  # noqa: E501
        'payment_method': 'payment_method',  # noqa: E501
        'phone': 'phone',  # noqa: E501
        'postal_code': 'postal_code',  # noqa: E501
        'purchase_order_number': 'purchase_order_number',  # noqa: E501
        'query_target': 'query_target',  # noqa: E501
        'refund_date_begin': 'refund_date_begin',  # noqa: E501
        'refund_date_end': 'refund_date_end',  # noqa: E501
        'rma': 'rma',  # noqa: E501
        'screen_branding_theme_code': 'screen_branding_theme_code',  # noqa: E501
        'shipment_date_begin': 'shipment_date_begin',  # noqa: E501
        'shipment_date_end': 'shipment_date_end',  # noqa: E501
        'shipped_on_date_begin': 'shipped_on_date_begin',  # noqa: E501
        'shipped_on_date_end': 'shipped_on_date_end',  # noqa: E501
        'state_region': 'state_region',  # noqa: E501
        'storefront_host_name': 'storefront_host_name',  # noqa: E501
        'total': 'total',  # noqa: E501
    }

    read_only_vars = {
    }

    _composed_schemas = {}

    @classmethod
    @convert_js_args_to_python_args
    def _from_openapi_data(cls, *args, **kwargs):  # noqa: E501
        """OrderQuery - a model defined in OpenAPI

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the model in received_data
                                when deserializing a response
            _spec_property_naming (bool): True if the variable names in the input data
                                are serialized names, as specified in the OpenAPI document.
                                False if the variable names in the input data
                                are pythonic names, e.g. snake case (default)
            _configuration (Configuration): the instance to use when
                                deserializing a file_type parameter.
                                If passed, type conversion is attempted
                                If omitted no type conversion is done.
            _visited_composed_classes (tuple): This stores a tuple of
                                classes that we have traveled through so that
                                if we see that class again we will not use its
                                discriminator again.
                                When traveling through a discriminator, the
                                composed schema that is
                                is traveled through is added to this set.
                                For example if Animal has a discriminator
                                petType and we pass in "Dog", and the class Dog
                                allOf includes Animal, we move through Animal
                                once using the discriminator, and pick Dog.
                                Then in Dog, we will make an instance of the
                                Animal class but this time we won't travel
                                through its discriminator because we passed in
                                _visited_composed_classes = (Animal,)
            cc_email (str): CC Email. [optional]  # noqa: E501
            channel_partner_code (str): The code of the channel partner. [optional]  # noqa: E501
            channel_partner_order_id (str): The order ID assigned by the channel partner for this order. [optional]  # noqa: E501
            city (str): City. [optional]  # noqa: E501
            company (str): Company. [optional]  # noqa: E501
            country_code (str): ISO-3166 two letter country code. [optional]  # noqa: E501
            creation_date_begin (str): Date/time that the order was created. [optional]  # noqa: E501
            creation_date_end (str): Date/time that the order was created. [optional]  # noqa: E501
            current_stage (str): Current stage that the order is in.. [optional]  # noqa: E501
            custom_field_1 (str): Custom field 1. [optional]  # noqa: E501
            custom_field_10 (str): Custom field 10. [optional]  # noqa: E501
            custom_field_2 (str): Custom field 2. [optional]  # noqa: E501
            custom_field_3 (str): Custom field 3. [optional]  # noqa: E501
            custom_field_4 (str): Custom field 4. [optional]  # noqa: E501
            custom_field_5 (str): Custom field 5. [optional]  # noqa: E501
            custom_field_6 (str): Custom field 6. [optional]  # noqa: E501
            custom_field_7 (str): Custom field 7. [optional]  # noqa: E501
            custom_field_8 (str): Custom field 8. [optional]  # noqa: E501
            custom_field_9 (str): Custom field 9. [optional]  # noqa: E501
            customer_profile_oid (int): The customer profile to find associated orders for. [optional]  # noqa: E501
            email (str): Email. [optional]  # noqa: E501
            first_name (str): First name. [optional]  # noqa: E501
            item_id (str): Item ID. [optional]  # noqa: E501
            last_name (str): Last name. [optional]  # noqa: E501
            order_id (str): Order ID. [optional]  # noqa: E501
            payment_date_begin (str): Date/time that the order was successfully processed. [optional]  # noqa: E501
            payment_date_end (str): Date/time that the order was successfully processed. [optional]  # noqa: E501
            payment_method (str): Payment method. [optional]  # noqa: E501
            phone (str): Phone. [optional]  # noqa: E501
            postal_code (str): Postal code. [optional]  # noqa: E501
            purchase_order_number (str): Purchase order number. [optional]  # noqa: E501
            query_target (str): Query Target. [optional]  # noqa: E501
            refund_date_begin (str): Date/time that the order was refunded. [optional]  # noqa: E501
            refund_date_end (str): Date/time that the order was refunded. [optional]  # noqa: E501
            rma (str): RMA number. [optional]  # noqa: E501
            screen_branding_theme_code (str): Screen branding theme code associated with the order (legacy checkout). [optional]  # noqa: E501
            shipment_date_begin (str): Date/time that the order was shipped. [optional]  # noqa: E501
            shipment_date_end (str): Date/time that the order was shipped. [optional]  # noqa: E501
            shipped_on_date_begin (str): Date/time that the order should ship on. [optional]  # noqa: E501
            shipped_on_date_end (str): Date/time that the order should ship on. [optional]  # noqa: E501
            state_region (str): State for United States otherwise region or province for other countries. [optional]  # noqa: E501
            storefront_host_name (str): StoreFront host name associated with the order. [optional]  # noqa: E501
            total (float): Total. [optional]  # noqa: E501
        """

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', True)
        _path_to_item = kwargs.pop('_path_to_item', ())
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        self = super(OpenApiModel, cls).__new__(cls)

        if args:
            for arg in args:
                if isinstance(arg, dict):
                    kwargs.update(arg)
                else:
                    raise ApiTypeError(
                        "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments." % (
                            args,
                            self.__class__.__name__,
                        ),
                        path_to_item=_path_to_item,
                        valid_classes=(self.__class__,),
                    )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)

        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)
        return self

    required_properties = set([
        '_data_store',
        '_check_type',
        '_spec_property_naming',
        '_path_to_item',
        '_configuration',
        '_visited_composed_classes',
    ])

    @convert_js_args_to_python_args
    def __init__(self, *args, **kwargs):  # noqa: E501
        """OrderQuery - a model defined in OpenAPI

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the model in received_data
                                when deserializing a response
            _spec_property_naming (bool): True if the variable names in the input data
                                are serialized names, as specified in the OpenAPI document.
                                False if the variable names in the input data
                                are pythonic names, e.g. snake case (default)
            _configuration (Configuration): the instance to use when
                                deserializing a file_type parameter.
                                If passed, type conversion is attempted
                                If omitted no type conversion is done.
            _visited_composed_classes (tuple): This stores a tuple of
                                classes that we have traveled through so that
                                if we see that class again we will not use its
                                discriminator again.
                                When traveling through a discriminator, the
                                composed schema that is
                                is traveled through is added to this set.
                                For example if Animal has a discriminator
                                petType and we pass in "Dog", and the class Dog
                                allOf includes Animal, we move through Animal
                                once using the discriminator, and pick Dog.
                                Then in Dog, we will make an instance of the
                                Animal class but this time we won't travel
                                through its discriminator because we passed in
                                _visited_composed_classes = (Animal,)
            cc_email (str): CC Email. [optional]  # noqa: E501
            channel_partner_code (str): The code of the channel partner. [optional]  # noqa: E501
            channel_partner_order_id (str): The order ID assigned by the channel partner for this order. [optional]  # noqa: E501
            city (str): City. [optional]  # noqa: E501
            company (str): Company. [optional]  # noqa: E501
            country_code (str): ISO-3166 two letter country code. [optional]  # noqa: E501
            creation_date_begin (str): Date/time that the order was created. [optional]  # noqa: E501
            creation_date_end (str): Date/time that the order was created. [optional]  # noqa: E501
            current_stage (str): Current stage that the order is in.. [optional]  # noqa: E501
            custom_field_1 (str): Custom field 1. [optional]  # noqa: E501
            custom_field_10 (str): Custom field 10. [optional]  # noqa: E501
            custom_field_2 (str): Custom field 2. [optional]  # noqa: E501
            custom_field_3 (str): Custom field 3. [optional]  # noqa: E501
            custom_field_4 (str): Custom field 4. [optional]  # noqa: E501
            custom_field_5 (str): Custom field 5. [optional]  # noqa: E501
            custom_field_6 (str): Custom field 6. [optional]  # noqa: E501
            custom_field_7 (str): Custom field 7. [optional]  # noqa: E501
            custom_field_8 (str): Custom field 8. [optional]  # noqa: E501
            custom_field_9 (str): Custom field 9. [optional]  # noqa: E501
            customer_profile_oid (int): The customer profile to find associated orders for. [optional]  # noqa: E501
            email (str): Email. [optional]  # noqa: E501
            first_name (str): First name. [optional]  # noqa: E501
            item_id (str): Item ID. [optional]  # noqa: E501
            last_name (str): Last name. [optional]  # noqa: E501
            order_id (str): Order ID. [optional]  # noqa: E501
            payment_date_begin (str): Date/time that the order was successfully processed. [optional]  # noqa: E501
            payment_date_end (str): Date/time that the order was successfully processed. [optional]  # noqa: E501
            payment_method (str): Payment method. [optional]  # noqa: E501
            phone (str): Phone. [optional]  # noqa: E501
            postal_code (str): Postal code. [optional]  # noqa: E501
            purchase_order_number (str): Purchase order number. [optional]  # noqa: E501
            query_target (str): Query Target. [optional]  # noqa: E501
            refund_date_begin (str): Date/time that the order was refunded. [optional]  # noqa: E501
            refund_date_end (str): Date/time that the order was refunded. [optional]  # noqa: E501
            rma (str): RMA number. [optional]  # noqa: E501
            screen_branding_theme_code (str): Screen branding theme code associated with the order (legacy checkout). [optional]  # noqa: E501
            shipment_date_begin (str): Date/time that the order was shipped. [optional]  # noqa: E501
            shipment_date_end (str): Date/time that the order was shipped. [optional]  # noqa: E501
            shipped_on_date_begin (str): Date/time that the order should ship on. [optional]  # noqa: E501
            shipped_on_date_end (str): Date/time that the order should ship on. [optional]  # noqa: E501
            state_region (str): State for United States otherwise region or province for other countries. [optional]  # noqa: E501
            storefront_host_name (str): StoreFront host name associated with the order. [optional]  # noqa: E501
            total (float): Total. [optional]  # noqa: E501
        """

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', False)
        _path_to_item = kwargs.pop('_path_to_item', ())
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        if args:
            for arg in args:
                if isinstance(arg, dict):
                    kwargs.update(arg)
                else:
                    raise ApiTypeError(
                        "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments." % (
                            args,
                            self.__class__.__name__,
                        ),
                        path_to_item=_path_to_item,
                        valid_classes=(self.__class__,),
                    )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)

        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)
            if var_name in self.read_only_vars:
                raise ApiAttributeError(f"`{var_name}` is a read-only attribute. Use `from_openapi_data` to instantiate "
                                     f"class with read only attributes.")
