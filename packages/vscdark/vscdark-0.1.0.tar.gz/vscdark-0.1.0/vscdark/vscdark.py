import matplotlib.pyplot as plt
from IPython.display import HTML, display
from pathlib import Path

theme = "vscdark.vscdark"
theme_is_dark = True
verbose_css = False


def set_style(
    new_theme: str | None = None, dark: bool | None = None, display_css: bool = True, verbose: bool | None = None
) -> None:
    global theme
    global theme_is_dark
    global verbose_css
    theme = new_theme or theme
    theme_is_dark = dark or theme_is_dark
    verbose_css = verbose or verbose_css

    if theme == "vscdark":
        theme = "vscdark.vscdark"

    plt.style.use(theme)

    if display_css:
        display(css())


def css() -> HTML:
    return HTML(
        ("Widget CSS Active" if verbose_css else "")
        + """<style>
            .cell-output-ipywidget-background {background-color: transparent !important;}
            .jp-OutputArea-output {background-color: transparent !important;}
            div.jupyter-widgets.widget-label {display: none;}
            """
        + (
            ".widget-label {color: white !important;} .widget-readout {color:white; !important; }"
            if theme_is_dark
            else ""
        )
        + "</style>"
    )
