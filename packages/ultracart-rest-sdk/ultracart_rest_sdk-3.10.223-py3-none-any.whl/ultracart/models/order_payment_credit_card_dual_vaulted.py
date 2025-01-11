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


class OrderPaymentCreditCardDualVaulted(object):
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
        'gateway_name': 'str',
        'properties': 'list[OrderPaymentCreditCardDualVaultedProperty]',
        'rotating_transaction_gateway_code': 'str'
    }

    attribute_map = {
        'gateway_name': 'gateway_name',
        'properties': 'properties',
        'rotating_transaction_gateway_code': 'rotating_transaction_gateway_code'
    }

    def __init__(self, gateway_name=None, properties=None, rotating_transaction_gateway_code=None):  # noqa: E501
        """OrderPaymentCreditCardDualVaulted - a model defined in Swagger"""  # noqa: E501

        self._gateway_name = None
        self._properties = None
        self._rotating_transaction_gateway_code = None
        self.discriminator = None

        if gateway_name is not None:
            self.gateway_name = gateway_name
        if properties is not None:
            self.properties = properties
        if rotating_transaction_gateway_code is not None:
            self.rotating_transaction_gateway_code = rotating_transaction_gateway_code

    @property
    def gateway_name(self):
        """Gets the gateway_name of this OrderPaymentCreditCardDualVaulted.  # noqa: E501


        :return: The gateway_name of this OrderPaymentCreditCardDualVaulted.  # noqa: E501
        :rtype: str
        """
        return self._gateway_name

    @gateway_name.setter
    def gateway_name(self, gateway_name):
        """Sets the gateway_name of this OrderPaymentCreditCardDualVaulted.


        :param gateway_name: The gateway_name of this OrderPaymentCreditCardDualVaulted.  # noqa: E501
        :type: str
        """

        self._gateway_name = gateway_name

    @property
    def properties(self):
        """Gets the properties of this OrderPaymentCreditCardDualVaulted.  # noqa: E501


        :return: The properties of this OrderPaymentCreditCardDualVaulted.  # noqa: E501
        :rtype: list[OrderPaymentCreditCardDualVaultedProperty]
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this OrderPaymentCreditCardDualVaulted.


        :param properties: The properties of this OrderPaymentCreditCardDualVaulted.  # noqa: E501
        :type: list[OrderPaymentCreditCardDualVaultedProperty]
        """

        self._properties = properties

    @property
    def rotating_transaction_gateway_code(self):
        """Gets the rotating_transaction_gateway_code of this OrderPaymentCreditCardDualVaulted.  # noqa: E501


        :return: The rotating_transaction_gateway_code of this OrderPaymentCreditCardDualVaulted.  # noqa: E501
        :rtype: str
        """
        return self._rotating_transaction_gateway_code

    @rotating_transaction_gateway_code.setter
    def rotating_transaction_gateway_code(self, rotating_transaction_gateway_code):
        """Sets the rotating_transaction_gateway_code of this OrderPaymentCreditCardDualVaulted.


        :param rotating_transaction_gateway_code: The rotating_transaction_gateway_code of this OrderPaymentCreditCardDualVaulted.  # noqa: E501
        :type: str
        """

        self._rotating_transaction_gateway_code = rotating_transaction_gateway_code

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
        if issubclass(OrderPaymentCreditCardDualVaulted, dict):
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
        if not isinstance(other, OrderPaymentCreditCardDualVaulted):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
