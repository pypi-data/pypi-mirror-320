import uuid

from .JHTML import HTML

__all__ = [
    "JSMol"
]

__reload_hooks__ = [".JHTML"]

class JSMol:
    class Applet(HTML.Div):
        base_scripts = [
            HTML.Script(src="https://cdn.jsdelivr.net/gh/b3m2a1/jsmol-cdn@16.3.7.5/jsmol/JSmol.min.js"),
            HTML.Script(src="https://cdn.jsdelivr.net/gh/b3m2a1/jsmol-cdn@16.3.7.5/jsmol/js/Jmol2.js"),
            HTML.Script(
                """jmolInitialize("https://cdn.jsdelivr.net/gh/b3m2a1/jsmol-cdn@16.3.7.5/jsmol/");\n"""
                """Jmol.Info["serverURL"] = "https://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php";\n"""
                # """Jmol.Info["j2sPath"] = "https://cdn.jsdelivr.net/gh/b3m2a1/jsmol-cdn@16.3.7.4/jsmol/j2s";\n"""
                """Jmol.Info["width"] = "100%";\n"""
                """Jmol.Info["height"] = "100%";"""
            )
        ]
        def __init__(self, *model_etc, width='500px', height='500px', animate=False, vibrate=False, load_script=None,
                     suffix=None,
                     **attrs):
            if suffix is None:
                suffix = str(uuid.uuid4())[:6].replace("-", "")
            self.suffix = suffix
            self.id = "jsmol-applet-" + self.suffix
            if len(model_etc) > 0 and isinstance(model_etc[0], str):
                model_file = model_etc[0]
                rest = model_etc[1:]
            else:
                model_file = None
                rest = model_etc
            if load_script is None:
                if animate:
                    load_script = 'anim mode palindrome; anim on;'
                elif vibrate:
                    load_script = "vibration on"
                else:
                    load_script = ""
            self.load_script = load_script
            elems = self.base_scripts + [self.create_applet(model_file)] + list(rest)
            super().__init__(*elems, id=self.id, width=width, height=height, **attrs)

        @property
        def applet_target(self):
            return f"_{self.suffix}"
        def create_applet(self, model_file):
            targ = self.applet_target
            if model_file is None:
                loader = f'jmolApplet(400, "load {model_file}; {self.load_script}", "{targ}")'
            elif (
                    model_file.startswith("https://")
                    or model_file.startswith("file://")
                    or model_file.startswith("http://")
            ):
                loader = f'jmolApplet(400, "load {model_file}; {self.load_script}", "{targ}")'
            else:
                loader = f'jmolAppletInline(400, `{model_file}`, "{self.load_script}", "{targ}")'
            return HTML.Div(
                HTML.Script(f"""window.setTimeout((function () {{
                    let loaded = false;
                    if (!loaded) {{
                        loaded = true;
                        let applet = {loader};
                         document.getElementById("{self.id}").innerHTML = applet._code;
                        // window.setTimeout(() => {{ applet._cover(false); }}, 250)
                    }}
                }}), 250)"""),
                id=f"{self.id}-pane"
            )
