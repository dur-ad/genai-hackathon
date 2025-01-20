import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from rag_model import get_rag_response, analyze_maize_image
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image
import base64
from io import BytesIO

#createdashapp
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.CYBORG,
        "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&display=swap"
    ]
)

#datastructures
class FarmData:
    @staticmethod
    def generate_time_series(days=30):
        dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(days)]
        return pd.DataFrame({'date': dates})

    @staticmethod
    def get_inventory_data():
        return {
            "crops": [
                {"name": "Maize", "quantity": 150, "unit": "kg", "status": "optimal"}
            ],
            "resources": [
                {"name": "Water", "level": 85, "unit": "%"},
                {"name": "Nutrients", "level": 72, "unit": "%"},
                {"name": "Growing Medium", "level": 90, "unit": "%"}
            ]
        }

    @staticmethod
    def get_plant_health_data():
        return {
            "current_metrics": [
                {"plant": "Maize", "health": 92, "pH": 6.2, "humidity": 65, "temperature": 23.5}
            ],
            "optimal_ranges": {
                "pH": {"min": 5.5, "max": 6.5},
                "humidity": {"min": 60, "max": 75},
                "temperature": {"min": 20, "max": 26}
            }
        }

    @staticmethod
    def get_system_status():
        return {
            "components": [
                {"name": "Irrigation System", "status": "operational", "efficiency": 95},
                {"name": "Climate Control", "status": "operational", "efficiency": 88},
                {"name": "Soil Monitoring", "status": "operational", "efficiency": 94},
                {"name": "Nutrient Delivery", "status": "maintenance_required", "efficiency": 82}
            ],
            "alerts": [
                {"type": "info", "message": "Maize growth rate optimal"},
                {"type": "warning", "message": "Nutrient levels need adjustment in 24 hours"},
                {"type": "info", "message": "Soil moisture at recommended levels"}
            ]
        }

#initdata
farm_data = FarmData()
inventory = farm_data.get_inventory_data()
plant_health = farm_data.get_plant_health_data()
system_status = farm_data.get_system_status()

#styling
CUSTOM_STYLE = {
    'background': '#1a1a1a',
    'text': '#ffffff',
    'accent': '#00ff9d',
    'card': '#2d2d2d',
    'font-family': 'Orbitron, sans-serif'
}

def create_alert_item(alert):
    #createalert
    colors = {
        'critical': '#ff0000',
        'warning': '#ffae00',
        'info': '#00ff9d'
    }
    
    return html.Div([
        html.Div(
            "●", 
            style={
                'color': colors[alert['type']],
                'marginRight': '10px',
                'display': 'inline-block',
                'animation': 'pulse 2s infinite' if alert['type'] == 'critical' else 'none'
            }
        ),
        html.Span(alert['message'], 
                 style={'color': CUSTOM_STYLE['text']})
    ], style={'marginBottom': '10px'})

def create_system_status_indicators(status_data):
    #createstatus
    components = []
    
    #systemstatus
    for comp in status_data['components']:
        color = {
            'operational': '#00ff9d',
            'maintenance_required': '#ffae00',
            'critical': '#ff0000'
        }.get(comp['status'], '#ff0000')
        
        components.append(
            dbc.Col(
                dbc.Card([
                    html.H4(comp['name'], 
                           style={'color': CUSTOM_STYLE['text'], 'fontSize': '1rem', 'marginBottom': '10px'}),
                    html.Div([
                        html.Div(f"{comp['efficiency']}%", 
                                style={'color': color, 'fontSize': '1.5rem', 'fontWeight': 'bold'}),
                        html.Div("Efficiency", 
                                style={'color': CUSTOM_STYLE['text'], 'fontSize': '0.8rem'})
                    ], style={'textAlign': 'center'})
                ], style={'backgroundColor': CUSTOM_STYLE['card'], 'padding': '15px'})
            )
        )
    
    return html.Div([
        dbc.Row(components, className="mb-4"),
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    html.H4("ACTIVE ALERTS", 
                           style={'color': CUSTOM_STYLE['accent'], 'marginBottom': '15px'}),
                    html.Div([create_alert_item(alert) for alert in status_data['alerts']])
                ], style={'backgroundColor': CUSTOM_STYLE['card'], 'padding': '15px'})
            )
        )
    ])

