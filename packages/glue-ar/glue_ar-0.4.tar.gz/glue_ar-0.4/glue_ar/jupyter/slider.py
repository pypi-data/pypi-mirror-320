import ipyvuetify as v
import traitlets


class Slider(v.VuetifyTemplate):

    template_file = (__file__, "slider.vue")
    min = traitlets.Float().tag(sync=True)
    max = traitlets.Float().tag(sync=True)
    step = traitlets.Float().tag(sync=True)
    icon_src = traitlets.Unicode().tag(sync=True)
    doc_text = traitlets.Unicode(allow_none=True).tag(sync=True)

    def __init__(self,
                 icon_path: str,
                 cb_property: str):

        super().__init__()
