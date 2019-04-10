import os

class Website(object):

    def __init__(self, filename, title="Website", target_name="ABC", ref_name="XYZ"):
        self.f = open(filename,"w+")
        self._in_row = False
        self._hist_in_current_row = False

        self.f.write("""<!DOCTYPE html>
<html>
<head>
<style>
body {
  font-family: Sans-Serif;
  background-color: #ffffff;
}
</style>
""")
        self.f.write("""<title>{0}</title>
</head>
<body>
<h1>{0}</h1>
<p>In all plots below, the <b><font color='red'>{1}</font></b> histograms are in red, and the <b><font color='blue'>{2}</font></b> histograms are in blue.</p>
<p>Static website generated from DQM files with <a href=https://github.com/guitargeek/dqm-hist-webpage>dqm-hist-webpage</a>.</p>
""".format(title, target_name, ref_name))

        self.tableofcontents = ''

        self.content = ""

    def start_section(self, name):
        if self._in_row:
            self._end_row()
        self.content += "<h2>{0}</h2>".format(name)
        self._begin_row()

        self.tableofcontents += """
<b>{0}</b>
<br><br>""".format(name)

    def newline(self):
        if self._in_row and self._hist_in_current_row:
            self._begin_row()

    def _draw_uparrow(self):
        self.content +="""<tr valign="top">
        <td>
            <a href="index.html">
                <img width="18" height="18" border="0" align="middle" src="up.gif" alt="Top"/>
            </a>
        </td>
        """

    def _begin_row(self):
        if self._in_row:
            self._end_row()
        self._in_row = True
        self._hist_in_current_row = False

    def _end_row(self):
        self.content += "</tr>"
        self.content += "</table>"
        self.tableofcontents += '<br>'
        self._in_row = False

    def add_hist(self, name, filename):
        if not self._in_row:
            self._begin_row()
        if not self._hist_in_current_row:
            self.content += '<table cellpadding="5">'
            self._draw_uparrow()
        self.content += """
        <td>
            <a id="{0}" name="{0}"></a>
            <a href="{1}">
                <img border="0" class="image" width="440" src="{1}">
            </a>
        </td>
        """.format(name, filename)
        self._hist_in_current_row = True
        self.tableofcontents += '• <a href="#{0}">{0}</a> '.format(name)

    def close(self):
        self.tableofcontents += "<br>"
        self.f.write(self.tableofcontents)
        self.f.write(self.content)
        self.f.write("</body>")
        self.f.write("</html>")
        self.f.close()