def create_inventory_table(crops_data):
    #createtable
    return html.Div([
        html.Table(
            [html.Tr([html.Th(col, style={'color': CUSTOM_STYLE['accent']}) 
                     for col in ['Crop', 'Quantity', 'Status']],
                    style={'borderBottom': f'2px solid {CUSTOM_STYLE["accent"]}'})] +
            [html.Tr([
                html.Td(crop['name']),
                html.Td(f"{crop['quantity']} {crop['unit']}"),
                html.Td(html.Div(
                    crop['status'].upper(),
                    style={
                        'color': {
                            'optimal': '#00ff9d',
                            'low': '#ffae00',
                            'critical': '#ff0000'
                        }.get(crop['status'], '#ffffff'),
                        'fontWeight': 'bold'
                    }
                ))
            ]) for crop in crops_data]
        , style={
            'width': '100%',
            'color': CUSTOM_STYLE['text'],
            'borderCollapse': 'collapse'
        })
    ])

def create_resource_gauges(resources_data):
    #creategauges
    return html.Div([
        dbc.Row([
            dbc.Col(
                create_gauge(resource['name'], resource['level'], resource['unit']),
                width=4
            ) for resource in resources_data
        ])
    ])

def create_gauge(name, level, unit):
    #createsinglegauge
    color = '#00ff9d' if level > 70 else '#ffae00' if level > 30 else '#ff0000'
    
    return html.Div([
        html.Div(
            style={
                'position': 'relative',
                'width': '80%',
                'paddingBottom': '80%',
                'margin': '0 auto',
            },
            children=[
                html.Div(
                    style={
                        'position': 'absolute',
                        'top': '0',
                        'left': '0',
                        'right': '0',
                        'bottom': '0',
                        'background': f'conic-gradient({color} {level}%, #333 0)',
                        'borderRadius': '50%',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center'
                    },
                    children=[
                        html.Div(
                            f"{level}{unit}",
                            style={
                                'background': CUSTOM_STYLE['card'],
                                'borderRadius': '50%',
                                'width': '70%',
                                'height': '70%',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'color': color,
                                'fontSize': 'clamp(0.8rem, 2vw, 1.2rem)',
                                'fontWeight': 'bold'
                            }
                        )
                    ]
                )
            ]
        ),
        html.Div(name, style={
            'textAlign': 'center',
            'marginTop': '5px',
            'color': CUSTOM_STYLE['text'],
            'fontSize': 'clamp(0.7rem, 1.5vw, 0.9rem)',
            'whiteSpace': 'nowrap',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis'
        })
    ], style={
        'width': '100%',
        'padding': '5px'
    })

def create_chat_interface():
    #createchatui
    return html.Div([
        dcc.Upload(
            id='upload-image',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Image', style={'color': CUSTOM_STYLE['accent']})
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px 0',
                'color': CUSTOM_STYLE['text'],
                'borderColor': CUSTOM_STYLE['accent'],
                'cursor': 'pointer'
            },
            multiple=False
        ),
        html.Div(id='output-image-upload')
    ])

def create_health_metrics(health_data):
    #createhealthmetrics
    metric = health_data['current_metrics'][0]
    optimal_ranges = health_data['optimal_ranges']
    
    return html.Div([
        #maingauge
        dbc.Row([
            dbc.Col(
                create_health_gauge(metric['health'], "Overall Health"),
                width=12,
                style={'marginBottom': '10px'}
            )
        ]),
        #additionalmetrics
        dbc.Row([
            dbc.Col([
                create_metric_pill("pH", metric['pH'], 
                                 f"{optimal_ranges['pH']['min']}-{optimal_ranges['pH']['max']}")
            ], width=4),
            dbc.Col([
                create_metric_pill("Humidity", metric['humidity'], 
                                 f"{optimal_ranges['humidity']['min']}-{optimal_ranges['humidity']['max']}")
            ], width=4),
            dbc.Col([
                create_metric_pill("Temp", metric['temperature'], 
                                 f"{optimal_ranges['temperature']['min']}-{optimal_ranges['temperature']['max']}")
            ], width=4),
        ])
    ])

