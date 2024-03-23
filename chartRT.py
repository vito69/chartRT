
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import pandas_ta as ta
import requests
import datetime

app = Dash()

app.index_string = '''
<!DOCTYPE html>
<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='en' lang='en'>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

def create_dropdown(option, id_value):
	return html.Div(
		[
			html.Div(" ".join(id_value.replace('-', ' ').split(' ')[:-1]).capitalize(),
				style = {"padding":"0px 20px 0px 20px"}),
			dcc.Dropdown(option, id=id_value, value=option[2])
		],style = {"padding":"0px 20px 0px 20px"}
	)

app.layout = html.Div([

	html.Div([
		create_dropdown(['ETHUSD', 'ETHEUR', 'BTCEUR','BTCUSD', 'XRPUSD', 'XRPEUR'], 'coin-select'),
		create_dropdown(['60', '300', '900', '1800', '3600', '86400'],'timeframe-select'),
		create_dropdown(['20', '50', '100'], 'num-bars-select'),
		], style = {"display":"flex", "margin":"auto", "width":"800px",
			"justify-content":"space-around", "heigh":"30px"}
	),

	html.Div([
		dcc.RangeSlider(0,20,1, value = [0,20], id="range-slider"),
		], id="range-slider-container",
		style={"width":"800px", "margin":"auto", "padding-top":"5px"}
	),
	dcc.Graph(id="candles"),
	#dcc.Graph(id="indicator"),
	
	dcc.Interval(id="interval", interval=1000),
])
	
@app.callback(
	Output("range-slider-container", "children"),
	Input("num-bars-select", "value")
)
def update_rangeslider(num_bars):
	return dcc.RangeSlider(min=0, max=int(num_bars), step=int(int(num_bars)/20),
		value = [0, int(num_bars)], id="range-slider")
		
@app.callback(
	Output("candles", "figure"),
	#Output("indicator", "figure"),
	Input("interval", "n_intervals"),
	Input("coin-select", "value"),
	Input("timeframe-select", "value"),
	Input("num-bars-select", "value"),
	Input("range-slider", "value"),
)	
def update_figure(n_intervals, coin_pair, timeframe, num_bars, range_values):
	url = f"https://www.bitstamp.net/api/v2/ohlc/{coin_pair.lower()}/"
	params = {
		"step":timeframe,
		"limit":int(num_bars) + 14,
	}
	
	data = requests.get(url, params=params).json()["data"]["ohlc"]

	data = pd.DataFrame(data)
	data.timestamp = pd.to_datetime(data.timestamp.astype(float), unit="s")
	#data['rsi'] = ta.rsi(data.close.astype(float))
	data = data.iloc[14:]
	data = data.iloc[range_values[0]:range_values[1]]
	candles = go.Figure(
		data = [
			go.Candlestick(
				x = data.timestamp,
				open = data.open,
				high = data.high,
				low = data.low,
				close = data.close,
				increasing_line_color="#ffff99",
				increasing_fillcolor="#ffff99",
				decreasing_line_color="#7b3f00",
				decreasing_fillcolor="#7b3f00",
			)
		]
	)
	
	candles.update_layout(xaxis_rangeslider_visible=False, height = 600, template ="plotly_dark")
	candles.update_layout(transition_duration = 500)
	candles.update_layout(title='Open: '+data.iloc[-1:]['open'].to_string(index = False)+
		' | High: '+data[-1:]['high'].to_string(index=False)+
		' | Low: '+data[-1:]['low'].to_string(index=False)+
		' | Close: '+data[-1:]['close'].to_string(index=False)+
		'								'+datetime.datetime.now().strftime('%H:%M:%S')
		)
	candles.update_layout(font_color="#ffff99")
	#+' | /'+coin_pair+' / '+str(round(int(timeframe)/60))+' min. / '+num_bars, title_x=0.95

	#indicator = px.line(x=data.timestamp, y=data.rsi, height = 200, template ="plotly_dark", color_discrete_sequence=["chocolate"])
	#indicator.update_layout(transition_duration = 500)

	return candles#, indicator
	
if __name__ == '__main__':
	app.run_server(debug=True)
