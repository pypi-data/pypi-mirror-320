from typing import Optional

import allure
import pytest
from mag_tools.exception.app_exception import AppException
from mag_tools.log.logger import Logger
from mag_tools.model.common.message_type import MessageType
from mag_tools.utils.common.string_format import StringFormat
from selenium.webdriver.remote.webelement import WebElement

from mag_test.bean.base_test import BaseTest
from mag_test.bean.element_info import ElementInfo
from mag_test.core.app_driver import AppDriver
from mag_test.finder.element_finder import ElementFinder
from mag_test.model.control_type import ControlType
from mag_test.model.test_component_type import TestComponentType
from mag_test.model.usage_status import UsageStatus
from mag_test.utils.event_utils import EventUtils


class Step(BaseTest):
    def __init__(self, home_dir:str, name: Optional[str], control_name:Optional[str], control_type:Optional[ControlType],
                 automation_id:Optional[str], value:Optional[str], function_index:Optional[int]=None, step_index:Optional[int]=None,
                 parent_name:Optional[str]=None, parent_type:Optional[ControlType]=None, parent_id:Optional[str]=None,
                 pop_window:Optional[str]=None, status:UsageStatus=UsageStatus.NORMAL):
        super().__init__(home_dir, name, step_index, TestComponentType.STEP, None, status)

        self.__function_index = function_index
        self.__element_info = ElementInfo(control_name, control_type, automation_id, None,
                                          parent_name, parent_type, parent_id, None, StringFormat.format(value), pop_window)

    @pytest.mark.benchmark
    def start(self, driver:AppDriver):
        """
        启动测试步骤
        :param driver: AppDriver
        """
        if self._status == UsageStatus.NORMAL:
            with allure.step(f"  {self._index} {self._name}"):  # 描述测试步骤
                try:
                    Logger.debug(f'测试步骤[{self._name}]-{self._index}：\n\t{self.__element_info}')

                    if self.__element_info.is_virtual_control():
                        EventUtils.process_virtual_event(self.__element_info)
                    else:
                        # 查找控件并处理事件
                        element = ElementFinder.find(driver, self.__element_info)
                        self.__process_event(driver, element)

                        # 检查消息提示框
                        alert_result = driver.check_alert()
                        if alert_result[0] in {MessageType.ERROR}:
                            raise AppException(alert_result[1])

                        # 如果指定了弹出窗口，则切换
                        if self.__element_info.pop_window:
                            # driver = ElementFinder.find(driver, self.__element_info)
                            driver = driver.switch_to_window_by_title(self.__element_info.pop_window)

                    self.success()
                except (AppException, Exception) as e:
                    Logger.error(f"测试步骤[{self._name}-{self._index}]失败: {self.__element_info.name}({self.__element_info.control_type})\n{str(e)}")
                    self.fail(str(e))

        return driver

    def __process_event(self, driver:AppDriver, element:WebElement):
        """
        启动测试步骤
        :param driver: AppDriver
        """

        try:
            attachment = self.get_attachment(self.__element_info.value)
            EventUtils.process_event(driver, element, self.__element_info, attachment)
        except (AppException, Exception) as e:
            Logger.info(str(e))