def create_health_gauge(value, title):
    #createhealthgauge
    color = '#00ff9d' if value > 80 else '#ffae00' if value > 60 else '#ff0000'
    
    return html.Div([
        html.Div(
            style={
                'position': 'relative',
                'width': '100px',
                'height': '100px',
                'margin': '0 auto',
                'background': f'conic-gradient({color} {value}%, #333 0)',
                'borderRadius': '50%',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center'
            },
            children=[
                html.Div(
                    f"{value}%",
                    style={
                        'background': CUSTOM_STYLE['card'],
                        'borderRadius': '50%',
                        'width': '70%',
                        'height': '70%',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'color': color,
                        'fontSize': '1.2rem',
                        'fontWeight': 'bold'
                    }
                )
            ]
        ),
        html.Div(title, style={
            'textAlign': 'center',
            'marginTop': '5px',
            'color': CUSTOM_STYLE['text'],
            'fontSize': '0.9rem'
        })
    ])

def create_metric_pill(label, value, optimal_range):
    #createpill
    return html.Div([
        html.Div(label, style={
            'color': CUSTOM_STYLE['accent'],
            'fontSize': '0.8rem',
            'marginBottom': '2px'
        }),
        html.Div(f"{value}", style={
            'color': CUSTOM_STYLE['text'],
            'fontSize': '1.1rem',
            'fontWeight': 'bold'
        }),
        html.Div(f"Range: {optimal_range}", style={
            'color': '#888',
            'fontSize': '0.7rem'
        })
    ], style={
        'textAlign': 'center',
        'backgroundColor': '#1E1E1E',
        'padding': '8px',
        'borderRadius': '5px',
        'height': '100%'
    })

