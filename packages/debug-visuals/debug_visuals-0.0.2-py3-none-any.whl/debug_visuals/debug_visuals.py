# Needed to function imports
from typing import List, Any
import random
import json

# additional imports
try:
    from shapely.geometry.base import BaseGeometry
except ModuleNotFoundError:
    pass

try:
    from geopandas import GeoSeries, GeoDataFrame
except ModuleNotFoundError:
    pass


class Visualizer:
    """
    This is an abstract class that collects all visualization functions with a single import
    Use it in the file that you want to debug by importing it:
        `from debug_visuals import Visualizer`
    And use it inside the debug visualizer view:
        `Visualizer.vis(your_variable)`
    """

    @staticmethod
    def vis(var: Any) -> str:
        if isinstance(var, list):
            if all([isinstance(val, (int, float)) for val in var]):
                return Visualizer.value_graph([var])

            elif all([isinstance(val, BaseGeometry) for val in var]):
                return Visualizer.shape(var)

            else:
                # nodes with arrows of str(val) for val in var
                return Visualizer.vis_list(var)

        if isinstance(var, BaseGeometry):
            return Visualizer.shape(var)

        if isinstance(var, GeoDataFrame):
            return Visualizer.shape([geom for geom in var.geometry])
        if isinstance(var, GeoSeries):
            return Visualizer.shape([geom for geom in var])

        if isinstance(var, dict):
            return Visualizer.vis_dict(var)

        return json.dumps(
            {
                "kind": {"text": True},
                "text": f"Unknown Type: {var.__class__.__name__}"
            }
        )

    @staticmethod
    def _coords_to_xy(coords):
        """
        Given a sequence of Shapely coordinates, return separate lists of x and y.
        Ensures the ring is closed if it's a polygon boundary.
        """
        if len(coords) > 1 and coords[0] != coords[-1]:
            # For polygon boundaries, Shapely often includes the closing
            # coordinate anyway, but just in case, we can ensure the
            # ring is closed:
            coords = list(coords) + [coords[0]]

        xs, ys = zip(*coords)
        return list(xs), list(ys)

    @staticmethod
    def geometry_to_plotly_traces(geom: BaseGeometry, cnt = None):
        """
        Convert a Shapely geometry into a list of Plotly trace dictionaries.
        Each trace is an item in the 'data' array of a Plotly figure.
        """
        h = random.randrange(0, 256, 1)
        color = f"hsla({h}, 100%, 50%, 0.5)"
        fill_color = f"hsla({h}, 100%, 50%, 0.1)"
        name_prefix = None
        if cnt is not None:
            name_prefix = f"{cnt}: "
        traces = []
        geom_type = geom.geom_type.lower()

        if geom.is_empty:
            return traces  # no trace for empty geometry

        if geom_type == "point":
            # Single point
            x, y = geom.x, geom.y
            traces.append({
                "type": "scatter",
                "x": [x],
                "y": [y],
                "mode": "markers",
                "marker": {"color": color},
                "name": name_prefix + "Point"
            })

        elif geom_type == "linestring" or geom_type == "linearring":
            x, y = Visualizer._coords_to_xy(geom.coords)
            traces.append({
                "type": "scatter",
                "x": x,
                "y": y,
                "mode": "lines",
                "line": {"color": color},
                "name": name_prefix + geom.__class__.__name__
            })

        elif geom_type == "polygon":
            # Exterior ring
            exterior_x, exterior_y = Visualizer._coords_to_xy(geom.exterior.coords)
            traces.append({
                "type": "scatter",
                "x": exterior_x,
                "y": exterior_y,
                "mode": "lines",
                "fill": "toself",    # fill the polygon
                "fillcolor": fill_color,
                "line": {"color": color},
                "name": name_prefix + "Polygon Exterior"
            })

            # Interior rings (holes)
            for i, interior in enumerate(geom.interiors):
                interior_x, interior_y = Visualizer._coords_to_xy(interior.coords)
                traces.append({
                    "type": "scatter",
                    "x": interior_x,
                    "y": interior_y,
                    "mode": "lines",
                    "fill": "tonext",  # subtract from previous fill
                    "fillcolor": fill_color,
                    "line": {"color": color, "dash": "dot"},
                    "name": f"    |-  Hole {i}"
                })

        elif geom_type.startswith("multi") or geom_type == "geometrycollection":
            # MultiPoint, MultiLineString, MultiPolygon, or GeometryCollection
            for i, part in enumerate(geom.geoms):
                traces.extend(Visualizer.geometry_to_plotly_traces(part, cnt = f"{cnt}.{i}"))

        return traces

    @staticmethod
    def shape(geom: BaseGeometry | List[BaseGeometry],
              title="Shapely Geometry") -> str:
        """
        Return a dictionary in the PlotlyVisualizationData format,
        so VS Code Debug Visualizer can render it as a Plotly chart.
        """
        geoms = geom
        if isinstance(geom, BaseGeometry):
            geoms = [geom]

        traces = []
        for i, g in enumerate(geoms):
            traces.extend(Visualizer.geometry_to_plotly_traces(g, i))

        # Basic 2D layout
        layout = {
            "title": title,
            # Make axes square-ish and centered
            "xaxis": {
                "title": "X",
                "zeroline": False
            },
            "yaxis": {
                "title": "Y",
                "zeroline": False,
                "scaleanchor": "x",
                "scaleratio": 1
            },
            "showlegend": True,
        }

        return json.dumps(
            {
                "kind": {"plotly": True},
                "data": traces,
                "layout": layout
            }
        )

    @staticmethod
    def vis_list(data) -> str:
        nodes = []
        edges = []
        for i, elem in enumerate(data):
            nodes.append(
                {
                    "id": str(i + 1),
                    "label": str(elem)
                }
            )

        for i in range(1, len(data)):
            edges.append(
                {
                    "from": str(i),
                    "to": str(i + 1),
                    "color": "blue"
                }
            )
        d = {
            "kind": {
                "graph": True
            },
            "nodes": nodes,
            "edges": edges
        }
        return json.dumps(d)

    @staticmethod
    def value_graph(data_lists) -> str:
        data = [{"y": list} for list in data_lists]
        d = {
            "kind": {"plotly": True},
            "data": data,
        }
        return json.dumps(d)

    @staticmethod
    def vis_dict(data: dict):

        def key_val_to_child(key, value) -> dict:
            if isinstance(value, (dict, list)):
                sub_children = []
                if isinstance(value, dict):
                    sub_children = [key_val_to_child(k, v) for k, v in value.items()]
                elif isinstance(value, list):
                    sub_children = [key_val_to_child(i, v) for i, v in enumerate(value)]
                child = {
                    "items": [
                        {
                            "text": str(key),
                            "emphasis": "style1"
                        },
                        {
                            "text": "...",
                            "emphasis": "style2"
                        },
                        {
                            "text": value.__class__.__name__,
                            "emphasis": "style3"
                        }
                    ],
                    "children": sub_children
                }
                return child
            else:
                child = {
                    "items": [
                        {
                            "text": str(key),
                            "emphasis": "style1"
                        },
                        {
                            "text": str(value),
                            "emphasis": "style2"
                        },
                        {
                            "text": value.__class__.__name__,
                            "emphasis": "style3"
                        }
                    ],
                    "children": []
                }
                return child

        children = []
        for key, value in data.items():
            children.append(key_val_to_child(key, value))

        d = {
            "kind": {
                "tree": True,
                "ast": True
            },
            "root": {
                "items": [
                    {
                        "text": "Dictionary: ",
                        "emphasis": "style1"
                    },
                    {
                        "text": "...",
                        "emphasis": "style2"
                    },
                    {
                        "text": data.__class__.__name__,
                        "emphasis": "style3"
                    }
                ],
                "children": children
            }
        }
        return json.dumps(d)
