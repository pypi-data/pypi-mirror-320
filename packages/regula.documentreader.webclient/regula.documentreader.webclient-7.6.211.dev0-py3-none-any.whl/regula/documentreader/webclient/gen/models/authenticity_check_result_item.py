# coding: utf-8

"""
    Generated by: https://openapi-generator.tech
"""

import pprint
import re  # noqa: F401

import six

from regula.documentreader.webclient.gen.configuration import Configuration
# this line was added to enable pycharm type hinting
from regula.documentreader.webclient.gen.models import *


"""
Common fields for all authenticity result objects
"""
class AuthenticityCheckResultItem(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'type': 'int',
        'element_result': 'CheckResult',
        'element_diagnose': 'CheckDiagnose',
        'percent_value': 'int'
    }

    attribute_map = {
        'type': 'Type',
        'element_result': 'ElementResult',
        'element_diagnose': 'ElementDiagnose',
        'percent_value': 'PercentValue'
    }
    discriminator_value_class_map = {
        1 : 'SecurityFeatureResult',
        1024 : 'IdentResult',
        1048576 : 'IdentResult',
        128 : 'PhotoIdentResult',
        131072 : 'IdentResult',
        16 : 'FiberResult',
        16384 : 'FiberResult',
        2 : 'SecurityFeatureResult',
        2048 : 'IdentResult',
        256 : 'PhotoIdentResult',
        262144 : 'IdentResult',
        32 : 'IdentResult',
        32768 : 'IdentResult',
        4 : 'IdentResult',
        4096 : 'SecurityFeatureResult',
        512 : 'SecurityFeatureResult',
        524288 : 'IdentResult',
        64 : 'OCRSecurityTextResult',
        65536 : 'SecurityFeatureResult',
        8 : 'SecurityFeatureResult',
        8192 : 'SecurityFeatureResult',
        8388608 : 'SecurityFeatureResult',
    }

    def __init__(self, type=0, element_result=None, element_diagnose=None, percent_value=None, local_vars_configuration=None):  # noqa: E501
        """AuthenticityCheckResultItem - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._type = None
        self._element_result = None
        self._element_diagnose = None
        self._percent_value = None
        self.discriminator = 'type'

        self.type = type
        if element_result is not None:
            self.element_result = element_result
        if element_diagnose is not None:
            self.element_diagnose = element_diagnose
        if percent_value is not None:
            self.percent_value = percent_value

    @property
    def type(self):
        """Gets the type of this AuthenticityCheckResultItem.  # noqa: E501

        Same as authenticity result type, but used for safe parsing of not-described values: https://docs.regulaforensics.com/develop/doc-reader-sdk/web-service/development/enums/authenticity-result-type/  # noqa: E501

        :return: The type of this AuthenticityCheckResultItem.  # noqa: E501
        :rtype: int
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this AuthenticityCheckResultItem.

        Same as authenticity result type, but used for safe parsing of not-described values: https://docs.regulaforensics.com/develop/doc-reader-sdk/web-service/development/enums/authenticity-result-type/  # noqa: E501

        :param type: The type of this AuthenticityCheckResultItem.  # noqa: E501
        :type type: int
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501

        self._type = type

    @property
    def element_result(self):
        """Gets the element_result of this AuthenticityCheckResultItem.  # noqa: E501


        :return: The element_result of this AuthenticityCheckResultItem.  # noqa: E501
        :rtype: CheckResult
        """
        return self._element_result

    @element_result.setter
    def element_result(self, element_result):
        """Sets the element_result of this AuthenticityCheckResultItem.


        :param element_result: The element_result of this AuthenticityCheckResultItem.  # noqa: E501
        :type element_result: CheckResult
        """

        self._element_result = element_result

    @property
    def element_diagnose(self):
        """Gets the element_diagnose of this AuthenticityCheckResultItem.  # noqa: E501


        :return: The element_diagnose of this AuthenticityCheckResultItem.  # noqa: E501
        :rtype: CheckDiagnose
        """
        return self._element_diagnose

    @element_diagnose.setter
    def element_diagnose(self, element_diagnose):
        """Sets the element_diagnose of this AuthenticityCheckResultItem.


        :param element_diagnose: The element_diagnose of this AuthenticityCheckResultItem.  # noqa: E501
        :type element_diagnose: CheckDiagnose
        """

        self._element_diagnose = element_diagnose

    @property
    def percent_value(self):
        """Gets the percent_value of this AuthenticityCheckResultItem.  # noqa: E501


        :return: The percent_value of this AuthenticityCheckResultItem.  # noqa: E501
        :rtype: int
        """
        return self._percent_value

    @percent_value.setter
    def percent_value(self, percent_value):
        """Sets the percent_value of this AuthenticityCheckResultItem.


        :param percent_value: The percent_value of this AuthenticityCheckResultItem.  # noqa: E501
        :type percent_value: int
        """

        self._percent_value = percent_value

    def get_real_child_model(self, data):
        """Returns the real base class specified by the discriminator"""
        discriminator_key = self.attribute_map[self.discriminator]
        discriminator_value = data[discriminator_key]
        from regula.documentreader.webclient.ext.models import RawAuthenticityCheckResultItem
        return self.discriminator_value_class_map.get(discriminator_value, RawAuthenticityCheckResultItem.__name__)

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
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

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, AuthenticityCheckResultItem):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AuthenticityCheckResultItem):
            return True

        return self.to_dict() != other.to_dict()
