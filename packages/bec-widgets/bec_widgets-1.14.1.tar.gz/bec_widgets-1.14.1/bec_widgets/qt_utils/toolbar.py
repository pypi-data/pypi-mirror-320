# pylint: disable=no-name-in-module
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Literal

from bec_qthemes._icon.material_icons import material_icon
from qtpy.QtCore import QSize, Qt
from qtpy.QtGui import QAction, QColor, QIcon
from qtpy.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMenu,
    QSizePolicy,
    QToolBar,
    QToolButton,
    QWidget,
)

import bec_widgets

MODULE_PATH = os.path.dirname(bec_widgets.__file__)


class ToolBarAction(ABC):
    """
    Abstract base class for toolbar actions.

    Args:
        icon_path (str, optional): The name of the icon file from `assets/toolbar_icons`. Defaults to None.
        tooltip (bool, optional): The tooltip for the action. Defaults to None.
        checkable (bool, optional): Whether the action is checkable. Defaults to False.
    """

    def __init__(self, icon_path: str = None, tooltip: str = None, checkable: bool = False):
        self.icon_path = (
            os.path.join(MODULE_PATH, "assets", "toolbar_icons", icon_path) if icon_path else None
        )
        self.tooltip = tooltip
        self.checkable = checkable
        self.action = None

    @abstractmethod
    def add_to_toolbar(self, toolbar: QToolBar, target: QWidget):
        """Adds an action or widget to a toolbar.

        Args:
            toolbar (QToolBar): The toolbar to add the action or widget to.
            target (QWidget): The target widget for the action.
        """


class SeparatorAction(ToolBarAction):
    """Separator action for the toolbar."""

    def add_to_toolbar(self, toolbar: QToolBar, target: QWidget):
        toolbar.addSeparator()


class IconAction(ToolBarAction):
    """
    Action with an icon for the toolbar.

    Args:
        icon_path (str): The path to the icon file.
        tooltip (str): The tooltip for the action.
        checkable (bool, optional): Whether the action is checkable. Defaults to False.
    """

    def __init__(self, icon_path: str = None, tooltip: str = None, checkable: bool = False):
        super().__init__(icon_path, tooltip, checkable)

    def add_to_toolbar(self, toolbar: QToolBar, target: QWidget):
        icon = QIcon()
        icon.addFile(self.icon_path, size=QSize(20, 20))
        self.action = QAction(icon, self.tooltip, target)
        self.action.setCheckable(self.checkable)
        toolbar.addAction(self.action)


class MaterialIconAction:
    """
    Action with a Material icon for the toolbar.

    Args:
        icon_path (str, optional): The name of the Material icon. Defaults to None.
        tooltip (bool, optional): The tooltip for the action. Defaults to None.
        checkable (bool, optional): Whether the action is checkable. Defaults to False.
        filled (bool, optional): Whether the icon is filled. Defaults to False.
    """

    def __init__(
        self,
        icon_name: str = None,
        tooltip: str = None,
        checkable: bool = False,
        filled: bool = False,
        color: str | tuple | QColor | dict[Literal["dark", "light"], str] | None = None,
    ):
        self.icon_name = icon_name
        self.tooltip = tooltip
        self.checkable = checkable
        self.action = None
        self.filled = filled
        self.color = color

    def add_to_toolbar(self, toolbar: QToolBar, target: QWidget):
        icon = self.get_icon()
        self.action = QAction(icon, self.tooltip, target)
        self.action.setCheckable(self.checkable)
        toolbar.addAction(self.action)

    def get_icon(self):

        icon = material_icon(
            self.icon_name,
            size=(20, 20),
            convert_to_pixmap=False,
            filled=self.filled,
            color=self.color,
        )
        return icon


