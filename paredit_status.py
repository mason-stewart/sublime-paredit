import sublime, sublime_plugin

class PareditStatusCommand(sublime_plugin.TextCommand):
  def run(self, view, text):
    sublime.status_message("  --  PAREDIT: " + text)
