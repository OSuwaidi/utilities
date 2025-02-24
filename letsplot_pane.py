import param
from panel.reactive import ReactiveHTML

from lets_plot import __version__ as _lets_plot_version
from lets_plot.plot.core import PlotSpec
from lets_plot._type_utils import standardize_dict

import polars as pl


class LetsPlotPane(ReactiveHTML):
    object: PlotSpec = param.ClassSelector(class_=PlotSpec, precedence=-1)

    _plot_spec_as_dict: dict = param.Dict()

    _template = '<div id="pn-container" style="height:100%;width:100%"></div>'

    __javascript__ = [f"https://cdn.jsdelivr.net/gh/JetBrains/lets-plot@v{_lets_plot_version}/js-package/distr/lets-plot.min.js"]

    @param.depends("object", watch=True, on_init=True)
    def _update_config(self) -> None:
        if not self.object:
            self._plot_spec_as_dict = {}
        else:
            spec: dict = self.object.as_dict()
            if "data" in spec and isinstance(spec["data"], pl.DataFrame):
                spec["data"] = spec["data"].to_dict(as_series=False)

            self._plot_spec_as_dict = standardize_dict(spec)

    _scripts = {
        "render": "state.height=-10",
        "after_layout": "self._plot_spec_as_dict()",
        "_plot_spec_as_dict": """
var height=pn_container.clientHeight
if (state.height-5<=height & height<=state.height+5){height=state.height}
state.height=height
pn_container.innerHTML=""
LetsPlot.buildPlotFromRawSpecs(data._plot_spec_as_dict, pn_container.clientWidth-5, height, pn_container);
""",
    }
