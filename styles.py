class Theme:
    PRIMARY = "#10A37F"
    PRIMARY_LIGHT = "#E7F7F1"
    PRIMARY_DARK = "#0B7B61"
    ACCENT = "#6D5BD0"

    BG_MAIN = "#FFFFFF"
    BG_CANVAS = "#F7F7F8"
    BG_SIDEBAR = "#111827"
    BG_SIDEBAR_HOVER = "#1F2937"
    BG_USER_MSG = "#E7F7F1"
    BG_AI_MSG = "#FFFFFF"
    BG_INPUT = "#FFFFFF"
    BG_HOVER = "#F1F5F9"
    BG_CODE = "#0F172A"

    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#64748B"
    TEXT_LIGHT = "#94A3B8"
    TEXT_ON_DARK = "#F8FAFC"
    TEXT_MUTED_ON_DARK = "#CBD5E1"

    BORDER = "#E2E8F0"
    BORDER_DARK = "#263244"
    BORDER_FOCUS = "#10A37F"

    SUCCESS = "#16A34A"
    ERROR = "#DC2626"
    WARNING = "#D97706"

    SIDEBAR_WIDTH = 292
    INPUT_MAX_HEIGHT = 180

    @staticmethod
    def get_stylesheet():
        return """
        QMainWindow {
            background-color: #FFFFFF;
            color: #111827;
        }
        QWidget {
            font-family: "Segoe UI";
            font-size: 13px;
        }
        QToolTip {
            background-color: #111827;
            color: #F8FAFC;
            border: 1px solid #263244;
            padding: 6px 8px;
            border-radius: 6px;
        }
        QScrollBar:vertical {
            background: transparent;
            width: 8px;
            margin: 4px 2px 4px 2px;
        }
        QScrollBar::handle:vertical {
            background: #CBD5E1;
            border-radius: 4px;
            min-height: 32px;
        }
        QScrollBar::handle:vertical:hover {
            background: #94A3B8;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            height: 0px;
        }
        """