class DeviceSelectionAction(ToolBarAction):
    """
    Action for selecting a device in a combobox.

    Args:
        label (str): The label for the combobox.
        device_combobox (DeviceComboBox): The combobox for selecting the device.

    """

    def __init__(self, label: str, device_combobox):
        super().__init__()
        self.label = label
        self.device_combobox = device_combobox
        self.device_combobox.currentIndexChanged.connect(lambda: self.set_combobox_style("#ffa700"))

    def add_to_toolbar(self, toolbar, target):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        label = QLabel(f"{self.label}")
        layout.addWidget(label)
        layout.addWidget(self.device_combobox)
        toolbar.addWidget(widget)

    def set_combobox_style(self, color: str):
        self.device_combobox.setStyleSheet(f"QComboBox {{ background-color: {color}; }}")


class WidgetAction(ToolBarAction):
    """
    Action for adding any widget to the toolbar.

    Args:
        label (str|None): The label for the widget.
        widget (QWidget): The widget to be added to the toolbar.

    """

    def __init__(self, label: str | None = None, widget: QWidget = None, parent=None):
        super().__init__(parent)
        self.label = label
        self.widget = widget

    def add_to_toolbar(self, toolbar: QToolBar, target: QWidget):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        if self.label is not None:
            label_widget = QLabel(f"{self.label}")
            label_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            label_widget.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
            layout.addWidget(label_widget)

        if isinstance(self.widget, QComboBox):
            self.widget.setSizeAdjustPolicy(QComboBox.AdjustToContents)

            size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.widget.setSizePolicy(size_policy)

            self.widget.setMinimumWidth(self.calculate_minimum_width(self.widget))

        else:
            self.widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        layout.addWidget(self.widget)

        toolbar.addWidget(container)

    @staticmethod
    def calculate_minimum_width(combo_box: QComboBox) -> int:
        """
        Calculate the minimum width required to display the longest item in the combo box.

        Args:
            combo_box (QComboBox): The combo box to calculate the width for.

        Returns:
            int: The calculated minimum width in pixels.
        """
        font_metrics = combo_box.fontMetrics()
        max_width = max(font_metrics.width(combo_box.itemText(i)) for i in range(combo_box.count()))
        return max_width + 60


class ExpandableMenuAction(ToolBarAction):
    """
    Action for an expandable menu in the toolbar.

    Args:
        label (str): The label for the menu.
        actions (dict): A dictionary of actions to populate the menu.
        icon_path (str, optional): The path to the icon file. Defaults to None.

    """

    def __init__(self, label: str, actions: dict, icon_path: str = None):
        super().__init__(icon_path, label)
        self.actions = actions
        self.widgets = defaultdict(dict)

    def add_to_toolbar(self, toolbar: QToolBar, target: QWidget):
        button = QToolButton(toolbar)
        if self.icon_path:
            button.setIcon(QIcon(self.icon_path))
        button.setText(self.tooltip)
        button.setPopupMode(QToolButton.InstantPopup)
        button.setStyleSheet(
            """
                   QToolButton {
                       font-size: 14px;
                   }
                   QMenu {
                       font-size: 14px;
                   }
               """
        )
        menu = QMenu(button)
        for action_id, action in self.actions.items():
            sub_action = QAction(action.tooltip, target)
            if hasattr(action, "icon_path"):
                icon = QIcon()
                icon.addFile(action.icon_path, size=QSize(20, 20))
                sub_action.setIcon(icon)
            elif hasattr(action, "get_icon"):
                sub_action.setIcon(action.get_icon())
            sub_action.setCheckable(action.checkable)
            menu.addAction(sub_action)
            self.widgets[action_id] = sub_action
        button.setMenu(menu)
        toolbar.addWidget(button)


