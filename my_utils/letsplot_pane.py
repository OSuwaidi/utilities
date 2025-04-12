import param
from panel.reactive import ReactiveHTML

import base64
from lets_plot.plot.core import PlotSpec
from lets_plot._kbridge import (
    _generate_static_configure_html,
    _generate_display_html_for_raw_spec
)

import polars as pl
import pandas as pd

_config_html: bytes = _generate_static_configure_html().encode("utf-8")  # load necessary JS/CSS boilerplate


class LetsPlotPane(ReactiveHTML):
    # Param objects are initialized and bound (to instances) upon object instantiation
    plot_object = param.ClassSelector(class_=PlotSpec, precedence=-1)  # default = None
    sizing_options = param.Dict(default={"width_mode": "fit", "height_mode": "fit"})
    plot_uri = param.String()  # default = ""

    _template = """
    <iframe
        id="pn-container"
        src="data:text/html;base64,${plot_uri}"
        style="height:1.8vh; width:42vw; border: none;">
    </iframe>
    """  # HTML template that gets rendered and declares how the sublass' parameters are linked to HTML

    @param.depends("plot_object", watch=True, on_init=True)
    def _update_config(self) -> None:
        if not self.plot_object:
            self.plot_uri = ""
            return

        spec: dict = self.plot_object.as_dict()
        if (data := spec.get("data")) is not None:
            if isinstance(data, pl.DataFrame):
                spec["data"] = data.to_dict(as_series=False)
            elif isinstance(data, pd.DataFrame):
                spec["data"] = data.to_dict(orient="list")

        display_html: str = _generate_display_html_for_raw_spec(spec, sizing_options=self.sizing_options, responsive=True)

        plot_html_bytes = _config_html + display_html.encode("utf-8")
        self.plot_uri = base64.b64encode(plot_html_bytes).decode("utf-8")
