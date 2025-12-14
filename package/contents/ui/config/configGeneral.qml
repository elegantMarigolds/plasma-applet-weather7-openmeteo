import QtQuick
import QtQuick.Controls as QQC2
import org.kde.kcmutils as KCM
import org.kde.kirigami as Kirigami
import Qt.labs.platform as Platform

KCM.SimpleKCM {
  id: generalConfigPage

  property alias cfg_City: cityField.text
  property alias cfg_Command: commandField.text
  property alias cfg_FontFamily: fontDialog.fontChosen.family
  property alias cfg_Interval: updateIntervalSpin.value

  Kirigami.FormLayout {
    Row {
      spacing: Kirigami.Units.smallSpacing
      Kirigami.FormData.label: i18nc("@label", "Font Family:")
      QQC2.TextField {
        id: fontFamilyField
        text: fontDialog.fontChosen.family
        readOnly: true
      }
      QQC2.ToolButton {
        icon.name: "settings-configure"

        onClicked: {
          fontDialog.currentFont = fontDialog.fontChosen
          fontDialog.open()
        }
      }
      Platform.FontDialog {
        id: fontDialog
        property font fontChosen: Qt.font()

        onAccepted: {
          fontChosen = font
        }
      }
    }
    QQC2.TextField {
      id: commandField
      text: plasmoid.configuration.Command
      Kirigami.FormData.label: i18nc("@label", "Weather Script/Command:")
    }
    QQC2.TextField {
      id: cityField
      text: plasmoid.configuration.City
      Kirigami.FormData.label: i18nc("@label", "City Name:")
    }
    QQC2.SpinBox {
      id: updateIntervalSpin
      value: plasmoid.configuration.Interval
      Kirigami.FormData.label: i18nc("@label:spinbox", "Update every:")

      from: 1
      to: 3600
      editable: true

      textFromValue: function(value) {
        return (i18np("%1 minute", "%1 minutes", value));
      }
      valueFromText: function(text) {
        return parseInt(text);
      }
    }
  }
}
