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


class EmailRateLimiter(object):
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
        'available': 'int',
        'limit': 'int',
        'name': 'str'
    }

    attribute_map = {
        'available': 'available',
        'limit': 'limit',
        'name': 'name'
    }

    def __init__(self, available=None, limit=None, name=None):  # noqa: E501
        """EmailRateLimiter - a model defined in Swagger"""  # noqa: E501

        self._available = None
        self._limit = None
        self._name = None
        self.discriminator = None

        if available is not None:
            self.available = available
        if limit is not None:
            self.limit = limit
        if name is not None:
            self.name = name

    @property
    def available(self):
        """Gets the available of this EmailRateLimiter.  # noqa: E501


        :return: The available of this EmailRateLimiter.  # noqa: E501
        :rtype: int
        """
        return self._available

    @available.setter
    def available(self, available):
        """Sets the available of this EmailRateLimiter.


        :param available: The available of this EmailRateLimiter.  # noqa: E501
        :type: int
        """

        self._available = available

    @property
    def limit(self):
        """Gets the limit of this EmailRateLimiter.  # noqa: E501


        :return: The limit of this EmailRateLimiter.  # noqa: E501
        :rtype: int
        """
        return self._limit

    @limit.setter
    def limit(self, limit):
        """Sets the limit of this EmailRateLimiter.


        :param limit: The limit of this EmailRateLimiter.  # noqa: E501
        :type: int
        """

        self._limit = limit

    @property
    def name(self):
        """Gets the name of this EmailRateLimiter.  # noqa: E501


        :return: The name of this EmailRateLimiter.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this EmailRateLimiter.


        :param name: The name of this EmailRateLimiter.  # noqa: E501
        :type: str
        """

        self._name = name

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
        if issubclass(EmailRateLimiter, dict):
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
        if not isinstance(other, EmailRateLimiter):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
