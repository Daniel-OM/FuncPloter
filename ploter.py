
import itertools

import numpy as np
import pandas as pd
import plotly.graph_objects as go


def plotFunction(functions:(list or function), xstart:int, xstop:int, xstep:float=1, xname:str='x',
                 ystart:int=None, ystop:int=None, ystep:float=1, yname:str='y', zname:str='z'
                 ) -> (go.Figure, pd.DataFrame):
    
    ystart = xstart if ystart == None else ystart
    ystop = xstop if ystop == None else ystop

    # In case there is a step of type float
    xmult = int('1' + '0'*len(str(xstep).split('.')[-1])) if '.' in str(xstep) else 1
    ymult = int('1' + '0'*len(str(ystep).split('.')[-1])) if '.' in str(ystep) else 1
    
    # Generate the x and y axis
    xaxis = [i/xmult for i in range(int(xstart*xmult), int(xstop*xmult), int(xstep*xmult))]
    yaxis = [i/ymult for i in range(int(ystart*ymult), int(ystop*ymult), int(ystep*ymult))]
    
    if len(yaxis) < len(xaxis):
        yaxis = list(np.linspace(ystart, ystop, len(xaxis)))
    elif len(yaxis) > len(xaxis):
        xaxis = list(np.linspace(xstart, xstop, len(yaxis)))

    # If a function was passed create the list
    if not isinstance(functions, list):
        functions = [functions]
        
    # Iterate over each function of the list
    series = []
    data: pd.DataFrame = pd.DataFrame({'x':xaxis})

    for i, f in enumerate(functions):
        dimensions = f.__code__.co_argcount

        # If it is a 2D function
        if dimensions == 1:
            func = lambda x: (x.apply(lambda v: f(v)) if isinstance(x, pd.Series) else f(x))
            data[f'y{i}'] = func(data['x'])
            series.append(go.Scatter(x=data['x'], y=data[f'y{i}']))

        # If it is a 3D function
        elif dimensions == 2:
            func = lambda x, y: (f(x, y) if isinstance(x, pd.Series) else f(x, y))
            if 'y' not in data:
                data['y'] = yaxis
            temp = pd.DataFrame(data=list(itertools.product(data['x'], data['y'])), columns=['x', 'y'])
            temp['z'] = func(temp['x'], temp['y'])
            data.set_index('y', drop=True, inplace=True)
            data[f'z{i}'] = temp.groupby('y')['z'].apply(list)
            data.reset_index(drop=False, inplace=True)
            series.append(go.Surface(z=data[f'z{i}'].values, x=data['x'], y=data['y']))
            
        # If it has more than 3 dimensions raise an error
        else:
            raise ValueError('Function with more than 3 dimensions can\'t be ploted.')

        
    # Generate chart to plot
    fig: go.Figure = go.Figure(data=series)

    if dimensions == 1:
        fig.update_xaxes(title=xname)
        fig.update_yaxes(title=yname)

    # If it is a 3D function
    elif dimensions == 2:
        fig.update_layout(
            scene = {
                'xaxis_title': xname,
                'yaxis_title': yname,
                'zaxis_title': zname
            }
        )

    fig.update_layout(title='Function plot', autosize=False,
                  width=700, height=700,
                  margin=dict(l=20, r=20, b=20, t=30))
    fig.show()

    return fig, data


if __name__ == '__main__':

    import math

    # func1 = lambda x: (x.apply(lambda v: 2*math.sin(v)) if isinstance(x, pd.Series) else 2*math.sin(x))
    # func2 = lambda x: (x.apply(lambda v: math.sin(v)) if isinstance(x, pd.Series) else math.sin(x))
    # func3 = lambda x: (x.apply(lambda v: math.sin(2*v)) if isinstance(x, pd.Series) else math.sin(2*x))
    # func4 = lambda x: (x.apply(lambda v: math.sin(v) + 2) if isinstance(x, pd.Series) else math.sin(x) + 2)

    func1 = lambda x, y: (x * y - (1 - x)) * 100
    func2 = lambda x, y: (x - (1 - x)/y) * 100 if (x - (1 - x)/y) > 0 else 0
    func2 = lambda x, y: np.where((x - (1 - x)/y) > 0, (x - (1 - x)/y) * 100, 0)
    fig, data = plotFunction(func2, xstart=0.2, xstop=1, xstep=0.05, xname='Probabilidad de Ganar', 
                       ystart=0.5, ystop=6, ystep=0.2, yname='Ratio Beneficio-Riesgo', 
                       zname='Tamaño de Kelly')
