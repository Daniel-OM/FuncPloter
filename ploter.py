
import itertools
import math

import pandas as pd
import plotly.graph_objects as go


def plotFunction(functions:(list or function), start:int, stop:int, step:float=1) -> None:

    # In case there is a step of type float
    if '.' in str(step):
        mult = int('1' + '0'*len(str(step).split('.')[-1]))
    else:
        mult = 1
    # Generate the x and y axis
    axis = [i/mult for i in range(start, int(stop*mult), int(step*mult))]

    # If a function was passed create the list
    if not isinstance(functions, list):
        functions = [functions]

    # Iterate over each function of the list
    series = []
    data: pd.DataFrame = pd.DataFrame({'x':axis})

    for i, func in enumerate(functions):
        dimensions = func.__code__.co_argcount

        # If it is a 2D function
        if dimensions == 1:
            data[f'y{i}'] = func(data['x'])
            series.append(go.Scatter(x=data['x'], y=data[f'y{i}']))

        # If it is a 3D function
        elif dimensions == 2:
            if 'y' not in data:
                data['y'] = axis
            temp = pd.DataFrame(data=list(itertools.product(data['x'], data['y'])), columns=['x', 'y'])
            temp['z'] = func(temp['x'], temp['y'])
            data[f'z{i}'] = temp.groupby('y')['z'].apply(list)
            series.append(go.Surface(z=data[f'z{i}'].values, x=data['x'], y=data['y']))

        # If it has more than 3 dimensions raise an error
        else:
            raise ValueError('Function with more than 3 dimensions can\'t be ploted.')

    # Generate chart to plot
    fig: go.Figure = go.Figure(data=series)
    fig.update_layout(title='Function plot', autosize=False,
                  width=500, height=500,
                  margin=dict(l=65, r=50, b=65, t=90))
    fig.show()


if __name__ == '__main__':
    func1 = lambda x: 2*(x.apply(lambda v: math.sin(v)) if isinstance(x, pd.Series) else math.sin(x))
    func2 = lambda x: (x.apply(lambda v: math.sin(v)) if isinstance(x, pd.Series) else math.sin(x))
    func3 = lambda x: (x.apply(lambda v: math.sin(2*v)) if isinstance(x, pd.Series) else math.sin(2*x))
    func4 = lambda x: (x.apply(lambda v: math.sin(v)) if isinstance(x, pd.Series) else math.sin(x)) + 2
    plotFunction([func1, func2, func3, func4], 0, 20, 0.1)