#mainlayout
app.layout = html.Div(style={
    'backgroundColor': CUSTOM_STYLE['background'],
    'minHeight': '100vh',
    'padding': '15px',
    'maxWidth': '100%',
    'overflow': 'hidden'
}, children=[
    #header
    dbc.Row([
        dbc.Col(html.H1("HYDROPONIC FARM CONTROL CENTER", 
                        style={'color': CUSTOM_STYLE['accent'], 
                               'textAlign': 'center',
                               'fontFamily': CUSTOM_STYLE['font-family'],
                               'marginBottom': '30px'}), 
                width=12)
    ]),
    
    #maincontent
    dbc.Row([
        #leftsection
        dbc.Col([
            # System Status Dashboard
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("MAIZE CULTIVATION STATUS", 
                                   style={'backgroundColor': CUSTOM_STYLE['accent'],
                                         'color': CUSTOM_STYLE['background']}),
                        dbc.CardBody(
                            [create_system_status_indicators(system_status)]
                        )
                    ], style={'backgroundColor': CUSTOM_STYLE['card']}),
                    width=12
                )
            ], className="mb-4"),

            # Combined Row for Health, Resources, and Inventory
            dbc.Row([
                # Health Monitoring
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("MAIZE HEALTH", 
                                   style={'backgroundColor': CUSTOM_STYLE['accent'],
                                         'color': CUSTOM_STYLE['background']}),
                        dbc.CardBody([
                            create_health_metrics(plant_health)
                        ], style={
                            'padding': '10px',
                            'height': '250px',  # Increased from 220px to 250px
                            'overflowY': 'auto'
                        })
                    ], style={
                        'backgroundColor': CUSTOM_STYLE['card'],
                        'height': '100%'
                    })
                ], width=4),
                
                # Resource Levels
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("RESOURCES", 
                                   style={'backgroundColor': CUSTOM_STYLE['accent'],
                                         'color': CUSTOM_STYLE['background']}),
                        dbc.CardBody([
                            create_resource_gauges(inventory['resources'])
                        ], style={
                            'padding': '10px',
                            'height': '250px',  # Increased from 220px to 250px
                            'overflowY': 'auto'
                        })
                    ], style={
                        'backgroundColor': CUSTOM_STYLE['card'],
                        'height': '100%'
                    })
                ], width=4),
                
                # Inventory
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("INVENTORY", 
                                   style={'backgroundColor': CUSTOM_STYLE['accent'],
                                         'color': CUSTOM_STYLE['background']}),
                        dbc.CardBody([
                            create_inventory_table(inventory['crops'])
                        ], style={
                            'padding': '10px',
                            'height': '250px',  # Increased from 220px to 250px
                            'overflowY': 'auto'
                        })
                    ], style={
                        'backgroundColor': CUSTOM_STYLE['card'],
                        'height': '100%'
                    })
                ], width=4)
            ], className="mb-4", style={'height': 'auto'})
        ], width=8, style={'paddingRight': '10px'}),
        
        #rightsection
        dbc.Col([
            # Image Upload Card
            dbc.Card([
                dbc.CardHeader("MAIZE IMAGE ANALYSIS", 
                            style={'backgroundColor': CUSTOM_STYLE['accent'],
                                  'color': CUSTOM_STYLE['background']}),
                dbc.CardBody([
                    dcc.Upload(
                        id='upload-image',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Image', style={'color': CUSTOM_STYLE['accent']})
                        ]),
                        style={
                            'width': '100%',
                            'height': '80px',  # Increased height
                            'lineHeight': '80px',  # Match height
                            'borderWidth': '2px',  # More visible border
                            'borderStyle': 'dashed',
                            'borderRadius': '10px',  # Increased radius
                            'textAlign': 'center',
                            'margin': '10px 0',
                            'color': CUSTOM_STYLE['text'],
                            'borderColor': CUSTOM_STYLE['accent'],
                            'cursor': 'pointer',
                            'fontSize': '1.1rem'  # Larger text
                        },
                        multiple=False
                    ),
                    html.Div(id='output-image-upload')
                ], style={
                    'height': '500px',  # Increased from 300px
                    'overflowY': 'auto',
                    'padding': '20px'  # Added padding
                })
            ], style={
                'backgroundColor': CUSTOM_STYLE['card'], 
                'marginBottom': '20px',
                'height': '550px'  # Set fixed height
            }),
            
            # Chat Interface Card
            dbc.Card([
                dbc.CardHeader("MAIZE ASSISTANT", 
                            style={'backgroundColor': CUSTOM_STYLE['accent'],
                                  'color': CUSTOM_STYLE['background']}),
                dbc.CardBody([
                    html.Div(
                        id='chat-history',
                        style={
                            'height': '300px',
                            'overflowY': 'auto',
                            'marginBottom': '20px',
                            'padding': '10px',
                            'backgroundColor': CUSTOM_STYLE['background'],
                            'borderRadius': '5px',
                            'border': f'1px solid {CUSTOM_STYLE["accent"]}'
                        }
                    ),
                    dbc.Input(
                        id='chat-input',
                        type='text',
                        placeholder='Ask about maize cultivation...',
                        style={
                            'backgroundColor': CUSTOM_STYLE['background'],
                            'color': CUSTOM_STYLE['text'],
                            'border': f'1px solid {CUSTOM_STYLE["accent"]}',
                            'marginBottom': '10px'
                        }
                    ),
                    dbc.Button(
                        "Send",
                        id='chat-button',
                        color='primary',
                        style={'backgroundColor': CUSTOM_STYLE['accent'], 'border': 'none'}
                    )
                ])
            ], style={
                'backgroundColor': CUSTOM_STYLE['card'],
                'height': 'calc(100vh - 600px)'  # Adjust this value to fit your layout
            })
        ], width=4, style={'paddingLeft': '10px'})
    ], className="g-0")
])

