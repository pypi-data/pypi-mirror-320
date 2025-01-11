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


class CouponMoreLoyaltyCashback(object):
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
        'loyalty_cashback': 'float'
    }

    attribute_map = {
        'loyalty_cashback': 'loyalty_cashback'
    }

    def __init__(self, loyalty_cashback=None):  # noqa: E501
        """CouponMoreLoyaltyCashback - a model defined in Swagger"""  # noqa: E501

        self._loyalty_cashback = None
        self.discriminator = None

        if loyalty_cashback is not None:
            self.loyalty_cashback = loyalty_cashback

    @property
    def loyalty_cashback(self):
        """Gets the loyalty_cashback of this CouponMoreLoyaltyCashback.  # noqa: E501

        The additional loyalty cashback  # noqa: E501

        :return: The loyalty_cashback of this CouponMoreLoyaltyCashback.  # noqa: E501
        :rtype: float
        """
        return self._loyalty_cashback

    @loyalty_cashback.setter
    def loyalty_cashback(self, loyalty_cashback):
        """Sets the loyalty_cashback of this CouponMoreLoyaltyCashback.

        The additional loyalty cashback  # noqa: E501

        :param loyalty_cashback: The loyalty_cashback of this CouponMoreLoyaltyCashback.  # noqa: E501
        :type: float
        """

        self._loyalty_cashback = loyalty_cashback

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
        if issubclass(CouponMoreLoyaltyCashback, dict):
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
        if not isinstance(other, CouponMoreLoyaltyCashback):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
