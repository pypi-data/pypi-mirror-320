# coding: utf-8

"""
    UltraCart Rest API V2

    UltraCart REST API Version 2  # noqa: E501

    OpenAPI spec version: 2.0.0
    Contact: support@ultracart.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class CartSettingsPaymentCreditCard(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'collect_credit_card_verification_number': 'bool',
        'collect_credit_card_verification_number_minimum': 'float',
        'credit_card_types': 'list[str]',
        'hosted_fields_shopping_cart_token': 'str'
    }

    attribute_map = {
        'collect_credit_card_verification_number': 'collect_credit_card_verification_number',
        'collect_credit_card_verification_number_minimum': 'collect_credit_card_verification_number_minimum',
        'credit_card_types': 'credit_card_types',
        'hosted_fields_shopping_cart_token': 'hosted_fields_shopping_cart_token'
    }

    def __init__(self, collect_credit_card_verification_number=None, collect_credit_card_verification_number_minimum=None, credit_card_types=None, hosted_fields_shopping_cart_token=None):  # noqa: E501
        """CartSettingsPaymentCreditCard - a model defined in Swagger"""  # noqa: E501

        self._collect_credit_card_verification_number = None
        self._collect_credit_card_verification_number_minimum = None
        self._credit_card_types = None
        self._hosted_fields_shopping_cart_token = None
        self.discriminator = None

        if collect_credit_card_verification_number is not None:
            self.collect_credit_card_verification_number = collect_credit_card_verification_number
        if collect_credit_card_verification_number_minimum is not None:
            self.collect_credit_card_verification_number_minimum = collect_credit_card_verification_number_minimum
        if credit_card_types is not None:
            self.credit_card_types = credit_card_types
        if hosted_fields_shopping_cart_token is not None:
            self.hosted_fields_shopping_cart_token = hosted_fields_shopping_cart_token

    @property
    def collect_credit_card_verification_number(self):
        """Gets the collect_credit_card_verification_number of this CartSettingsPaymentCreditCard.  # noqa: E501

        True if the credit card verification number should be collected  # noqa: E501

        :return: The collect_credit_card_verification_number of this CartSettingsPaymentCreditCard.  # noqa: E501
        :rtype: bool
        """
        return self._collect_credit_card_verification_number

    @collect_credit_card_verification_number.setter
    def collect_credit_card_verification_number(self, collect_credit_card_verification_number):
        """Sets the collect_credit_card_verification_number of this CartSettingsPaymentCreditCard.

        True if the credit card verification number should be collected  # noqa: E501

        :param collect_credit_card_verification_number: The collect_credit_card_verification_number of this CartSettingsPaymentCreditCard.  # noqa: E501
        :type: bool
        """

        self._collect_credit_card_verification_number = collect_credit_card_verification_number

    @property
    def collect_credit_card_verification_number_minimum(self):
        """Gets the collect_credit_card_verification_number_minimum of this CartSettingsPaymentCreditCard.  # noqa: E501

        If this field is null or the total is greater than or equal to this value then collect the CVV2.  # noqa: E501

        :return: The collect_credit_card_verification_number_minimum of this CartSettingsPaymentCreditCard.  # noqa: E501
        :rtype: float
        """
        return self._collect_credit_card_verification_number_minimum

    @collect_credit_card_verification_number_minimum.setter
    def collect_credit_card_verification_number_minimum(self, collect_credit_card_verification_number_minimum):
        """Sets the collect_credit_card_verification_number_minimum of this CartSettingsPaymentCreditCard.

        If this field is null or the total is greater than or equal to this value then collect the CVV2.  # noqa: E501

        :param collect_credit_card_verification_number_minimum: The collect_credit_card_verification_number_minimum of this CartSettingsPaymentCreditCard.  # noqa: E501
        :type: float
        """

        self._collect_credit_card_verification_number_minimum = collect_credit_card_verification_number_minimum

    @property
    def credit_card_types(self):
        """Gets the credit_card_types of this CartSettingsPaymentCreditCard.  # noqa: E501

        Available credit card types  # noqa: E501

        :return: The credit_card_types of this CartSettingsPaymentCreditCard.  # noqa: E501
        :rtype: list[str]
        """
        return self._credit_card_types

    @credit_card_types.setter
    def credit_card_types(self, credit_card_types):
        """Sets the credit_card_types of this CartSettingsPaymentCreditCard.

        Available credit card types  # noqa: E501

        :param credit_card_types: The credit_card_types of this CartSettingsPaymentCreditCard.  # noqa: E501
        :type: list[str]
        """

        self._credit_card_types = credit_card_types

    @property
    def hosted_fields_shopping_cart_token(self):
        """Gets the hosted_fields_shopping_cart_token of this CartSettingsPaymentCreditCard.  # noqa: E501

        The shoppingCartToken needed for proper initialization of hosted fields collection  # noqa: E501

        :return: The hosted_fields_shopping_cart_token of this CartSettingsPaymentCreditCard.  # noqa: E501
        :rtype: str
        """
        return self._hosted_fields_shopping_cart_token

    @hosted_fields_shopping_cart_token.setter
    def hosted_fields_shopping_cart_token(self, hosted_fields_shopping_cart_token):
        """Sets the hosted_fields_shopping_cart_token of this CartSettingsPaymentCreditCard.

        The shoppingCartToken needed for proper initialization of hosted fields collection  # noqa: E501

        :param hosted_fields_shopping_cart_token: The hosted_fields_shopping_cart_token of this CartSettingsPaymentCreditCard.  # noqa: E501
        :type: str
        """

        self._hosted_fields_shopping_cart_token = hosted_fields_shopping_cart_token

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(CartSettingsPaymentCreditCard, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, CartSettingsPaymentCreditCard):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
