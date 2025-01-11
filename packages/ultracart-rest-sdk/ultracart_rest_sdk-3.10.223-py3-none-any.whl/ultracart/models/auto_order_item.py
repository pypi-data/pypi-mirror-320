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


class AutoOrderItem(object):
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
        'arbitrary_item_id': 'str',
        'arbitrary_percentage_discount': 'float',
        'arbitrary_quantity': 'float',
        'arbitrary_schedule_days': 'int',
        'arbitrary_unit_cost': 'float',
        'arbitrary_unit_cost_remaining_orders': 'int',
        'auto_order_item_oid': 'int',
        'calculated_next_shipment_dts': 'str',
        'first_order_dts': 'str',
        'frequency': 'str',
        'future_schedules': 'list[AutoOrderItemFutureSchedule]',
        'last_order_dts': 'str',
        'life_time_value': 'float',
        'next_item_id': 'str',
        'next_preshipment_notice_dts': 'str',
        'next_shipment_dts': 'str',
        'no_order_after_dts': 'str',
        'number_of_rebills': 'int',
        'options': 'list[AutoOrderItemOption]',
        'original_item_id': 'str',
        'original_quantity': 'float',
        'paused': 'bool',
        'paypal_payer_id': 'str',
        'paypal_recurring_payment_profile_id': 'str',
        'preshipment_notice_sent': 'bool',
        'rebill_value': 'float',
        'remaining_repeat_count': 'int',
        'simple_schedule': 'AutoOrderItemSimpleSchedule'
    }

    attribute_map = {
        'arbitrary_item_id': 'arbitrary_item_id',
        'arbitrary_percentage_discount': 'arbitrary_percentage_discount',
        'arbitrary_quantity': 'arbitrary_quantity',
        'arbitrary_schedule_days': 'arbitrary_schedule_days',
        'arbitrary_unit_cost': 'arbitrary_unit_cost',
        'arbitrary_unit_cost_remaining_orders': 'arbitrary_unit_cost_remaining_orders',
        'auto_order_item_oid': 'auto_order_item_oid',
        'calculated_next_shipment_dts': 'calculated_next_shipment_dts',
        'first_order_dts': 'first_order_dts',
        'frequency': 'frequency',
        'future_schedules': 'future_schedules',
        'last_order_dts': 'last_order_dts',
        'life_time_value': 'life_time_value',
        'next_item_id': 'next_item_id',
        'next_preshipment_notice_dts': 'next_preshipment_notice_dts',
        'next_shipment_dts': 'next_shipment_dts',
        'no_order_after_dts': 'no_order_after_dts',
        'number_of_rebills': 'number_of_rebills',
        'options': 'options',
        'original_item_id': 'original_item_id',
        'original_quantity': 'original_quantity',
        'paused': 'paused',
        'paypal_payer_id': 'paypal_payer_id',
        'paypal_recurring_payment_profile_id': 'paypal_recurring_payment_profile_id',
        'preshipment_notice_sent': 'preshipment_notice_sent',
        'rebill_value': 'rebill_value',
        'remaining_repeat_count': 'remaining_repeat_count',
        'simple_schedule': 'simple_schedule'
    }

    def __init__(self, arbitrary_item_id=None, arbitrary_percentage_discount=None, arbitrary_quantity=None, arbitrary_schedule_days=None, arbitrary_unit_cost=None, arbitrary_unit_cost_remaining_orders=None, auto_order_item_oid=None, calculated_next_shipment_dts=None, first_order_dts=None, frequency=None, future_schedules=None, last_order_dts=None, life_time_value=None, next_item_id=None, next_preshipment_notice_dts=None, next_shipment_dts=None, no_order_after_dts=None, number_of_rebills=None, options=None, original_item_id=None, original_quantity=None, paused=None, paypal_payer_id=None, paypal_recurring_payment_profile_id=None, preshipment_notice_sent=None, rebill_value=None, remaining_repeat_count=None, simple_schedule=None):  # noqa: E501
        """AutoOrderItem - a model defined in Swagger"""  # noqa: E501

        self._arbitrary_item_id = None
        self._arbitrary_percentage_discount = None
        self._arbitrary_quantity = None
        self._arbitrary_schedule_days = None
        self._arbitrary_unit_cost = None
        self._arbitrary_unit_cost_remaining_orders = None
        self._auto_order_item_oid = None
        self._calculated_next_shipment_dts = None
        self._first_order_dts = None
        self._frequency = None
        self._future_schedules = None
        self._last_order_dts = None
        self._life_time_value = None
        self._next_item_id = None
        self._next_preshipment_notice_dts = None
        self._next_shipment_dts = None
        self._no_order_after_dts = None
        self._number_of_rebills = None
        self._options = None
        self._original_item_id = None
        self._original_quantity = None
        self._paused = None
        self._paypal_payer_id = None
        self._paypal_recurring_payment_profile_id = None
        self._preshipment_notice_sent = None
        self._rebill_value = None
        self._remaining_repeat_count = None
        self._simple_schedule = None
        self.discriminator = None

        if arbitrary_item_id is not None:
            self.arbitrary_item_id = arbitrary_item_id
        if arbitrary_percentage_discount is not None:
            self.arbitrary_percentage_discount = arbitrary_percentage_discount
        if arbitrary_quantity is not None:
            self.arbitrary_quantity = arbitrary_quantity
        if arbitrary_schedule_days is not None:
            self.arbitrary_schedule_days = arbitrary_schedule_days
        if arbitrary_unit_cost is not None:
            self.arbitrary_unit_cost = arbitrary_unit_cost
        if arbitrary_unit_cost_remaining_orders is not None:
            self.arbitrary_unit_cost_remaining_orders = arbitrary_unit_cost_remaining_orders
        if auto_order_item_oid is not None:
            self.auto_order_item_oid = auto_order_item_oid
        if calculated_next_shipment_dts is not None:
            self.calculated_next_shipment_dts = calculated_next_shipment_dts
        if first_order_dts is not None:
            self.first_order_dts = first_order_dts
        if frequency is not None:
            self.frequency = frequency
        if future_schedules is not None:
            self.future_schedules = future_schedules
        if last_order_dts is not None:
            self.last_order_dts = last_order_dts
        if life_time_value is not None:
            self.life_time_value = life_time_value
        if next_item_id is not None:
            self.next_item_id = next_item_id
        if next_preshipment_notice_dts is not None:
            self.next_preshipment_notice_dts = next_preshipment_notice_dts
        if next_shipment_dts is not None:
            self.next_shipment_dts = next_shipment_dts
        if no_order_after_dts is not None:
            self.no_order_after_dts = no_order_after_dts
        if number_of_rebills is not None:
            self.number_of_rebills = number_of_rebills
        if options is not None:
            self.options = options
        if original_item_id is not None:
            self.original_item_id = original_item_id
        if original_quantity is not None:
            self.original_quantity = original_quantity
        if paused is not None:
            self.paused = paused
        if paypal_payer_id is not None:
            self.paypal_payer_id = paypal_payer_id
        if paypal_recurring_payment_profile_id is not None:
            self.paypal_recurring_payment_profile_id = paypal_recurring_payment_profile_id
        if preshipment_notice_sent is not None:
            self.preshipment_notice_sent = preshipment_notice_sent
        if rebill_value is not None:
            self.rebill_value = rebill_value
        if remaining_repeat_count is not None:
            self.remaining_repeat_count = remaining_repeat_count
        if simple_schedule is not None:
            self.simple_schedule = simple_schedule

    @property
    def arbitrary_item_id(self):
        """Gets the arbitrary_item_id of this AutoOrderItem.  # noqa: E501

        Arbitrary item id that should be rebilled instead of the normal schedule  # noqa: E501

        :return: The arbitrary_item_id of this AutoOrderItem.  # noqa: E501
        :rtype: str
        """
        return self._arbitrary_item_id

    @arbitrary_item_id.setter
    def arbitrary_item_id(self, arbitrary_item_id):
        """Sets the arbitrary_item_id of this AutoOrderItem.

        Arbitrary item id that should be rebilled instead of the normal schedule  # noqa: E501

        :param arbitrary_item_id: The arbitrary_item_id of this AutoOrderItem.  # noqa: E501
        :type: str
        """

        self._arbitrary_item_id = arbitrary_item_id

    @property
    def arbitrary_percentage_discount(self):
        """Gets the arbitrary_percentage_discount of this AutoOrderItem.  # noqa: E501

        An arbitrary percentage discount to provide on future rebills  # noqa: E501

        :return: The arbitrary_percentage_discount of this AutoOrderItem.  # noqa: E501
        :rtype: float
        """
        return self._arbitrary_percentage_discount

    @arbitrary_percentage_discount.setter
    def arbitrary_percentage_discount(self, arbitrary_percentage_discount):
        """Sets the arbitrary_percentage_discount of this AutoOrderItem.

        An arbitrary percentage discount to provide on future rebills  # noqa: E501

        :param arbitrary_percentage_discount: The arbitrary_percentage_discount of this AutoOrderItem.  # noqa: E501
        :type: float
        """

        self._arbitrary_percentage_discount = arbitrary_percentage_discount

    @property
    def arbitrary_quantity(self):
        """Gets the arbitrary_quantity of this AutoOrderItem.  # noqa: E501

        Arbitrary quantity to rebill  # noqa: E501

        :return: The arbitrary_quantity of this AutoOrderItem.  # noqa: E501
        :rtype: float
        """
        return self._arbitrary_quantity

    @arbitrary_quantity.setter
    def arbitrary_quantity(self, arbitrary_quantity):
        """Sets the arbitrary_quantity of this AutoOrderItem.

        Arbitrary quantity to rebill  # noqa: E501

        :param arbitrary_quantity: The arbitrary_quantity of this AutoOrderItem.  # noqa: E501
        :type: float
        """

        self._arbitrary_quantity = arbitrary_quantity

    @property
    def arbitrary_schedule_days(self):
        """Gets the arbitrary_schedule_days of this AutoOrderItem.  # noqa: E501

        The number of days to rebill if the frequency is set to an arbitrary number of days  # noqa: E501

        :return: The arbitrary_schedule_days of this AutoOrderItem.  # noqa: E501
        :rtype: int
        """
        return self._arbitrary_schedule_days

    @arbitrary_schedule_days.setter
    def arbitrary_schedule_days(self, arbitrary_schedule_days):
        """Sets the arbitrary_schedule_days of this AutoOrderItem.

        The number of days to rebill if the frequency is set to an arbitrary number of days  # noqa: E501

        :param arbitrary_schedule_days: The arbitrary_schedule_days of this AutoOrderItem.  # noqa: E501
        :type: int
        """

        self._arbitrary_schedule_days = arbitrary_schedule_days

    @property
    def arbitrary_unit_cost(self):
        """Gets the arbitrary_unit_cost of this AutoOrderItem.  # noqa: E501

        Arbitrary unit cost that rebills of this item should occur at  # noqa: E501

        :return: The arbitrary_unit_cost of this AutoOrderItem.  # noqa: E501
        :rtype: float
        """
        return self._arbitrary_unit_cost

    @arbitrary_unit_cost.setter
    def arbitrary_unit_cost(self, arbitrary_unit_cost):
        """Sets the arbitrary_unit_cost of this AutoOrderItem.

        Arbitrary unit cost that rebills of this item should occur at  # noqa: E501

        :param arbitrary_unit_cost: The arbitrary_unit_cost of this AutoOrderItem.  # noqa: E501
        :type: float
        """

        self._arbitrary_unit_cost = arbitrary_unit_cost

    @property
    def arbitrary_unit_cost_remaining_orders(self):
        """Gets the arbitrary_unit_cost_remaining_orders of this AutoOrderItem.  # noqa: E501

        The number of rebills to give the arbitrary unit cost on before reverting to normal pricing.  # noqa: E501

        :return: The arbitrary_unit_cost_remaining_orders of this AutoOrderItem.  # noqa: E501
        :rtype: int
        """
        return self._arbitrary_unit_cost_remaining_orders

    @arbitrary_unit_cost_remaining_orders.setter
    def arbitrary_unit_cost_remaining_orders(self, arbitrary_unit_cost_remaining_orders):
        """Sets the arbitrary_unit_cost_remaining_orders of this AutoOrderItem.

        The number of rebills to give the arbitrary unit cost on before reverting to normal pricing.  # noqa: E501

        :param arbitrary_unit_cost_remaining_orders: The arbitrary_unit_cost_remaining_orders of this AutoOrderItem.  # noqa: E501
        :type: int
        """

        self._arbitrary_unit_cost_remaining_orders = arbitrary_unit_cost_remaining_orders

    @property
    def auto_order_item_oid(self):
        """Gets the auto_order_item_oid of this AutoOrderItem.  # noqa: E501

        Primary key of AutoOrderItem  # noqa: E501

        :return: The auto_order_item_oid of this AutoOrderItem.  # noqa: E501
        :rtype: int
        """
        return self._auto_order_item_oid

    @auto_order_item_oid.setter
    def auto_order_item_oid(self, auto_order_item_oid):
        """Sets the auto_order_item_oid of this AutoOrderItem.

        Primary key of AutoOrderItem  # noqa: E501

        :param auto_order_item_oid: The auto_order_item_oid of this AutoOrderItem.  # noqa: E501
        :type: int
        """

        self._auto_order_item_oid = auto_order_item_oid

    @property
    def calculated_next_shipment_dts(self):
        """Gets the calculated_next_shipment_dts of this AutoOrderItem.  # noqa: E501

        Calculated Date/time that this item is scheduled to rebill.  Will be null if no more shipments are going to occur on this item  # noqa: E501

        :return: The calculated_next_shipment_dts of this AutoOrderItem.  # noqa: E501
        :rtype: str
        """
        return self._calculated_next_shipment_dts

    @calculated_next_shipment_dts.setter
    def calculated_next_shipment_dts(self, calculated_next_shipment_dts):
        """Sets the calculated_next_shipment_dts of this AutoOrderItem.

        Calculated Date/time that this item is scheduled to rebill.  Will be null if no more shipments are going to occur on this item  # noqa: E501

        :param calculated_next_shipment_dts: The calculated_next_shipment_dts of this AutoOrderItem.  # noqa: E501
        :type: str
        """

        self._calculated_next_shipment_dts = calculated_next_shipment_dts

    @property
    def first_order_dts(self):
        """Gets the first_order_dts of this AutoOrderItem.  # noqa: E501

        Date/time of the first order of this item.  Null if item added to auto order and has not been rebilled yet.  # noqa: E501

        :return: The first_order_dts of this AutoOrderItem.  # noqa: E501
        :rtype: str
        """
        return self._first_order_dts

    @first_order_dts.setter
    def first_order_dts(self, first_order_dts):
        """Sets the first_order_dts of this AutoOrderItem.

        Date/time of the first order of this item.  Null if item added to auto order and has not been rebilled yet.  # noqa: E501

        :param first_order_dts: The first_order_dts of this AutoOrderItem.  # noqa: E501
        :type: str
        """

        self._first_order_dts = first_order_dts

    @property
    def frequency(self):
        """Gets the frequency of this AutoOrderItem.  # noqa: E501

        Frequency of the rebill if not a fixed schedule  # noqa: E501

        :return: The frequency of this AutoOrderItem.  # noqa: E501
        :rtype: str
        """
        return self._frequency

    @frequency.setter
    def frequency(self, frequency):
        """Sets the frequency of this AutoOrderItem.

        Frequency of the rebill if not a fixed schedule  # noqa: E501

        :param frequency: The frequency of this AutoOrderItem.  # noqa: E501
        :type: str
        """
        allowed_values = ["Weekly", "Biweekly", "Every...", "Every 10 Days", "Every 24 Days", "Every 28 Days", "Monthly", "Every 45 Days", "Every 2 Months", "Every 3 Months", "Every 4 Months", "Every 5 Months", "Every 6 Months", "Yearly", "Every 4 Weeks", "Every 6 Weeks", "Every 8 Weeks"]  # noqa: E501
        if frequency not in allowed_values:
            raise ValueError(
                "Invalid value for `frequency` ({0}), must be one of {1}"  # noqa: E501
                .format(frequency, allowed_values)
            )

        self._frequency = frequency

    @property
    def future_schedules(self):
        """Gets the future_schedules of this AutoOrderItem.  # noqa: E501

        The future rebill schedule for this item up to the next ten rebills  # noqa: E501

        :return: The future_schedules of this AutoOrderItem.  # noqa: E501
        :rtype: list[AutoOrderItemFutureSchedule]
        """
        return self._future_schedules

    @future_schedules.setter
    def future_schedules(self, future_schedules):
        """Sets the future_schedules of this AutoOrderItem.

        The future rebill schedule for this item up to the next ten rebills  # noqa: E501

        :param future_schedules: The future_schedules of this AutoOrderItem.  # noqa: E501
        :type: list[AutoOrderItemFutureSchedule]
        """

        self._future_schedules = future_schedules

    @property
    def last_order_dts(self):
        """Gets the last_order_dts of this AutoOrderItem.  # noqa: E501

        Date/time of the last order of this item  # noqa: E501

        :return: The last_order_dts of this AutoOrderItem.  # noqa: E501
        :rtype: str
        """
        return self._last_order_dts

    @last_order_dts.setter
    def last_order_dts(self, last_order_dts):
        """Sets the last_order_dts of this AutoOrderItem.

        Date/time of the last order of this item  # noqa: E501

        :param last_order_dts: The last_order_dts of this AutoOrderItem.  # noqa: E501
        :type: str
        """

        self._last_order_dts = last_order_dts

    @property
    def life_time_value(self):
        """Gets the life_time_value of this AutoOrderItem.  # noqa: E501

        The life time value of this item including the original purchase  # noqa: E501

        :return: The life_time_value of this AutoOrderItem.  # noqa: E501
        :rtype: float
        """
        return self._life_time_value

    @life_time_value.setter
    def life_time_value(self, life_time_value):
        """Sets the life_time_value of this AutoOrderItem.

        The life time value of this item including the original purchase  # noqa: E501

        :param life_time_value: The life_time_value of this AutoOrderItem.  # noqa: E501
        :type: float
        """

        self._life_time_value = life_time_value

    @property
    def next_item_id(self):
        """Gets the next_item_id of this AutoOrderItem.  # noqa: E501

        Calculated next item id  # noqa: E501

        :return: The next_item_id of this AutoOrderItem.  # noqa: E501
        :rtype: str
        """
        return self._next_item_id

    @next_item_id.setter
    def next_item_id(self, next_item_id):
        """Sets the next_item_id of this AutoOrderItem.

        Calculated next item id  # noqa: E501

        :param next_item_id: The next_item_id of this AutoOrderItem.  # noqa: E501
        :type: str
        """

        self._next_item_id = next_item_id

    @property
    def next_preshipment_notice_dts(self):
        """Gets the next_preshipment_notice_dts of this AutoOrderItem.  # noqa: E501

        The date/time of when the next pre-shipment notice should be sent  # noqa: E501

        :return: The next_preshipment_notice_dts of this AutoOrderItem.  # noqa: E501
        :rtype: str
        """
        return self._next_preshipment_notice_dts

    @next_preshipment_notice_dts.setter
    def next_preshipment_notice_dts(self, next_preshipment_notice_dts):
        """Sets the next_preshipment_notice_dts of this AutoOrderItem.

        The date/time of when the next pre-shipment notice should be sent  # noqa: E501

        :param next_preshipment_notice_dts: The next_preshipment_notice_dts of this AutoOrderItem.  # noqa: E501
        :type: str
        """

        self._next_preshipment_notice_dts = next_preshipment_notice_dts

    @property
    def next_shipment_dts(self):
        """Gets the next_shipment_dts of this AutoOrderItem.  # noqa: E501

        Date/time that this item is scheduled to rebill  # noqa: E501

        :return: The next_shipment_dts of this AutoOrderItem.  # noqa: E501
        :rtype: str
        """
        return self._next_shipment_dts

    @next_shipment_dts.setter
    def next_shipment_dts(self, next_shipment_dts):
        """Sets the next_shipment_dts of this AutoOrderItem.

        Date/time that this item is scheduled to rebill  # noqa: E501

        :param next_shipment_dts: The next_shipment_dts of this AutoOrderItem.  # noqa: E501
        :type: str
        """

        self._next_shipment_dts = next_shipment_dts

    @property
    def no_order_after_dts(self):
        """Gets the no_order_after_dts of this AutoOrderItem.  # noqa: E501

        Date/time after which no additional rebills of this item should occur  # noqa: E501

        :return: The no_order_after_dts of this AutoOrderItem.  # noqa: E501
        :rtype: str
        """
        return self._no_order_after_dts

    @no_order_after_dts.setter
    def no_order_after_dts(self, no_order_after_dts):
        """Sets the no_order_after_dts of this AutoOrderItem.

        Date/time after which no additional rebills of this item should occur  # noqa: E501

        :param no_order_after_dts: The no_order_after_dts of this AutoOrderItem.  # noqa: E501
        :type: str
        """

        self._no_order_after_dts = no_order_after_dts

    @property
    def number_of_rebills(self):
        """Gets the number_of_rebills of this AutoOrderItem.  # noqa: E501

        The number of times this item has rebilled  # noqa: E501

        :return: The number_of_rebills of this AutoOrderItem.  # noqa: E501
        :rtype: int
        """
        return self._number_of_rebills

    @number_of_rebills.setter
    def number_of_rebills(self, number_of_rebills):
        """Sets the number_of_rebills of this AutoOrderItem.

        The number of times this item has rebilled  # noqa: E501

        :param number_of_rebills: The number_of_rebills of this AutoOrderItem.  # noqa: E501
        :type: int
        """

        self._number_of_rebills = number_of_rebills

    @property
    def options(self):
        """Gets the options of this AutoOrderItem.  # noqa: E501

        Options associated with this item  # noqa: E501

        :return: The options of this AutoOrderItem.  # noqa: E501
        :rtype: list[AutoOrderItemOption]
        """
        return self._options

    @options.setter
    def options(self, options):
        """Sets the options of this AutoOrderItem.

        Options associated with this item  # noqa: E501

        :param options: The options of this AutoOrderItem.  # noqa: E501
        :type: list[AutoOrderItemOption]
        """

        self._options = options

    @property
    def original_item_id(self):
        """Gets the original_item_id of this AutoOrderItem.  # noqa: E501

        The original item id purchased.  This item controls scheduling.  If you wish to modify a schedule, for example, from monthly to yearly, change this item from your monthly item to your yearly item, and then change the next_shipment_dts to your desired date.  # noqa: E501

        :return: The original_item_id of this AutoOrderItem.  # noqa: E501
        :rtype: str
        """
        return self._original_item_id

    @original_item_id.setter
    def original_item_id(self, original_item_id):
        """Sets the original_item_id of this AutoOrderItem.

        The original item id purchased.  This item controls scheduling.  If you wish to modify a schedule, for example, from monthly to yearly, change this item from your monthly item to your yearly item, and then change the next_shipment_dts to your desired date.  # noqa: E501

        :param original_item_id: The original_item_id of this AutoOrderItem.  # noqa: E501
        :type: str
        """

        self._original_item_id = original_item_id

    @property
    def original_quantity(self):
        """Gets the original_quantity of this AutoOrderItem.  # noqa: E501

        The original quantity purchased  # noqa: E501

        :return: The original_quantity of this AutoOrderItem.  # noqa: E501
        :rtype: float
        """
        return self._original_quantity

    @original_quantity.setter
    def original_quantity(self, original_quantity):
        """Sets the original_quantity of this AutoOrderItem.

        The original quantity purchased  # noqa: E501

        :param original_quantity: The original_quantity of this AutoOrderItem.  # noqa: E501
        :type: float
        """

        self._original_quantity = original_quantity

    @property
    def paused(self):
        """Gets the paused of this AutoOrderItem.  # noqa: E501

        True if paused.  This field is an object instead of a primitive for backwards compatibility.  # noqa: E501

        :return: The paused of this AutoOrderItem.  # noqa: E501
        :rtype: bool
        """
        return self._paused

    @paused.setter
    def paused(self, paused):
        """Sets the paused of this AutoOrderItem.

        True if paused.  This field is an object instead of a primitive for backwards compatibility.  # noqa: E501

        :param paused: The paused of this AutoOrderItem.  # noqa: E501
        :type: bool
        """

        self._paused = paused

    @property
    def paypal_payer_id(self):
        """Gets the paypal_payer_id of this AutoOrderItem.  # noqa: E501

        The PayPal Payer ID tied to this item  # noqa: E501

        :return: The paypal_payer_id of this AutoOrderItem.  # noqa: E501
        :rtype: str
        """
        return self._paypal_payer_id

    @paypal_payer_id.setter
    def paypal_payer_id(self, paypal_payer_id):
        """Sets the paypal_payer_id of this AutoOrderItem.

        The PayPal Payer ID tied to this item  # noqa: E501

        :param paypal_payer_id: The paypal_payer_id of this AutoOrderItem.  # noqa: E501
        :type: str
        """

        self._paypal_payer_id = paypal_payer_id

    @property
    def paypal_recurring_payment_profile_id(self):
        """Gets the paypal_recurring_payment_profile_id of this AutoOrderItem.  # noqa: E501

        The PayPal Profile ID tied to this item  # noqa: E501

        :return: The paypal_recurring_payment_profile_id of this AutoOrderItem.  # noqa: E501
        :rtype: str
        """
        return self._paypal_recurring_payment_profile_id

    @paypal_recurring_payment_profile_id.setter
    def paypal_recurring_payment_profile_id(self, paypal_recurring_payment_profile_id):
        """Sets the paypal_recurring_payment_profile_id of this AutoOrderItem.

        The PayPal Profile ID tied to this item  # noqa: E501

        :param paypal_recurring_payment_profile_id: The paypal_recurring_payment_profile_id of this AutoOrderItem.  # noqa: E501
        :type: str
        """

        self._paypal_recurring_payment_profile_id = paypal_recurring_payment_profile_id

    @property
    def preshipment_notice_sent(self):
        """Gets the preshipment_notice_sent of this AutoOrderItem.  # noqa: E501

        True if the preshipment notice associated with the next rebill has been sent  # noqa: E501

        :return: The preshipment_notice_sent of this AutoOrderItem.  # noqa: E501
        :rtype: bool
        """
        return self._preshipment_notice_sent

    @preshipment_notice_sent.setter
    def preshipment_notice_sent(self, preshipment_notice_sent):
        """Sets the preshipment_notice_sent of this AutoOrderItem.

        True if the preshipment notice associated with the next rebill has been sent  # noqa: E501

        :param preshipment_notice_sent: The preshipment_notice_sent of this AutoOrderItem.  # noqa: E501
        :type: bool
        """

        self._preshipment_notice_sent = preshipment_notice_sent

    @property
    def rebill_value(self):
        """Gets the rebill_value of this AutoOrderItem.  # noqa: E501

        The value of the rebills of this item  # noqa: E501

        :return: The rebill_value of this AutoOrderItem.  # noqa: E501
        :rtype: float
        """
        return self._rebill_value

    @rebill_value.setter
    def rebill_value(self, rebill_value):
        """Sets the rebill_value of this AutoOrderItem.

        The value of the rebills of this item  # noqa: E501

        :param rebill_value: The rebill_value of this AutoOrderItem.  # noqa: E501
        :type: float
        """

        self._rebill_value = rebill_value

    @property
    def remaining_repeat_count(self):
        """Gets the remaining_repeat_count of this AutoOrderItem.  # noqa: E501

        The number of rebills remaining before this item is complete  # noqa: E501

        :return: The remaining_repeat_count of this AutoOrderItem.  # noqa: E501
        :rtype: int
        """
        return self._remaining_repeat_count

    @remaining_repeat_count.setter
    def remaining_repeat_count(self, remaining_repeat_count):
        """Sets the remaining_repeat_count of this AutoOrderItem.

        The number of rebills remaining before this item is complete  # noqa: E501

        :param remaining_repeat_count: The remaining_repeat_count of this AutoOrderItem.  # noqa: E501
        :type: int
        """

        self._remaining_repeat_count = remaining_repeat_count

    @property
    def simple_schedule(self):
        """Gets the simple_schedule of this AutoOrderItem.  # noqa: E501


        :return: The simple_schedule of this AutoOrderItem.  # noqa: E501
        :rtype: AutoOrderItemSimpleSchedule
        """
        return self._simple_schedule

    @simple_schedule.setter
    def simple_schedule(self, simple_schedule):
        """Sets the simple_schedule of this AutoOrderItem.


        :param simple_schedule: The simple_schedule of this AutoOrderItem.  # noqa: E501
        :type: AutoOrderItemSimpleSchedule
        """

        self._simple_schedule = simple_schedule

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
        if issubclass(AutoOrderItem, dict):
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
        if not isinstance(other, AutoOrderItem):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
