import QtQuick
import QtQuick.Layouts
import QtQuick.Effects
import org.kde.ksvg as KSvg
import org.kde.plasma.plasmoid
import org.kde.kirigami as Kirigami
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components as PlasmaComponents

PlasmoidItem {
  Layout.minimumWidth: 350
  Layout.minimumHeight: 245
  implicitWidth: 350
  implicitHeight: 245

  Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

  Weather {
    id: weather
  }

  property string fontFamily: Plasmoid.configuration.FontFamily

  Image {
    id: backgound
    anchors.fill: parent
    source: weather.backgroundImages[weather.currentStatus]
  }

  MultiEffect {
    source: backgound
    anchors.fill: backgound
    shadowBlur: 0.5
    shadowEnabled: true
    shadowColor: "#272727"
    shadowVerticalOffset: 0
  }

  Column {
    id: weatherInfo
    anchors.top: parent.top
    anchors.right: parent.right
    anchors.topMargin: 2
    anchors.rightMargin: 10

    Text {
      text: weather.currentTemperature
      font.family: fontFamily
      font.weight: Font.Medium
      font.pointSize: 42
      color: "white"
      horizontalAlignment: Text.AlignRight
    }

    Text {
      text: weather.currentRange
      font.family: fontFamily
      font.pointSize: 10
      color: "white"
      opacity: 0.6
      horizontalAlignment: Text.AlignRight
      width: parent.width
    }

    Text {
      text: weather.statusList[weather.currentStatus]
      font.family: fontFamily
      font.pointSize: 14
      color: "white"
      horizontalAlignment: Text.AlignRight
      width: parent.width
    }

    Text {
        text: weather.precipitationChance
        font.family: fontFamily
        font.pointSize: 10
        color: "white"
        opacity: 0.6
        horizontalAlignment: Text.AlignRight
        width: parent.width
    }

    Text {
      text: weather.currentCity
      font.family: fontFamily
      font.pointSize: 10
      color: "white"
      opacity: 0.6
      horizontalAlignment: Text.AlignRight
      width: parent.width
    }
  }

  Rectangle {
    id: footer
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.bottom: parent.bottom
    anchors.leftMargin: 10
    anchors.rightMargin: 10
    height: 35
    color: "transparent"
    RowLayout {
      anchors.fill: parent

      Text {
        text: weather.weatherSource
        font.family: fontFamily
        font.pointSize: 10
        color: "white"
        opacity: 0.6
        Layout.alignment: Qt.AlignLeft
        MouseArea {
          anchors.fill: parent
        }
      }

      Item { Layout.fillWidth: true }

      Text {
        id: updateTimeText
        text: weather.updateTime
        font.family: fontFamily
        font.pointSize: 10
        color: "white"
        opacity: 0.6
        Layout.alignment: Qt.AlignRight
        MouseArea {
          anchors.fill: parent
          onClicked: {
            weather.updateWeather()
          }
          cursorShape: Qt.PointingHandCursor
        }
      }
    }
  }

  Flow {
    id: forecastFlow
    anchors.horizontalCenter: parent.horizontalCenter
    anchors.bottom: footer.top
    layoutDirection: Qt.LeftToRight
    spacing: 24
    anchors.bottomMargin: 15

    Repeater {
      model: weather.forecastList
      Rectangle {
        width: 94
        height: 90
        color: "transparent"
        RowLayout {
          anchors.fill: parent
          anchors.margins: Kirigami.Units.smallSpacing
          spacing: Kirigami.Units.smallSpacing
          Column {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            spacing: 2
            Text {
              text: modelData.time
              font.family: fontFamily
              font.pointSize: 10
              color: "white"
              opacity: 0.6
            }
            Text {
              text: modelData.high
              font.family: fontFamily
              font.pointSize: 12
              color: "white"
            }
            Text {
              text: modelData.low
              font.family: fontFamily
              font.pointSize: 12
              font.weight: Font.Light
              color: "white"
              opacity: 0.6
            }
            Text {
              text: modelData.precip
              font.family: fontFamily
              font.pointSize: 10
              color: "#88ccff"  // Light blue for precipitation
              opacity: 0.8
            }
          }
          KSvg.SvgItem {
            Layout.preferredWidth: 48
            Layout.preferredHeight: 48
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
            smooth: true
            antialiasing: true
            svg: KSvg.Svg {
              imagePath: weather.skyconImages[modelData.status]
            }
          }
        }
      }
    }
  }

  Timer {
    id: tickTimer
    interval: 1000 * 60 * Plasmoid.configuration.Interval
    running: true
    repeat: true
    triggeredOnStart: true

    onTriggered: {
      weather.updateWeather()
    }
  }
}