class ModularToolBar(QToolBar):
    """Modular toolbar with optional automatic initialization.

    Args:
        parent (QWidget, optional): The parent widget of the toolbar. Defaults to None.
        actions (dict, optional): A dictionary of action creators to populate the toolbar. Defaults to None.
        target_widget (QWidget, optional): The widget that the actions will target. Defaults to None.
        orientation (Literal["horizontal", "vertical"], optional): The initial orientation of the toolbar. Defaults to "horizontal".
        background_color (str, optional): The background color of the toolbar. Defaults to "rgba(0, 0, 0, 0)" - transparent background.
    """

    def __init__(
        self,
        parent=None,
        actions: dict | None = None,
        target_widget=None,
        orientation: Literal["horizontal", "vertical"] = "horizontal",
        background_color: str = "rgba(0, 0, 0, 0)",
    ):
        super().__init__(parent)

        self.widgets = defaultdict(dict)
        self.background_color = background_color
        self.set_background_color(self.background_color)

        # Set the initial orientation
        self.set_orientation(orientation)

        if actions is not None and target_widget is not None:
            self.populate_toolbar(actions, target_widget)

    def populate_toolbar(self, actions: dict, target_widget):
        """Populates the toolbar with a set of actions.

        Args:
            actions (dict): A dictionary of action creators to populate the toolbar.
            target_widget (QWidget): The widget that the actions will target.
        """
        self.clear()
        for action_id, action in actions.items():
            action.add_to_toolbar(self, target_widget)
            self.widgets[action_id] = action

    def set_background_color(self, color: str = "rgba(0, 0, 0, 0)"):
        """
        Sets the background color and other appearance settings.

        Args:
            color(str): The background color of the toolbar.
        """
        self.setIconSize(QSize(20, 20))
        self.setMovable(False)
        self.setFloatable(False)
        self.setContentsMargins(0, 0, 0, 0)
        self.background_color = color
        self.setStyleSheet(f"QToolBar {{ background-color: {color}; border: none; }}")

    def set_orientation(self, orientation: Literal["horizontal", "vertical"]):
        """Sets the orientation of the toolbar.

        Args:
            orientation (Literal["horizontal", "vertical"]): The desired orientation of the toolbar.
        """
        if orientation == "horizontal":
            self.setOrientation(Qt.Horizontal)
        elif orientation == "vertical":
            self.setOrientation(Qt.Vertical)
        else:
            raise ValueError("Orientation must be 'horizontal' or 'vertical'.")

    def update_material_icon_colors(self, new_color: str | tuple | QColor):
        """
        Updates the color of all MaterialIconAction icons in the toolbar.

        Args:
            new_color (str | tuple | QColor): The new color for the icons.
        """
        for action in self.widgets.values():
            if isinstance(action, MaterialIconAction):
                action.color = new_color
                # Refresh the icon
                updated_icon = action.get_icon()
                action.action.setIcon(updated_icon)

    def add_action(self, action_id: str, action: ToolBarAction, target_widget: QWidget):
        """
        Adds a new action to the toolbar dynamically.

        Args:
            action_id (str): Unique identifier for the action.
            action (ToolBarAction): The action to add to the toolbar.
            target_widget (QWidget): The target widget for the action.
        """
        if action_id in self.widgets:
            raise ValueError(f"Action with ID '{action_id}' already exists.")
        action.add_to_toolbar(self, target_widget)
        self.widgets[action_id] = action

    def hide_action(self, action_id: str):
        """
        Hides a specific action on the toolbar.

        Args:
            action_id (str): Unique identifier for the action to hide.
        """
        if action_id not in self.widgets:
            raise ValueError(f"Action with ID '{action_id}' does not exist.")
        action = self.widgets[action_id]
        if hasattr(action, "action") and isinstance(action.action, QAction):
            action.action.setVisible(False)

    def show_action(self, action_id: str):
        """
        Shows a specific action on the toolbar.

        Args:
            action_id (str): Unique identifier for the action to show.
        """
        if action_id not in self.widgets:
            raise ValueError(f"Action with ID '{action_id}' does not exist.")
        action = self.widgets[action_id]
        if hasattr(action, "action") and isinstance(action.action, QAction):
            action.action.setVisible(True)
