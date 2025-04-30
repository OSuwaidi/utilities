### Interactivity between widgets (parameters) and functions or components can be established in 4 main ways:
1. Using `@pn.depends` (*declarative* approach):
    `@pn.depends(p1.param.att1, p2.param.att2, ..., watch: bool, on_init: bool)` declares that the decorated function depends on parameter objects `p1` and `p2`,
    such that any changes to `att1` or `att2`, respectively, will automatically trigger a `func(p1.att1, p2.att2, ...)` function call (callback). It is best used:
        a.) To build reactive UIs, where the decorated function's return is used for front-side rendering (Panel components, plot, table, text)
        b.) To perform side effects depending on many different parameter objects, such as:
            i.) updating or mutating other objects' state(s)
            ii.) reaching out for DB, trigger external API, etc.
            iii.) logging or storing data
* **Note**: It's almost always better to create a parameterized object (state) with Param dependencies (indirectly via `pn.depends`) that stores your value then updating/mutating it via `pn.depends(..., watch=Tue)` (eagerly as a side effect), rather than returning the value directly from a `pn.depends(..., watch=False)`-decorated function. That's because:
  1. it's more efficient as it updates only the specific Parameters that are being changed rather than rendering reactive functions directly.
  2. without `watch=True`, the reactivity is deferred and the callback is *only* triggered when the decorated-function is used for rendering UI components (when laid out).
  3. if multiple objects depend on the change triggered via `pn.depends`, then you would have to manipulate them all through `pn.depends` itself since they have no other way of knowing that changes occured (or you would have them depend on the decorated function itself which is inefficient). But if you use a parameterized object as your state, all dependent objects can track it individually such that when its mutated via `pn.depends(..., watch=True)`, changes propagate once and they can all update their values as needed.

2. Using `pn.bind` (also declarative approach):
    `pn.bind(func, p1, p2, ...)` is basically a wrapper (syntactic sugar) around `@pn.depends` and hence is heavier due to overhead and not preferred.
    Only use `pn.bind` if you really need to use the bound function's return for some bussiness logic (dynamically computed values) in addition to reactive UI updates/rendering.

* **Note**: Declarative reactive functions automatically manage state changes.

3. Using `p.param.watch` (imperative approach):
    `p.param.watch(func, ["att1", "att2"], onlychanged: bool)` is the lowest-level API available to establish interactivity in Panel, since all reactivity is built on Param.
    `p.param.watch` is exclusively used to perform advanced, efficient side effects (similar to `pn.depends`), not for UI-driven reactivity. It has the least overhead and gives the watched function full access to the parameter's attributes such as `event.old`, `event.new`, `event.name`. It is best used when the callback is used solely for its side effects (e.g. external API request, DB query, object mutation, etc.) and when the the callback doesn't depend on many parameters, else use `pn.depends(... watch=True)` since you can provide many parameters at once.
* **Note**: If we need the callback to be triggered even if its tacked Param's attribute is set to whatever it's currently at, we must use `p.param.watch(..., onlychanged=False)`.

4. Using `pn.rx` (reactive approach):
  `pn.rx(object)` is a new method that transforms any object (built-in types, Param, function, dataframe) into a reactive expression that tracks and manages its dependents through chains of computations/operations reflected on its state, and is only trigerred when needed (on demand) for UI rendering.

**Note**: You can additonally create reactive components by directly binding Params, widgets or bound functions to component Parameters.
  E.g.:
  ```python
  slider = pn.widgets.IntSlider(value=5, start=1, end=10, name='page_size')
  tabulator = pn.widgets.Tabulator(df, page_size=slider, pagination="remote")  # directly bind the value of "slider" widget to "page_size" Parameter
  ```