#imagecallback
@app.callback(
    Output('output-image-upload', 'children'),
    [Input('upload-image', 'contents')]
)
def update_image_upload(contents):
    if contents is None:
        raise dash.exceptions.PreventUpdate
    
    try:
        #decodeimage
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        image = Image.open(BytesIO(decoded))
        
        #getanalysis
        analysis_result = analyze_maize_image(image)
        
        #formatresults
        if analysis_result['success']:
            #statuscolor
            status_color = {
                'Healthy': '#00ff9d',
                'Spotted': '#ffae00',
                'Blighted': '#ff0000'
            }.get(analysis_result['health_status'], CUSTOM_STYLE['accent'])
            
            analysis_text = [
                html.Div([
                    html.Strong("Health Status: ", style={'color': CUSTOM_STYLE['accent']}),
                    html.Span(analysis_result['health_status'], 
                             style={'color': status_color, 'fontWeight': 'bold'})
                ]),
                html.Div([
                    html.Strong("Confidence: ", style={'color': CUSTOM_STYLE['accent']}),
                    html.Span(f"{analysis_result['confidence']:.1%}")
                ]),
                html.Div([
                    html.Strong("Analysis: ", style={'color': CUSTOM_STYLE['accent']}),
                    html.Span(analysis_result['description'])
                ]),
                html.Div([
                    html.Strong("Detected Features: ", style={'color': CUSTOM_STYLE['accent']}),
                    html.Span(", ".join(analysis_result['tags']))
                ])
            ]
        else:
            analysis_text = [
                html.Div([
                    html.Strong("Error: ", style={'color': '#ff0000'}),
                    html.Span(analysis_result['error'])
                ])
            ]
        
        return html.Div([
            # Image display
            html.Img(src=contents, style={
                'maxWidth': '400px',  # Increased from 300px
                'maxHeight': '400px',  # Increased from 300px
                'marginBottom': '20px',
                'borderRadius': '10px',
                'border': f'2px solid {CUSTOM_STYLE["accent"]}',
                'boxShadow': '0 0 10px rgba(0,255,157,0.3)'  # Added glow effect
            }),
            # Analysis results
            html.Div(analysis_text, style={
                'backgroundColor': '#1E1E1E',
                'padding': '15px',
                'borderRadius': '8px',
                'marginTop': '10px',
                'color': CUSTOM_STYLE['text'],
                'fontSize': '0.9rem',
                'lineHeight': '1.5'
            })
        ], style={
            'textAlign': 'center',
            'marginBottom': '20px'
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return html.Div([
            html.Strong("Error: ", style={'color': '#ff0000'}),
            html.Span(str(e))
        ])

#chatcallback
@app.callback(
    [Output('chat-history', 'children'),
     Output('chat-input', 'value')],
    [Input('chat-button', 'n_clicks'),
     Input('chat-input', 'n_submit')],
    [State('chat-input', 'value'),
     State('chat-history', 'children')]
)
def update_chat(n_clicks, n_submit, input_value, chat_history):
    if not dash.callback_context.triggered or not input_value:
        raise dash.exceptions.PreventUpdate
    
    if chat_history is None:
        chat_history = []
    
    #addusermessage
    chat_history.append(
        html.Div([
            html.Span("You: ", style={'color': CUSTOM_STYLE['accent'], 'fontWeight': 'bold'}),
            html.Span(input_value)
        ], style={'marginBottom': '10px'})
    )
    
    #getairesponse
    context = {
        'inventory': inventory,
        'plant_health': plant_health,
        'system_status': system_status
    }
    response = get_rag_response(input_value, context)
    
    #addairesponse
    chat_history.append(
        html.Div([
            html.Span("Farm Assistant: ", style={'color': CUSTOM_STYLE['accent'], 'fontWeight': 'bold'}),
            html.Span(response)
        ], style={'marginBottom': '10px'})
    )
    
    return chat_history, ''

if __name__ == '__main__':
    app.run_server(debug=True)
