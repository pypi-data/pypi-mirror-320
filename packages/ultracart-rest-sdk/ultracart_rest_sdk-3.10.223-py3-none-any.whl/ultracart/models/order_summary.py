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


class OrderSummary(object):
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
        'actual_fulfillment': 'Currency',
        'actual_payment_processing': 'Currency',
        'actual_shipping': 'Currency',
        'arbitrary_shipping_handling_total': 'Currency',
        'health_benefit_card_amount': 'Currency',
        'health_benefit_card_refunded': 'Currency',
        'internal_gift_certificate_amount': 'Currency',
        'internal_gift_certificate_refunded': 'Currency',
        'other_refunded': 'Currency',
        'shipping_handling_refunded': 'Currency',
        'shipping_handling_total': 'Currency',
        'shipping_handling_total_discount': 'Currency',
        'subtotal': 'Currency',
        'subtotal_discount': 'Currency',
        'subtotal_discount_refunded': 'Currency',
        'subtotal_refunded': 'Currency',
        'tax': 'Currency',
        'tax_refunded': 'Currency',
        'taxable_subtotal': 'Currency',
        'taxable_subtotal_discount': 'Currency',
        'total': 'Currency',
        'total_refunded': 'Currency'
    }

    attribute_map = {
        'actual_fulfillment': 'actual_fulfillment',
        'actual_payment_processing': 'actual_payment_processing',
        'actual_shipping': 'actual_shipping',
        'arbitrary_shipping_handling_total': 'arbitrary_shipping_handling_total',
        'health_benefit_card_amount': 'health_benefit_card_amount',
        'health_benefit_card_refunded': 'health_benefit_card_refunded',
        'internal_gift_certificate_amount': 'internal_gift_certificate_amount',
        'internal_gift_certificate_refunded': 'internal_gift_certificate_refunded',
        'other_refunded': 'other_refunded',
        'shipping_handling_refunded': 'shipping_handling_refunded',
        'shipping_handling_total': 'shipping_handling_total',
        'shipping_handling_total_discount': 'shipping_handling_total_discount',
        'subtotal': 'subtotal',
        'subtotal_discount': 'subtotal_discount',
        'subtotal_discount_refunded': 'subtotal_discount_refunded',
        'subtotal_refunded': 'subtotal_refunded',
        'tax': 'tax',
        'tax_refunded': 'tax_refunded',
        'taxable_subtotal': 'taxable_subtotal',
        'taxable_subtotal_discount': 'taxable_subtotal_discount',
        'total': 'total',
        'total_refunded': 'total_refunded'
    }

    def __init__(self, actual_fulfillment=None, actual_payment_processing=None, actual_shipping=None, arbitrary_shipping_handling_total=None, health_benefit_card_amount=None, health_benefit_card_refunded=None, internal_gift_certificate_amount=None, internal_gift_certificate_refunded=None, other_refunded=None, shipping_handling_refunded=None, shipping_handling_total=None, shipping_handling_total_discount=None, subtotal=None, subtotal_discount=None, subtotal_discount_refunded=None, subtotal_refunded=None, tax=None, tax_refunded=None, taxable_subtotal=None, taxable_subtotal_discount=None, total=None, total_refunded=None):  # noqa: E501
        """OrderSummary - a model defined in Swagger"""  # noqa: E501

        self._actual_fulfillment = None
        self._actual_payment_processing = None
        self._actual_shipping = None
        self._arbitrary_shipping_handling_total = None
        self._health_benefit_card_amount = None
        self._health_benefit_card_refunded = None
        self._internal_gift_certificate_amount = None
        self._internal_gift_certificate_refunded = None
        self._other_refunded = None
        self._shipping_handling_refunded = None
        self._shipping_handling_total = None
        self._shipping_handling_total_discount = None
        self._subtotal = None
        self._subtotal_discount = None
        self._subtotal_discount_refunded = None
        self._subtotal_refunded = None
        self._tax = None
        self._tax_refunded = None
        self._taxable_subtotal = None
        self._taxable_subtotal_discount = None
        self._total = None
        self._total_refunded = None
        self.discriminator = None

        if actual_fulfillment is not None:
            self.actual_fulfillment = actual_fulfillment
        if actual_payment_processing is not None:
            self.actual_payment_processing = actual_payment_processing
        if actual_shipping is not None:
            self.actual_shipping = actual_shipping
        if arbitrary_shipping_handling_total is not None:
            self.arbitrary_shipping_handling_total = arbitrary_shipping_handling_total
        if health_benefit_card_amount is not None:
            self.health_benefit_card_amount = health_benefit_card_amount
        if health_benefit_card_refunded is not None:
            self.health_benefit_card_refunded = health_benefit_card_refunded
        if internal_gift_certificate_amount is not None:
            self.internal_gift_certificate_amount = internal_gift_certificate_amount
        if internal_gift_certificate_refunded is not None:
            self.internal_gift_certificate_refunded = internal_gift_certificate_refunded
        if other_refunded is not None:
            self.other_refunded = other_refunded
        if shipping_handling_refunded is not None:
            self.shipping_handling_refunded = shipping_handling_refunded
        if shipping_handling_total is not None:
            self.shipping_handling_total = shipping_handling_total
        if shipping_handling_total_discount is not None:
            self.shipping_handling_total_discount = shipping_handling_total_discount
        if subtotal is not None:
            self.subtotal = subtotal
        if subtotal_discount is not None:
            self.subtotal_discount = subtotal_discount
        if subtotal_discount_refunded is not None:
            self.subtotal_discount_refunded = subtotal_discount_refunded
        if subtotal_refunded is not None:
            self.subtotal_refunded = subtotal_refunded
        if tax is not None:
            self.tax = tax
        if tax_refunded is not None:
            self.tax_refunded = tax_refunded
        if taxable_subtotal is not None:
            self.taxable_subtotal = taxable_subtotal
        if taxable_subtotal_discount is not None:
            self.taxable_subtotal_discount = taxable_subtotal_discount
        if total is not None:
            self.total = total
        if total_refunded is not None:
            self.total_refunded = total_refunded

    @property
    def actual_fulfillment(self):
        """Gets the actual_fulfillment of this OrderSummary.  # noqa: E501


        :return: The actual_fulfillment of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._actual_fulfillment

    @actual_fulfillment.setter
    def actual_fulfillment(self, actual_fulfillment):
        """Sets the actual_fulfillment of this OrderSummary.


        :param actual_fulfillment: The actual_fulfillment of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._actual_fulfillment = actual_fulfillment

    @property
    def actual_payment_processing(self):
        """Gets the actual_payment_processing of this OrderSummary.  # noqa: E501


        :return: The actual_payment_processing of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._actual_payment_processing

    @actual_payment_processing.setter
    def actual_payment_processing(self, actual_payment_processing):
        """Sets the actual_payment_processing of this OrderSummary.


        :param actual_payment_processing: The actual_payment_processing of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._actual_payment_processing = actual_payment_processing

    @property
    def actual_shipping(self):
        """Gets the actual_shipping of this OrderSummary.  # noqa: E501


        :return: The actual_shipping of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._actual_shipping

    @actual_shipping.setter
    def actual_shipping(self, actual_shipping):
        """Sets the actual_shipping of this OrderSummary.


        :param actual_shipping: The actual_shipping of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._actual_shipping = actual_shipping

    @property
    def arbitrary_shipping_handling_total(self):
        """Gets the arbitrary_shipping_handling_total of this OrderSummary.  # noqa: E501


        :return: The arbitrary_shipping_handling_total of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._arbitrary_shipping_handling_total

    @arbitrary_shipping_handling_total.setter
    def arbitrary_shipping_handling_total(self, arbitrary_shipping_handling_total):
        """Sets the arbitrary_shipping_handling_total of this OrderSummary.


        :param arbitrary_shipping_handling_total: The arbitrary_shipping_handling_total of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._arbitrary_shipping_handling_total = arbitrary_shipping_handling_total

    @property
    def health_benefit_card_amount(self):
        """Gets the health_benefit_card_amount of this OrderSummary.  # noqa: E501


        :return: The health_benefit_card_amount of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._health_benefit_card_amount

    @health_benefit_card_amount.setter
    def health_benefit_card_amount(self, health_benefit_card_amount):
        """Sets the health_benefit_card_amount of this OrderSummary.


        :param health_benefit_card_amount: The health_benefit_card_amount of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._health_benefit_card_amount = health_benefit_card_amount

    @property
    def health_benefit_card_refunded(self):
        """Gets the health_benefit_card_refunded of this OrderSummary.  # noqa: E501


        :return: The health_benefit_card_refunded of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._health_benefit_card_refunded

    @health_benefit_card_refunded.setter
    def health_benefit_card_refunded(self, health_benefit_card_refunded):
        """Sets the health_benefit_card_refunded of this OrderSummary.


        :param health_benefit_card_refunded: The health_benefit_card_refunded of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._health_benefit_card_refunded = health_benefit_card_refunded

    @property
    def internal_gift_certificate_amount(self):
        """Gets the internal_gift_certificate_amount of this OrderSummary.  # noqa: E501


        :return: The internal_gift_certificate_amount of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._internal_gift_certificate_amount

    @internal_gift_certificate_amount.setter
    def internal_gift_certificate_amount(self, internal_gift_certificate_amount):
        """Sets the internal_gift_certificate_amount of this OrderSummary.


        :param internal_gift_certificate_amount: The internal_gift_certificate_amount of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._internal_gift_certificate_amount = internal_gift_certificate_amount

    @property
    def internal_gift_certificate_refunded(self):
        """Gets the internal_gift_certificate_refunded of this OrderSummary.  # noqa: E501


        :return: The internal_gift_certificate_refunded of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._internal_gift_certificate_refunded

    @internal_gift_certificate_refunded.setter
    def internal_gift_certificate_refunded(self, internal_gift_certificate_refunded):
        """Sets the internal_gift_certificate_refunded of this OrderSummary.


        :param internal_gift_certificate_refunded: The internal_gift_certificate_refunded of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._internal_gift_certificate_refunded = internal_gift_certificate_refunded

    @property
    def other_refunded(self):
        """Gets the other_refunded of this OrderSummary.  # noqa: E501


        :return: The other_refunded of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._other_refunded

    @other_refunded.setter
    def other_refunded(self, other_refunded):
        """Sets the other_refunded of this OrderSummary.


        :param other_refunded: The other_refunded of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._other_refunded = other_refunded

    @property
    def shipping_handling_refunded(self):
        """Gets the shipping_handling_refunded of this OrderSummary.  # noqa: E501


        :return: The shipping_handling_refunded of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._shipping_handling_refunded

    @shipping_handling_refunded.setter
    def shipping_handling_refunded(self, shipping_handling_refunded):
        """Sets the shipping_handling_refunded of this OrderSummary.


        :param shipping_handling_refunded: The shipping_handling_refunded of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._shipping_handling_refunded = shipping_handling_refunded

    @property
    def shipping_handling_total(self):
        """Gets the shipping_handling_total of this OrderSummary.  # noqa: E501


        :return: The shipping_handling_total of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._shipping_handling_total

    @shipping_handling_total.setter
    def shipping_handling_total(self, shipping_handling_total):
        """Sets the shipping_handling_total of this OrderSummary.


        :param shipping_handling_total: The shipping_handling_total of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._shipping_handling_total = shipping_handling_total

    @property
    def shipping_handling_total_discount(self):
        """Gets the shipping_handling_total_discount of this OrderSummary.  # noqa: E501


        :return: The shipping_handling_total_discount of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._shipping_handling_total_discount

    @shipping_handling_total_discount.setter
    def shipping_handling_total_discount(self, shipping_handling_total_discount):
        """Sets the shipping_handling_total_discount of this OrderSummary.


        :param shipping_handling_total_discount: The shipping_handling_total_discount of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._shipping_handling_total_discount = shipping_handling_total_discount

    @property
    def subtotal(self):
        """Gets the subtotal of this OrderSummary.  # noqa: E501


        :return: The subtotal of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._subtotal

    @subtotal.setter
    def subtotal(self, subtotal):
        """Sets the subtotal of this OrderSummary.


        :param subtotal: The subtotal of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._subtotal = subtotal

    @property
    def subtotal_discount(self):
        """Gets the subtotal_discount of this OrderSummary.  # noqa: E501


        :return: The subtotal_discount of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._subtotal_discount

    @subtotal_discount.setter
    def subtotal_discount(self, subtotal_discount):
        """Sets the subtotal_discount of this OrderSummary.


        :param subtotal_discount: The subtotal_discount of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._subtotal_discount = subtotal_discount

    @property
    def subtotal_discount_refunded(self):
        """Gets the subtotal_discount_refunded of this OrderSummary.  # noqa: E501


        :return: The subtotal_discount_refunded of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._subtotal_discount_refunded

    @subtotal_discount_refunded.setter
    def subtotal_discount_refunded(self, subtotal_discount_refunded):
        """Sets the subtotal_discount_refunded of this OrderSummary.


        :param subtotal_discount_refunded: The subtotal_discount_refunded of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._subtotal_discount_refunded = subtotal_discount_refunded

    @property
    def subtotal_refunded(self):
        """Gets the subtotal_refunded of this OrderSummary.  # noqa: E501


        :return: The subtotal_refunded of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._subtotal_refunded

    @subtotal_refunded.setter
    def subtotal_refunded(self, subtotal_refunded):
        """Sets the subtotal_refunded of this OrderSummary.


        :param subtotal_refunded: The subtotal_refunded of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._subtotal_refunded = subtotal_refunded

    @property
    def tax(self):
        """Gets the tax of this OrderSummary.  # noqa: E501


        :return: The tax of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._tax

    @tax.setter
    def tax(self, tax):
        """Sets the tax of this OrderSummary.


        :param tax: The tax of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._tax = tax

    @property
    def tax_refunded(self):
        """Gets the tax_refunded of this OrderSummary.  # noqa: E501


        :return: The tax_refunded of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._tax_refunded

    @tax_refunded.setter
    def tax_refunded(self, tax_refunded):
        """Sets the tax_refunded of this OrderSummary.


        :param tax_refunded: The tax_refunded of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._tax_refunded = tax_refunded

    @property
    def taxable_subtotal(self):
        """Gets the taxable_subtotal of this OrderSummary.  # noqa: E501


        :return: The taxable_subtotal of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._taxable_subtotal

    @taxable_subtotal.setter
    def taxable_subtotal(self, taxable_subtotal):
        """Sets the taxable_subtotal of this OrderSummary.


        :param taxable_subtotal: The taxable_subtotal of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._taxable_subtotal = taxable_subtotal

    @property
    def taxable_subtotal_discount(self):
        """Gets the taxable_subtotal_discount of this OrderSummary.  # noqa: E501


        :return: The taxable_subtotal_discount of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._taxable_subtotal_discount

    @taxable_subtotal_discount.setter
    def taxable_subtotal_discount(self, taxable_subtotal_discount):
        """Sets the taxable_subtotal_discount of this OrderSummary.


        :param taxable_subtotal_discount: The taxable_subtotal_discount of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._taxable_subtotal_discount = taxable_subtotal_discount

    @property
    def total(self):
        """Gets the total of this OrderSummary.  # noqa: E501


        :return: The total of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._total

    @total.setter
    def total(self, total):
        """Sets the total of this OrderSummary.


        :param total: The total of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._total = total

    @property
    def total_refunded(self):
        """Gets the total_refunded of this OrderSummary.  # noqa: E501


        :return: The total_refunded of this OrderSummary.  # noqa: E501
        :rtype: Currency
        """
        return self._total_refunded

    @total_refunded.setter
    def total_refunded(self, total_refunded):
        """Sets the total_refunded of this OrderSummary.


        :param total_refunded: The total_refunded of this OrderSummary.  # noqa: E501
        :type: Currency
        """

        self._total_refunded = total_refunded

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
        if issubclass(OrderSummary, dict):
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
        if not isinstance(other, OrderSummary):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
