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


class WebhookLog(object):
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
        'delivery_dts': 'str',
        'duration': 'int',
        'queue_delay': 'int',
        'request': 'str',
        'request_headers': 'list[HTTPHeader]',
        'request_id': 'str',
        'response': 'str',
        'response_headers': 'list[HTTPHeader]',
        'status_code': 'int',
        'success': 'bool',
        'uri': 'str',
        'webhook_oid': 'int'
    }

    attribute_map = {
        'delivery_dts': 'delivery_dts',
        'duration': 'duration',
        'queue_delay': 'queue_delay',
        'request': 'request',
        'request_headers': 'request_headers',
        'request_id': 'request_id',
        'response': 'response',
        'response_headers': 'response_headers',
        'status_code': 'status_code',
        'success': 'success',
        'uri': 'uri',
        'webhook_oid': 'webhook_oid'
    }

    def __init__(self, delivery_dts=None, duration=None, queue_delay=None, request=None, request_headers=None, request_id=None, response=None, response_headers=None, status_code=None, success=None, uri=None, webhook_oid=None):  # noqa: E501
        """WebhookLog - a model defined in Swagger"""  # noqa: E501

        self._delivery_dts = None
        self._duration = None
        self._queue_delay = None
        self._request = None
        self._request_headers = None
        self._request_id = None
        self._response = None
        self._response_headers = None
        self._status_code = None
        self._success = None
        self._uri = None
        self._webhook_oid = None
        self.discriminator = None

        if delivery_dts is not None:
            self.delivery_dts = delivery_dts
        if duration is not None:
            self.duration = duration
        if queue_delay is not None:
            self.queue_delay = queue_delay
        if request is not None:
            self.request = request
        if request_headers is not None:
            self.request_headers = request_headers
        if request_id is not None:
            self.request_id = request_id
        if response is not None:
            self.response = response
        if response_headers is not None:
            self.response_headers = response_headers
        if status_code is not None:
            self.status_code = status_code
        if success is not None:
            self.success = success
        if uri is not None:
            self.uri = uri
        if webhook_oid is not None:
            self.webhook_oid = webhook_oid

    @property
    def delivery_dts(self):
        """Gets the delivery_dts of this WebhookLog.  # noqa: E501

        Date/time of delivery  # noqa: E501

        :return: The delivery_dts of this WebhookLog.  # noqa: E501
        :rtype: str
        """
        return self._delivery_dts

    @delivery_dts.setter
    def delivery_dts(self, delivery_dts):
        """Sets the delivery_dts of this WebhookLog.

        Date/time of delivery  # noqa: E501

        :param delivery_dts: The delivery_dts of this WebhookLog.  # noqa: E501
        :type: str
        """

        self._delivery_dts = delivery_dts

    @property
    def duration(self):
        """Gets the duration of this WebhookLog.  # noqa: E501

        Number of milliseconds to process the notification  # noqa: E501

        :return: The duration of this WebhookLog.  # noqa: E501
        :rtype: int
        """
        return self._duration

    @duration.setter
    def duration(self, duration):
        """Sets the duration of this WebhookLog.

        Number of milliseconds to process the notification  # noqa: E501

        :param duration: The duration of this WebhookLog.  # noqa: E501
        :type: int
        """

        self._duration = duration

    @property
    def queue_delay(self):
        """Gets the queue_delay of this WebhookLog.  # noqa: E501

        Number of milliseconds of delay caused by queuing  # noqa: E501

        :return: The queue_delay of this WebhookLog.  # noqa: E501
        :rtype: int
        """
        return self._queue_delay

    @queue_delay.setter
    def queue_delay(self, queue_delay):
        """Sets the queue_delay of this WebhookLog.

        Number of milliseconds of delay caused by queuing  # noqa: E501

        :param queue_delay: The queue_delay of this WebhookLog.  # noqa: E501
        :type: int
        """

        self._queue_delay = queue_delay

    @property
    def request(self):
        """Gets the request of this WebhookLog.  # noqa: E501

        Request payload (first 100,000 characters)  # noqa: E501

        :return: The request of this WebhookLog.  # noqa: E501
        :rtype: str
        """
        return self._request

    @request.setter
    def request(self, request):
        """Sets the request of this WebhookLog.

        Request payload (first 100,000 characters)  # noqa: E501

        :param request: The request of this WebhookLog.  # noqa: E501
        :type: str
        """

        self._request = request

    @property
    def request_headers(self):
        """Gets the request_headers of this WebhookLog.  # noqa: E501

        Request headers sent to the server  # noqa: E501

        :return: The request_headers of this WebhookLog.  # noqa: E501
        :rtype: list[HTTPHeader]
        """
        return self._request_headers

    @request_headers.setter
    def request_headers(self, request_headers):
        """Sets the request_headers of this WebhookLog.

        Request headers sent to the server  # noqa: E501

        :param request_headers: The request_headers of this WebhookLog.  # noqa: E501
        :type: list[HTTPHeader]
        """

        self._request_headers = request_headers

    @property
    def request_id(self):
        """Gets the request_id of this WebhookLog.  # noqa: E501

        Request id is a unique string that you can look up in the logs  # noqa: E501

        :return: The request_id of this WebhookLog.  # noqa: E501
        :rtype: str
        """
        return self._request_id

    @request_id.setter
    def request_id(self, request_id):
        """Sets the request_id of this WebhookLog.

        Request id is a unique string that you can look up in the logs  # noqa: E501

        :param request_id: The request_id of this WebhookLog.  # noqa: E501
        :type: str
        """

        self._request_id = request_id

    @property
    def response(self):
        """Gets the response of this WebhookLog.  # noqa: E501

        Response payload (first 100,000 characters)  # noqa: E501

        :return: The response of this WebhookLog.  # noqa: E501
        :rtype: str
        """
        return self._response

    @response.setter
    def response(self, response):
        """Sets the response of this WebhookLog.

        Response payload (first 100,000 characters)  # noqa: E501

        :param response: The response of this WebhookLog.  # noqa: E501
        :type: str
        """

        self._response = response

    @property
    def response_headers(self):
        """Gets the response_headers of this WebhookLog.  # noqa: E501

        Response headers received from the server  # noqa: E501

        :return: The response_headers of this WebhookLog.  # noqa: E501
        :rtype: list[HTTPHeader]
        """
        return self._response_headers

    @response_headers.setter
    def response_headers(self, response_headers):
        """Sets the response_headers of this WebhookLog.

        Response headers received from the server  # noqa: E501

        :param response_headers: The response_headers of this WebhookLog.  # noqa: E501
        :type: list[HTTPHeader]
        """

        self._response_headers = response_headers

    @property
    def status_code(self):
        """Gets the status_code of this WebhookLog.  # noqa: E501

        HTTP status code received from the server  # noqa: E501

        :return: The status_code of this WebhookLog.  # noqa: E501
        :rtype: int
        """
        return self._status_code

    @status_code.setter
    def status_code(self, status_code):
        """Sets the status_code of this WebhookLog.

        HTTP status code received from the server  # noqa: E501

        :param status_code: The status_code of this WebhookLog.  # noqa: E501
        :type: int
        """

        self._status_code = status_code

    @property
    def success(self):
        """Gets the success of this WebhookLog.  # noqa: E501

        True if the delivery was successful  # noqa: E501

        :return: The success of this WebhookLog.  # noqa: E501
        :rtype: bool
        """
        return self._success

    @success.setter
    def success(self, success):
        """Sets the success of this WebhookLog.

        True if the delivery was successful  # noqa: E501

        :param success: The success of this WebhookLog.  # noqa: E501
        :type: bool
        """

        self._success = success

    @property
    def uri(self):
        """Gets the uri of this WebhookLog.  # noqa: E501

        URI of the webhook delivered to  # noqa: E501

        :return: The uri of this WebhookLog.  # noqa: E501
        :rtype: str
        """
        return self._uri

    @uri.setter
    def uri(self, uri):
        """Sets the uri of this WebhookLog.

        URI of the webhook delivered to  # noqa: E501

        :param uri: The uri of this WebhookLog.  # noqa: E501
        :type: str
        """

        self._uri = uri

    @property
    def webhook_oid(self):
        """Gets the webhook_oid of this WebhookLog.  # noqa: E501

        webhook oid  # noqa: E501

        :return: The webhook_oid of this WebhookLog.  # noqa: E501
        :rtype: int
        """
        return self._webhook_oid

    @webhook_oid.setter
    def webhook_oid(self, webhook_oid):
        """Sets the webhook_oid of this WebhookLog.

        webhook oid  # noqa: E501

        :param webhook_oid: The webhook_oid of this WebhookLog.  # noqa: E501
        :type: int
        """

        self._webhook_oid = webhook_oid

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
        if issubclass(WebhookLog, dict):
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
        if not isinstance(other, WebhookLog):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
