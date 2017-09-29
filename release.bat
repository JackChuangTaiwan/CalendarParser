SET output=CalendarParser_release
SET ui_release=ui\CalendarParserUI\bin\Release
mkdir %output%
del "%output%"
copy "config.py" "%output%\config.py"
copy "core.py" "%output%\core.py"
copy "main.py" "%output%\main.py"
copy "converter_config.json" "%output%\converter_config.json"
copy "%ui_release%\CalendarParserUI.exe" "%output%\CalendarParserUI.exe"
PAUSE