
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import random
import io
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402


def get_graph(ticker, graph_type='Tick', variables=None, x=None):
    plt.rcParams["figure.figsize"] = (16, 10)
    fig, ax = plt.subplots()
    name = x

    if x is None:
        x = ticker.index.values
        name = ticker.index.name
    else:
        x = ticker[x]

    if variables is None:
        variables = ['Close']

    if graph_type == 'Tick':
        for index, val in enumerate(variables):
            y = ticker[val]
            if index > 0:
                upper_bound = max(y)
                if upper_bound > 100000:
                    scale = 'log'
                else:
                    scale = 'linear'

                twin = ax.twinx()
                r = random.random()
                g = random.random()
                b = random.random()
                color = (r, g, b)
                twin.plot(x, y, color=color, label=val)
                twin.set_yscale(scale)
                twin.set_ylabel(val, fontsize=16)
                twin.yaxis.label.set_color(color)
                twin.tick_params(axis='y', labelcolor=color)

                if index > 1:
                    twin.spines.right.set_position(("axes", 1.2))

                continue

            c, = ax.plot(x, y, label=val)
            ax.set_ylabel(val, fontsize=16)
            ax.yaxis.label.set_color(c.get_color())
            ax.tick_params(axis='y', labelcolor=c.get_color())

        return fig

    if graph_type == 'Hist':
        for index, val in enumerate(variables):
            r = random.random()
            g = random.random()
            b = random.random()
            color = (r, g, b)
            y = ticker[val]
            if index > 0:
                upper_bound = max(y)
                if upper_bound > 100000:
                    log = True
                else:
                    log = False
                twin = ax.twinx()
                twin.hist(x, weights=y, color=color, label=val, log=log, alpha=0.5)
                twin.set_ylabel(val)
                twin.yaxis.label.set_color(color)
                twin.tick_params(axis='y', labelcolor=color)

                if index > 1:
                    twin.spines.right.set_position(("axes", 1.2))

                continue

            ax.hist(x, weights=y, color=color, label=val, alpha=0.5)
            ax.set_ylabel(val)
            ax.set_xlabel(name)
            ax.yaxis.label.set_color(color)
            ax.tick_params(axis='y', labelcolor=color)

        return fig

    if graph_type == 'Scatter':
        r = random.random()
        g = random.random()
        b = random.random()
        color = (r, g, b)
        if len(variables) >= 2:
            y = ticker[variables[0]]
            x = ticker[variables[1]]

        upper_bound_y = max(y)
        upper_bound_x = max(x)
        if upper_bound_y > 100000:
            log_y = True
        else:
            log_y = False
        if upper_bound_x > 100000:
            log_x = True
        else:
            log_x = False
        ax.scatter(x, y, color=color, alpha=0.5)
        ax.set_ylabel(variables[0])
        ax.set_xlabel(variables[1])
        if log_y:
            ax.set_yscale('log')
        if log_x:
            ax.set_xscale('log')
        ax.yaxis.label.set_color(color)
        ax.tick_params(axis='y', labelcolor=color)

    return fig


def format_graph(graph):
    output = io.BytesIO()
    FigureCanvas(graph).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

