import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
warnings.filterwarnings('ignore')

# Professional Color Scheme
COLORS = {
    "primary": "#2E86AB", "secondary": "#A23B72", "accent": "#F18F01",
    "success": "#4CAF50", "danger": "#F44336", "warning": "#FF9800",
    "light_bg": "#F8F9FE", "card_bg": "#FFFFFF", "text": "#2C3E50"
}

st.set_page_config(page_title="✈️ Beautiful Aviation Dashboard", layout="wide")

# Light Theme CSS
st.markdown("""
<style>
    .main { 
        background: linear-gradient(135deg, #F8F9FE 0%, #E8F4FD 100%); 
        font-family: 'Segoe UI', sans-serif; 
    }
    .tab-header { 
        font-size: 3.5rem; font-weight: bold; text-align: center; 
        color: #2E86AB; margin: 2rem 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(145deg, #FFFFFF 0%, #F1F8FF 100%);
        padding: 2.5rem; border-radius: 25px; text-align: center; 
        margin: 1rem 0; border: 2px solid #E3F2FD;
        box-shadow: 0 8px 32px rgba(46, 134, 171, 0.15);
    }
    .metric-number {
        font-size: 2.8rem; font-weight: bold; color: #2E86AB;
    }
    .metric-label {
        font-size: 1.2rem; color: #546E7A; margin-top: 0.5rem;
    }
    .crash-details {
        background: #FFFFFF; padding: 1.5rem; border-radius: 15px;
        border: 2px solid #E3F2FD; margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(46, 134, 171, 0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px; padding: 0px 24px;
        background-color: #FFFFFF; border-radius: 15px;
        border: 2px solid #E3F2FD; color: #2E86AB;
        font-size: 18px; font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2E86AB; color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/dataset.csv.csv', encoding="utf-8")
    except:
        df = pd.read_csv('data/dataset.csv.csv', encoding="latin1")
    
    df.columns = [c.strip() for c in df.columns]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['year'] = df['Date'].dt.year
    df['month'] = df['Date'].dt.month
    df['month_name'] = df['Date'].dt.strftime('%b')
    df['day_of_week'] = df['Date'].dt.dayofweek
    df['day_name'] = df['Date'].dt.strftime('%A')
    df['season'] = df['month'].apply(lambda x: 'Winter' if x in [12, 1, 2] else 'Spring' if x in [3, 4, 5] else 'Summer' if x in [6, 7, 8] else 'Fall')
    df['decade'] = (df['year'] // 10) * 10
    
    for col in ['Aboard', 'Fatalities', 'Ground']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(0)
    
    df['Operator'] = df['Operator'].fillna('Unknown').astype(str)
    df['Location'] = df['Location'].fillna('Unknown').astype(str)
    df['Type'] = df['Type'].fillna('Unknown').astype(str)
    df['Summary'] = df['Summary'].fillna('No details available').astype(str)
    
    # Add coordinates
    coords_map = {
        'virginia': (37.43, -78.66), 'california': (36.78, -119.42),
        'new york': (42.17, -74.95), 'texas': (31.97, -99.90),
        'florida': (27.77, -82.64), 'germany': (51.17, 10.45),
        'france': (46.23, 2.21), 'england': (55.38, -3.44),
        'canada': (56.13, -106.35), 'japan': (36.20, 138.25),
        'russia': (61.52, 105.32), 'china': (35.86, 104.20),
        'united states': (39.83, -98.58), 'pacific': (10.0, -140.0)
    }
    
    def get_coords(location):
        if pd.isna(location):
            return np.random.uniform(-60, 60), np.random.uniform(-180, 180)
        loc_lower = str(location).lower()
        for key, coords in coords_map.items():
            if key in loc_lower:
                return coords
        return np.random.uniform(-60, 60), np.random.uniform(-180, 180)

    coords = df['Location'].apply(get_coords)
    df['latitude'] = [c[0] for c in coords]
    df['longitude'] = [c[1] for c in coords]
    
    return df

def create_interactive_3d_globe(df, selected_year):
    """Interactive 3D Globe with enhanced tooltips"""
    filtered_df = df[df['year'] == selected_year] if selected_year else df
    
    if len(filtered_df) == 0:
        return None
    
    # Create enhanced hover text with detailed information
    hover_texts = []
    for _, row in filtered_df.iterrows():
        survival_rate = ((row['Aboard'] - row['Fatalities']) / row['Aboard'] * 100) if row['Aboard'] > 0 else 0
        hover_text = (
            f"<b>🛫 {row['Operator']}</b><br>"
            f"<b>📅 Date:</b> {row['Date'].strftime('%B %d, %Y')}<br>"
            f"<b>📍 Location:</b> {row['Location']}<br>"
            f"<b>✈️ Aircraft:</b> {row['Type']}<br>"
            f"<b>💀 Fatalities:</b> {int(row['Fatalities'])} / {int(row['Aboard'])} aboard<br>"
            f"<b>📊 Survival Rate:</b> {survival_rate:.1f}%<br>"
            f"<b>🌍 Ground Casualties:</b> {int(row['Ground'])}<br>"
            f"<b>📝 Summary:</b> {row['Summary'][:100]}..."
        )
        hover_texts.append(hover_text)
    
    fig = go.Figure(go.Scattergeo(
        lon=filtered_df['longitude'], lat=filtered_df['latitude'], 
        mode='markers',
        marker=dict(
            size=np.log1p(filtered_df['Fatalities']) * 2 + 6,
            color=filtered_df['Fatalities'], 
            colorscale=[[0, COLORS['success']], [0.5, COLORS['warning']], [1, COLORS['danger']]],
            opacity=0.8, colorbar=dict(title="Fatalities"),
            line=dict(width=1, color='white')
        ),
        text=hover_texts,
        hovertemplate="%{text}<extra></extra>"
    ))
    
    fig.update_geos(projection_type="orthographic", showcountries=True)
    fig.update_layout(
        title=dict(
            text=f"🌍 3D Globe - {len(filtered_df):,} Crashes" + (f" ({selected_year})" if selected_year else ""),
            font=dict(size=24, color=COLORS['text'])
        ),
        height=650, paper_bgcolor='white', font=dict(color=COLORS['text'], size=16)
    )
    return fig

def create_racing_sticks_animation(df):
    """ULTRA-SMOOTH Racing Animation with enhanced tooltips"""
    
    # Prepare monthly data
    monthly_data = df.groupby(['year', 'month']).agg({
        'Date': 'count',
        'Fatalities': 'sum'
    }).reset_index()
    monthly_data.columns = ['year', 'month', 'crashes', 'fatalities']
    
    # Add month names
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                  7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    monthly_data['month_name'] = monthly_data['month'].map(month_names)
    
    years = sorted(monthly_data['year'].unique())
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Scale values for visual balance
    max_crashes = monthly_data['crashes'].max()
    max_fatalities = monthly_data['fatalities'].max()
    scale_factor = max_crashes / max(max_fatalities, 1) if max_fatalities > 0 else 1
    
    fig = go.Figure()
    frames = []
    
    # Create animation frames (every 3rd year for smooth performance)
    for end_year in years[::3]:
        year_data = monthly_data[monthly_data['year'] == end_year]
        
        # Purple bars for crashes (partially transparent)
        crash_data = [0] * 12
        fatality_data = [0] * 12
        crash_hover = [""] * 12
        fatality_hover = [""] * 12
        
        for _, row in year_data.iterrows():
            month_idx = int(row['month']) - 1
            crash_data[month_idx] = row['crashes']
            fatality_data[month_idx] = row['fatalities'] * scale_factor
            
            # Enhanced hover text
            crash_hover[month_idx] = (
                f"<b>📅 {row['month_name']} {end_year}</b><br>"
                f"<b>✈️ Total Crashes:</b> {int(row['crashes'])}<br>"
                f"<b>📊 Monthly Rank:</b> #{sorted(crash_data, reverse=True).index(row['crashes']) + 1 if row['crashes'] > 0 else 'N/A'}"
            )
            
            fatality_hover[month_idx] = (
                f"<b>📅 {row['month_name']} {end_year}</b><br>"
                f"<b>💀 Total Fatalities:</b> {int(row['fatalities'])}<br>"
                f"<b>📈 Avg per Crash:</b> {row['fatalities']/row['crashes']:.1f}" if row['crashes'] > 0 else ""
            )
        
        frame = go.Frame(
            data=[
                # Purple racing bars (crashes)
                go.Bar(
                    x=months,
                    y=crash_data,
                    name='Crashes',
                    marker=dict(
                        color='rgba(147, 112, 219, 0.7)',
                        line=dict(color='rgba(147, 112, 219, 1)', width=2)
                    ),
                    text=[f"{int(val)}" if val > 0 else "" for val in crash_data],
                    textposition='outside',
                    textfont=dict(size=14, color='purple', family='Arial Black'),
                    textangle=0,
                    hovertext=crash_hover,
                    hovertemplate="%{hovertext}<extra></extra>",
                    offsetgroup=1
                ),
                # Blue racing bars (fatalities scaled)
                go.Bar(
                    x=months,
                    y=fatality_data,
                    name='Fatalities (scaled)',
                    marker=dict(
                        color='rgba(70, 130, 180, 0.7)',
                        line=dict(color='rgba(70, 130, 180, 1)', width=2)
                    ),
                    text=[f"{int(val/scale_factor)}" if val > 0 else "" for val in fatality_data],
                    textposition='outside',
                    textfont=dict(size=14, color='steelblue', family='Arial Black'),
                    textangle=0,
                    hovertext=fatality_hover,
                    hovertemplate="%{hovertext}<extra></extra>",
                    offsetgroup=2
                )
            ],
            name=str(end_year)
        )
        frames.append(frame)
    
    # Initial frame setup
    initial_year = years[0]
    initial_data = monthly_data[monthly_data['year'] == initial_year]
    
    initial_crashes = [0] * 12
    initial_fatalities = [0] * 12
    initial_crash_hover = [""] * 12
    initial_fatality_hover = [""] * 12
    
    for _, row in initial_data.iterrows():
        month_idx = int(row['month']) - 1
        initial_crashes[month_idx] = row['crashes']
        initial_fatalities[month_idx] = row['fatalities'] * scale_factor
        
        initial_crash_hover[month_idx] = (
            f"<b>📅 {row['month_name']} {initial_year}</b><br>"
            f"<b>✈️ Total Crashes:</b> {int(row['crashes'])}<br>"
            f"<b>📊 Monthly Rank:</b> #{sorted(initial_crashes, reverse=True).index(row['crashes']) + 1 if row['crashes'] > 0 else 'N/A'}"
        )
        
        initial_fatality_hover[month_idx] = (
            f"<b>📅 {row['month_name']} {initial_year}</b><br>"
            f"<b>💀 Total Fatalities:</b> {int(row['fatalities'])}<br>"
            f"<b>📈 Avg per Crash:</b> {row['fatalities']/row['crashes']:.1f}" if row['crashes'] > 0 else ""
        )
    
    # Add initial traces
    fig.add_trace(go.Bar(
        x=months,
        y=initial_crashes,
        name='Crashes',
        marker=dict(
            color='rgba(147, 112, 219, 0.7)',
            line=dict(color='rgba(147, 112, 219, 1)', width=2)
        ),
        text=[f"{int(val)}" if val > 0 else "" for val in initial_crashes],
        textposition='outside',
        textfont=dict(size=12, color='purple'),
        hovertext=initial_crash_hover,
        hovertemplate="%{hovertext}<extra></extra>",
        offsetgroup=1
    ))
    
    fig.add_trace(go.Bar(
        x=months,
        y=initial_fatalities,
        name='Fatalities (scaled)',
        marker=dict(
            color='rgba(70, 130, 180, 0.7)',
            line=dict(color='rgba(70, 130, 180, 1)', width=2)
        ),
        text=[f"{int(val/scale_factor)}" if val > 0 else "" for val in initial_fatalities],
        textposition='outside',
        textfont=dict(size=12, color='steelblue'),
        hovertext=initial_fatality_hover,
        hovertemplate="%{hovertext}<extra></extra>",
        offsetgroup=2
    ))
    
    fig.frames = frames
    
    # Update layout
    fig.update_layout(
        title={
            'text': "🏁 ULTRA-SMOOTH RACING STICKS (Purple vs Blue)",
            'font': {'size': 32, 'color': COLORS['text'], 'family': 'Arial Black'},
            'x': 0.5
        },
        xaxis={
            'title': {'text': "Months (Racing Arena)", 'font': {'size': 18}},
            'tickfont': {'size': 16}
        },
        yaxis={
            'title': {'text': "Racing Values", 'font': {'size': 18}},
            'tickfont': {'size': 16},
            'range': [0, max(max_crashes, max_fatalities * scale_factor) * 1.2]
        },
        height=800,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font={'color': COLORS['text'], 'size': 16},
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        margin={'l': 80, 'r': 80, 't': 120, 'b': 80},
        annotations=[
            {
                'text': "🟣 Purple = Crashes | 🔵 Blue = Fatalities (scaled) | Both bars race smoothly up & down!",
                'showarrow': False,
                'xref': "paper", 'yref': "paper",
                'x': 0.5, 'y': -0.12,
                'xanchor': 'center', 'yanchor': 'bottom',
                'font': {'size': 16, 'color': COLORS['secondary']}
            }
        ],
        updatemenus=[
            {
                'type': 'buttons',
                'buttons': [
                    {
                        'label': '🏁 RACE FAST (0.8s)',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 800, 'redraw': True},
                            'transition': {'duration': 400, 'easing': 'cubic-in-out'}
                        }]
                    },
                    {
                        'label': '🏃 RACE NORMAL (2s)',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 2000, 'redraw': True},
                            'transition': {'duration': 800, 'easing': 'cubic-in-out'}
                        }]
                    },
                    {
                        'label': '🚶 RACE SLOW (4s)',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 4000, 'redraw': True},
                            'transition': {'duration': 1200, 'easing': 'cubic-in-out'}
                        }]
                    },
                    {
                        'label': '⏸️ PAUSE',
                        'method': 'animate',
                        'args': [[None]]
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 10},
                'showactive': False,
                'bgcolor': COLORS['card_bg'],
                'bordercolor': COLORS['primary'],
                'borderwidth': 2,
                'font': {'size': 14, 'color': COLORS['text']},
                'x': 0.02, 'xanchor': 'left',
                'y': 1.08, 'yanchor': 'top'
            }
        ],
        sliders=[
            {
                'steps': [
                    {
                        'args': [[frame['name']], {
                            'frame': {'duration': 0, 'redraw': True},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }],
                        'label': str(frame['name']),
                        'method': 'animate'
                    } for frame in frames
                ],
                'active': 0,
                'currentvalue': {
                    'font': {'size': 18, 'color': COLORS['text']},
                    'prefix': '🏁 Racing Year: ',
                    'visible': True,
                    'xanchor': 'center'
                },
                'len': 0.8,
                'pad': {'b': 10, 't': 10},
                'transition': {'duration': 800, 'easing': 'cubic-in-out'},
                'x': 0.1, 'xanchor': 'left',
                'y': 0, 'yanchor': 'top'
            }
        ]
    )
    
    return fig

def create_crash_reasons_chart(df, selected_years=None):
    """Pie chart for crash reasons with enhanced tooltips"""
    filtered_df = df
    if selected_years:
        filtered_df = df[df['year'].between(selected_years[0], selected_years[1])]
    
    reasons = []
    for summary in filtered_df['Summary'].fillna('Unknown'):
        summary_lower = str(summary).lower()
        if 'weather' in summary_lower or 'storm' in summary_lower:
            reasons.append('Weather')
        elif 'engine' in summary_lower or 'mechanical' in summary_lower:
            reasons.append('Mechanical')
        elif 'pilot' in summary_lower or 'crew' in summary_lower:
            reasons.append('Human Error') 
        elif 'fire' in summary_lower:
            reasons.append('Fire')
        else:
            reasons.append('Other')
    
    reason_counts = pd.Series(reasons).value_counts()
    total_crashes = len(reasons)
    
    # Enhanced hover text
    hover_texts = [
        f"<b>{reason}</b><br>"
        f"<b>Count:</b> {count}<br>"
        f"<b>Percentage:</b> {count/total_crashes*100:.1f}%<br>"
        f"<b>Rank:</b> #{i+1} most common"
        for i, (reason, count) in enumerate(reason_counts.items())
    ]
    
    colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent'], 
             COLORS['success'], COLORS['warning'], COLORS['danger']]
    
    fig = go.Figure(go.Pie(
        labels=reason_counts.index, values=reason_counts.values,
        marker=dict(colors=colors[:len(reason_counts)], line=dict(color='white', width=3)),
        textinfo='label+percent',
        textfont=dict(size=18, color='white', family='Arial Black'),
        textposition='inside',
        pull=[0.05] * len(reason_counts),
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=dict(
            text=f"🎯 Crash Reasons{year_text}",
            font=dict(size=24, color=COLORS['text'])
        ),
        height=600,
        paper_bgcolor=COLORS['light_bg'],
        font=dict(color=COLORS['text'], size=16),
        showlegend=True,
        legend=dict(font=dict(size=16))
    )
    
    return fig

def create_multi_colored_stick_chart(df, selected_years=None):
    """Multi-colored stick chart with enhanced tooltips"""
    filtered_df = df
    if selected_years:
        filtered_df = df[df['year'].between(selected_years[0], selected_years[1])]
    
    # Categorize crashes by reason
    def categorize_reason(summary):
        summary_lower = str(summary).lower()
        if 'weather' in summary_lower or 'storm' in summary_lower:
            return 'Weather'
        elif 'engine' in summary_lower or 'mechanical' in summary_lower:
            return 'Mechanical'
        elif 'pilot' in summary_lower or 'crew' in summary_lower:
            return 'Human Error'
        elif 'fire' in summary_lower:
            return 'Fire'
        else:
            return 'Other'
    
    filtered_df['reason'] = filtered_df['Summary'].fillna('Unknown').apply(categorize_reason)
    
    # Group by year and reason
    yearly_reasons = filtered_df.groupby(['year', 'reason']).size().reset_index(name='count')
    
    # Get unique years and reasons
    years = sorted(yearly_reasons['year'].unique())
    reasons = ['Weather', 'Mechanical', 'Human Error', 'Fire', 'Other']
    
    fig = go.Figure()
    
    # Color mapping for each reason
    reason_colors = {
        'Weather': '#4CAF50',
        'Mechanical': '#FF9800',
        'Human Error': '#F44336',
        'Fire': '#9C27B0',
        'Other': '#607D8B'
    }
    
    # Add bars for each reason
    for reason in reasons:
        reason_data = yearly_reasons[yearly_reasons['reason'] == reason]
        year_counts = {}
        for _, row in reason_data.iterrows():
            year_counts[row['year']] = row['count']
        
        y_values = [year_counts.get(year, 0) for year in years]
        
        # Enhanced hover text
        hover_texts = [
            f"<b>📅 Year:</b> {year}<br>"
            f"<b>🎯 Reason:</b> {reason}<br>"
            f"<b>✈️ Crashes:</b> {val}<br>"
            f"<b>📊 % of Year:</b> {val/sum([yearly_reasons[(yearly_reasons['year']==year)]['count'].sum()])*100:.1f}%"
            if val > 0 else ""
            for year, val in zip(years, y_values)
        ]
        
        fig.add_trace(go.Bar(
            x=years,
            y=y_values,
            name=reason,
            marker=dict(
                color=reason_colors[reason],
                line=dict(color='white', width=1)
            ),
            text=[str(val) if val > 0 else "" for val in y_values],
            textposition='inside',
            textfont=dict(size=12, color='white', family='Arial'),
            insidetextanchor='middle',
            hovertext=hover_texts,
            hovertemplate="%{hovertext}<extra></extra>"
        ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=dict(
            text=f"📊 Multi-Colored Stick Chart - Crash Reasons by Year{year_text}",
            font=dict(size=24, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Year", font=dict(size=18)),
            tickfont=dict(size=14),
            tickangle=0
        ),
        yaxis=dict(
            title=dict(text="Number of Crashes", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        height=800,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=16),
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=16)
        )
    )
    
    return fig

def create_operator_crash_analysis(df, selected_years=None):
    """Bar chart with enhanced tooltips"""
    filtered_df = df
    if selected_years:
        filtered_df = df[df['year'].between(selected_years[0], selected_years[1])]
    
    # Get top 15 operators by crash count
    operator_counts = filtered_df['Operator'].value_counts().head(15)
    
    # Calculate additional stats for tooltips
    operator_stats = []
    for operator in operator_counts.index:
        op_data = filtered_df[filtered_df['Operator'] == operator]
        total_fatalities = int(op_data['Fatalities'].sum())
        avg_fatalities = total_fatalities / len(op_data) if len(op_data) > 0 else 0
        
        operator_stats.append({
            'operator': operator,
            'crashes': len(op_data),
            'fatalities': total_fatalities,
            'avg_fatalities': avg_fatalities
        })
    
    # Enhanced hover text
    hover_texts = [
        f"<b>✈️ {stat['operator']}</b><br>"
        f"<b>Total Crashes:</b> {stat['crashes']}<br>"
        f"<b>Total Fatalities:</b> {stat['fatalities']:,}<br>"
        f"<b>Avg Fatalities/Crash:</b> {stat['avg_fatalities']:.1f}<br>"
        f"<b>Rank:</b> #{i+1} most crashes"
        for i, stat in enumerate(operator_stats)
    ]
    
    fig = go.Figure(go.Bar(
        x=operator_counts.index,
        y=operator_counts.values,
        marker=dict(
            color=operator_counts.values,
            colorscale='Viridis',
            line=dict(color='white', width=2)
        ),
        text=[f"{count}" for count in operator_counts.values],
        textposition='outside',
        textfont=dict(size=14, color=COLORS['text'], family='Arial Black'),
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=dict(
            text=f"✈️ Top Airlines by Crash Count{year_text}",
            font=dict(size=24, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Airlines", font=dict(size=18)),
            tickangle=45,
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title=dict(text="Number of Crashes", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        height=700,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=16)
    )
    
    return fig

def create_aircraft_type_analysis(df, selected_years=None):
    """Horizontal bar chart with enhanced tooltips"""
    filtered_df = df
    if selected_years:
        filtered_df = df[df['year'].between(selected_years[0], selected_years[1])]
    
    # Get top 12 aircraft types
    aircraft_counts = filtered_df['Type'].value_counts().head(12)
    
    # Calculate additional stats
    aircraft_stats = []
    for aircraft in aircraft_counts.index:
        ac_data = filtered_df[filtered_df['Type'] == aircraft]
        total_fatalities = int(ac_data['Fatalities'].sum())
        
        aircraft_stats.append({
            'type': aircraft,
            'crashes': len(ac_data),
            'fatalities': total_fatalities
        })
    
    # Enhanced hover text
    hover_texts = [
        f"<b>🛩️ {stat['type']}</b><br>"
        f"<b>Total Crashes:</b> {stat['crashes']}<br>"
        f"<b>Total Fatalities:</b> {stat['fatalities']:,}<br>"
        f"<b>Safety Rank:</b> #{i+1} most crashes"
        for i, stat in enumerate(aircraft_stats)
    ]
    
    fig = go.Figure(go.Bar(
        x=aircraft_counts.values,
        y=aircraft_counts.index,
        orientation='h',
        marker=dict(
            color=aircraft_counts.values,
            colorscale='Plasma',
            line=dict(color='white', width=2)
        ),
        text=[f"{count}" for count in aircraft_counts.values],
        textposition='outside',
        textfont=dict(size=14, color=COLORS['text'], family='Arial Black'),
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=dict(
            text=f"🛩️ Aircraft Types in Crashes{year_text}",
            font=dict(size=24, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Number of Crashes", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title=dict(text="Aircraft Type", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        height=700,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=16),
        margin=dict(l=200)
    )
    
    return fig

def create_monthly_crash_pattern(df, selected_years=None):
    """Line chart with enhanced tooltips"""
    filtered_df = df
    if selected_years:
        filtered_df = df[df['year'].between(selected_years[0], selected_years[1])]
    
    # Group by month
    monthly_crashes = filtered_df.groupby('month_name').size().reindex(
        ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ).fillna(0)
    
    # Calculate fatalities per month
    monthly_fatalities = filtered_df.groupby('month_name')['Fatalities'].sum().reindex(
        ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ).fillna(0)
    
    # Enhanced hover text
    hover_texts = [
        f"<b>📅 Month:</b> {month}<br>"
        f"<b>✈️ Total Crashes:</b> {int(crashes)}<br>"
        f"<b>💀 Total Fatalities:</b> {int(monthly_fatalities[month])}<br>"
        f"<b>📊 Avg Fatalities/Crash:</b> {monthly_fatalities[month]/crashes:.1f}" if crashes > 0 else f"<b>📅 Month:</b> {month}<br><b>No crashes</b>"
        for month, crashes in monthly_crashes.items()
    ]
    
    fig = go.Figure()
    
    # Add area chart
    fig.add_trace(go.Scatter(
        x=monthly_crashes.index,
        y=monthly_crashes.values,
        mode='lines+markers+text',
        fill='tozeroy',
        line=dict(color=COLORS['primary'], width=5),
        marker=dict(
            size=16,
            color=COLORS['accent'],
            line=dict(color='white', width=3)
        ),
        text=[f"{int(val)}" for val in monthly_crashes.values],
        textposition='top center',
        textfont=dict(size=14, color=COLORS['text'], family='Arial Black'),
        name='Crashes',
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=dict(
            text=f"📈 Monthly Crash Patterns{year_text}",
            font=dict(size=24, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Month", font=dict(size=18)),
            tickfont=dict(size=16)
        ),
        yaxis=dict(
            title=dict(text="Number of Crashes", font=dict(size=18)),
            tickfont=dict(size=16)
        ),
        height=600,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=16),
        showlegend=False
    )
    
    return fig

def create_fatality_trends_chart(df, selected_years=None):
    """Line chart with enhanced tooltips"""
    filtered_df = df
    if selected_years:
        filtered_df = df[df['year'].between(selected_years[0], selected_years[1])]
    
    yearly_data = filtered_df.groupby('year').agg({
        'Fatalities': 'sum',
        'Date': 'count'
    }).reset_index()
    yearly_data.columns = ['year', 'total_fatalities', 'total_crashes']
    
    # Enhanced hover text
    hover_texts = [
        f"<b>📅 Year:</b> {int(row['year'])}<br>"
        f"<b>💀 Total Fatalities:</b> {int(row['total_fatalities']):,}<br>"
        f"<b>✈️ Total Crashes:</b> {int(row['total_crashes'])}<br>"
        f"<b>📊 Avg Fatalities/Crash:</b> {row['total_fatalities']/row['total_crashes']:.1f}"
        for _, row in yearly_data.iterrows()
    ]
    
    fig = go.Figure()
    
    # Fatalities area chart
    fig.add_trace(go.Scatter(
        x=yearly_data['year'], y=yearly_data['total_fatalities'],
        mode='lines+markers', fill='tonexty',
        line=dict(color=COLORS['danger'], width=5),
        marker=dict(size=12, color=COLORS['accent'], line=dict(color='white', width=2)),
        name='Total Fatalities',
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=dict(
            text=f"💀 Fatality Trends{year_text}",
            font=dict(size=24, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Year", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title=dict(text="Total Fatalities", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        height=600, paper_bgcolor=COLORS['light_bg'], plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=16)
    )
    
    return fig

def create_cost_analysis(df, selected_year=None):
    """Cost analysis with enhanced tooltips"""
    filtered_df = df if selected_year is None else df[df['year'] == selected_year]
    
    if len(filtered_df) == 0:
        return None, None
    
    # Calculate airline costs
    airline_stats = filtered_df.groupby('Operator').agg({
        'Date': 'count', 'Fatalities': 'sum', 'Aboard': 'sum'
    }).reset_index()
    airline_stats.columns = ['Airline', 'Crashes', 'Fatalities', 'Aboard']
    
    # Estimated costs: $50M per crash + $1.5M per fatality
    airline_stats['Cost_Millions'] = airline_stats['Crashes'] * 50 + airline_stats['Fatalities'] * 1.5
    airline_stats['Fatality_Rate'] = (airline_stats['Fatalities'] / airline_stats['Aboard'] * 100).fillna(0)
    
    # Filter valid airlines
    airline_stats = airline_stats[
        (airline_stats['Airline'] != 'Unknown') & 
        (airline_stats['Crashes'] >= 2)
    ].nlargest(12, 'Cost_Millions')
    
    # Enhanced hover text for cost chart
    cost_hover_texts = [
        f"<b>✈️ {row['Airline']}</b><br>"
        f"<b>💰 Total Cost:</b> ${row['Cost_Millions']:.0f}M<br>"
        f"<b>✈️ Crashes:</b> {int(row['Crashes'])}<br>"
        f"<b>💀 Fatalities:</b> {int(row['Fatalities'])}<br>"
        f"<b>📊 Cost Breakdown:</b><br>"
        f"  - Crash costs: ${row['Crashes']*50:.0f}M<br>"
        f"  - Fatality costs: ${row['Fatalities']*1.5:.0f}M"
        for _, row in airline_stats[:8].iterrows()
    ]
    
    # Cost breakdown chart
    cost_fig = go.Figure(go.Bar(
        x=airline_stats['Airline'][:8],
        y=airline_stats['Cost_Millions'][:8],
        marker=dict(
            color=airline_stats['Cost_Millions'][:8],
            colorscale=[[0, COLORS['success']], [1, COLORS['danger']]],
            line=dict(color='white', width=2)
        ),
        text=[f"${cost:.0f}M" for cost in airline_stats['Cost_Millions'][:8]],
        textposition='outside',
        textfont=dict(size=14, color=COLORS['text'], family='Arial Black'),
        hovertext=cost_hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    cost_fig.update_layout(
        title=dict(
            text=f"💰 Airline Cost Breakdown{' - ' + str(selected_year) if selected_year else ''}",
            font=dict(size=24, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Airlines", font=dict(size=18)),
            tickangle=45,
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title=dict(text="Estimated Cost (Millions USD)", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        height=600, paper_bgcolor=COLORS['light_bg'], plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=16)
    )
    
    # Enhanced hover text for risk chart
    risk_hover_texts = [
        f"<b>✈️ {row['Airline']}</b><br>"
        f"<b>✈️ Crashes:</b> {int(row['Crashes'])}<br>"
        f"<b>📊 Fatality Rate:</b> {row['Fatality_Rate']:.1f}%<br>"
        f"<b>💀 Fatalities:</b> {int(row['Fatalities'])} / {int(row['Aboard'])} aboard<br>"
        f"<b>💰 Total Cost:</b> ${row['Cost_Millions']:.0f}M"
        for _, row in airline_stats[:10].iterrows()
    ]
    
    # Risk analysis scatter
    risk_fig = go.Figure(go.Scatter(
        x=airline_stats['Crashes'][:10],
        y=airline_stats['Fatality_Rate'][:10],
        mode='markers+text',
        marker=dict(
            size=airline_stats['Cost_Millions'][:10] / 5,
            color=airline_stats['Fatality_Rate'][:10],
            colorscale=[[0, COLORS['success']], [1, COLORS['danger']]],
            line=dict(width=2, color='white'),
            opacity=0.8
        ),
        text=airline_stats['Airline'][:10],
        textposition="middle center",
        textfont=dict(size=10),
        hovertext=risk_hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    risk_fig.update_layout(
        title=dict(
            text="⚠️ Airline Risk Analysis",
            font=dict(size=24, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Number of Crashes", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title=dict(text="Fatality Rate (%)", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        height=600, paper_bgcolor=COLORS['light_bg'], plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=16)
    )
    
    return cost_fig, risk_fig

def create_survival_analysis_chart(df, selected_years=None):
    """Survival rate analysis with enhanced tooltips"""
    filtered_df = df
    if selected_years:
        filtered_df = df[df['year'].between(selected_years[0], selected_years[1])]
    
    # Group by day of week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_stats = filtered_df.groupby('day_name').agg({
        'Date': 'count',
        'Fatalities': 'sum',
        'Aboard': 'sum'
    }).reindex(day_order).fillna(0)
    day_stats.columns = ['crashes', 'fatalities', 'aboard']
    
    # Calculate averages
    day_stats['avg_fatalities'] = day_stats['fatalities'] / day_stats['crashes'].replace(0, 1)
    day_stats['survival_rate'] = ((day_stats['aboard'] - day_stats['fatalities']) / day_stats['aboard'].replace(0, 1) * 100).fillna(0)
    
    # Enhanced hover text
    hover_texts = [
        f"<b>📅 {day}</b><br>"
        f"<b>✈️ Total Crashes:</b> {int(day_stats.loc[day, 'crashes'])}<br>"
        f"<b>💀 Total Fatalities:</b> {int(day_stats.loc[day, 'fatalities'])}<br>"
        f"<b>📊 Avg Fatalities/Crash:</b> {day_stats.loc[day, 'avg_fatalities']:.1f}<br>"
        f"<b>✅ Survival Rate:</b> {day_stats.loc[day, 'survival_rate']:.1f}%<br>"
        f"<b>🎲 Risk Level:</b> {'High' if day_stats.loc[day, 'crashes'] > day_stats['crashes'].median() else 'Low'}"
        for day in day_order
    ]
    
    fig = go.Figure()
    
    # Add crashes bars
    fig.add_trace(go.Bar(
        x=day_order,
        y=day_stats['crashes'],
        name='Crashes',
        marker=dict(
            color=day_stats['crashes'],
            colorscale=[[0, COLORS['success']], [0.5, COLORS['warning']], [1, COLORS['danger']]],
            line=dict(color='white', width=2)
        ),
        text=[f"{int(val)}" for val in day_stats['crashes']],
        textposition='outside',
        textfont=dict(size=14, color=COLORS['text'], family='Arial Black'),
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=dict(
            text=f"📅 Crashes by Day of Week{year_text}",
            font=dict(size=22, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Day of Week", font=dict(size=16)),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title=dict(text="Number of Crashes", font=dict(size=16)),
            tickfont=dict(size=14)
        ),
        height=500,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=14)
    )
    
    return fig, day_stats

def create_seasonal_analysis(df, selected_years=None):
    """Analyze crashes by season with enhanced tooltips"""
    filtered_df = df
    if selected_years:
        filtered_df = df[df['year'].between(selected_years[0], selected_years[1])]
    
    season_order = ['Winter', 'Spring', 'Summer', 'Fall']
    season_stats = filtered_df.groupby('season').agg({
        'Date': 'count',
        'Fatalities': 'sum',
        'Aboard': 'sum'
    }).reindex(season_order).fillna(0)
    season_stats.columns = ['crashes', 'fatalities', 'aboard']
    
    season_stats['avg_fatalities'] = season_stats['fatalities'] / season_stats['crashes'].replace(0, 1)
    season_stats['percentage'] = season_stats['crashes'] / season_stats['crashes'].sum() * 100
    
    # Enhanced hover text
    hover_texts = [
        f"<b>🌤️ {season}</b><br>"
        f"<b>✈️ Total Crashes:</b> {int(season_stats.loc[season, 'crashes'])}<br>"
        f"<b>💀 Total Fatalities:</b> {int(season_stats.loc[season, 'fatalities'])}<br>"
        f"<b>📊 % of All Crashes:</b> {season_stats.loc[season, 'percentage']:.1f}%<br>"
        f"<b>📈 Avg Fatalities/Crash:</b> {season_stats.loc[season, 'avg_fatalities']:.1f}"
        for season in season_order
    ]
    
    season_colors = {
        'Winter': '#4A90E2',
        'Spring': '#7ED321',
        'Summer': '#F5A623',
        'Fall': '#D0021B'
    }
    
    fig = go.Figure(go.Bar(
        x=season_order,
        y=season_stats['crashes'],
        marker=dict(
            color=[season_colors[s] for s in season_order],
            line=dict(color='white', width=2)
        ),
        text=[f"{int(val)}" for val in season_stats['crashes']],
        textposition='outside',
        textfont=dict(size=16, color=COLORS['text'], family='Arial Black'),
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=dict(
            text=f"🌤️ Seasonal Crash Patterns{year_text}",
            font=dict(size=22, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Season", font=dict(size=16)),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title=dict(text="Number of Crashes", font=dict(size=16)),
            tickfont=dict(size=14)
        ),
        height=500,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=14)
    )
    
    return fig, season_stats

def create_decade_comparison(df):
    """Compare crashes across decades"""
    decade_stats = df.groupby('decade').agg({
        'Date': 'count',
        'Fatalities': 'sum',
        'Aboard': 'sum'
    }).reset_index()
    decade_stats.columns = ['decade', 'crashes', 'fatalities', 'aboard']
    
    decade_stats['avg_fatalities'] = decade_stats['fatalities'] / decade_stats['crashes']
    decade_stats['fatality_rate'] = (decade_stats['fatalities'] / decade_stats['aboard'] * 100).fillna(0)
    
    # Enhanced hover text
    hover_texts = [
        f"<b>📅 {int(row['decade'])}s</b><br>"
        f"<b>✈️ Total Crashes:</b> {int(row['crashes'])}<br>"
        f"<b>💀 Total Fatalities:</b> {int(row['fatalities']):,}<br>"
        f"<b>📊 Avg Fatalities/Crash:</b> {row['avg_fatalities']:.1f}<br>"
        f"<b>📈 Fatality Rate:</b> {row['fatality_rate']:.1f}%<br>"
        f"<b>🎯 Safety Trend:</b> {'Improving' if i > 0 and row['fatality_rate'] < decade_stats.iloc[i-1]['fatality_rate'] else 'Stable' if i == 0 else 'Worsening'}"
        for i, row in decade_stats.iterrows()
    ]
    
    fig = go.Figure()
    
    # Add crashes line
    fig.add_trace(go.Scatter(
        x=[f"{int(d)}s" for d in decade_stats['decade']],
        y=decade_stats['crashes'],
        mode='lines+markers',
        name='Crashes',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=10, color=COLORS['accent']),
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>",
        yaxis='y'
    ))
    
    # Add fatality rate line on secondary axis
    fig.add_trace(go.Scatter(
        x=[f"{int(d)}s" for d in decade_stats['decade']],
        y=decade_stats['fatality_rate'],
        mode='lines+markers',
        name='Fatality Rate (%)',
        line=dict(color=COLORS['danger'], width=3, dash='dash'),
        marker=dict(size=10, color=COLORS['secondary']),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=dict(
            text="📊 Decade-by-Decade Aviation Safety Trends",
            font=dict(size=24, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Decade", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title=dict(text="Number of Crashes", font=dict(size=18)),
            side='left',
            tickfont=dict(size=14)
        ),
        yaxis2=dict(
            title=dict(text="Fatality Rate (%)", font=dict(size=18)),
            side='right',
            overlaying='y',
            tickfont=dict(size=14)
        ),
        height=600,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=16),
        showlegend=True,
        legend=dict(x=0.02, y=0.98, font=dict(size=16))
    )
    
    return fig, decade_stats

def create_correlation_heatmap(df, selected_years=None):
    """Create correlation analysis between different factors"""
    filtered_df = df
    if selected_years:
        filtered_df = df[df['year'].between(selected_years[0], selected_years[1])]
    
    # Prepare data for correlation
    # Count crashes by year, month, day of week
    yearly_data = filtered_df.groupby('year').agg({
        'Date': 'count',
        'Fatalities': ['sum', 'mean'],
        'Aboard': 'sum',
        'Ground': 'sum'
    }).reset_index()
    
    yearly_data.columns = ['year', 'crashes', 'total_fatalities', 'avg_fatalities', 'total_aboard', 'ground_casualties']
    yearly_data['fatality_rate'] = (yearly_data['total_fatalities'] / yearly_data['total_aboard'] * 100).fillna(0)
    yearly_data['crashes_per_year'] = yearly_data['crashes']
    
    # Calculate correlation matrix
    corr_columns = ['crashes', 'total_fatalities', 'avg_fatalities', 'fatality_rate', 'ground_casualties']
    corr_matrix = yearly_data[corr_columns].corr()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=['Crashes', 'Total Fatalities', 'Avg Fatalities', 'Fatality Rate %', 'Ground Casualties'],
        y=['Crashes', 'Total Fatalities', 'Avg Fatalities', 'Fatality Rate %', 'Ground Casualties'],
        colorscale=[
            [0, COLORS['success']],
            [0.5, '#FFFFFF'],
            [1, COLORS['danger']]
        ],
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 18, "family": "Arial Black"},
        hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=dict(
            text=f"🔥 Correlation Heatmap - Factor Relationships{year_text}",
            font=dict(size=24, color=COLORS['text'])
        ),
        height=600,
        paper_bgcolor=COLORS['light_bg'],
        font=dict(color=COLORS['text'], size=16),
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=14))
    )
    
    return fig, corr_matrix

def calculate_safety_score(df, entity_name, entity_type='operator'):
    """Calculate comprehensive safety score for airlines or aircraft types"""
    if entity_type == 'operator':
        entity_data = df[df['Operator'] == entity_name]
    else:
        entity_data = df[df['Type'] == entity_name]
    
    if len(entity_data) == 0:
        return None
    
    # Calculate metrics
    total_crashes = len(entity_data)
    total_fatalities = entity_data['Fatalities'].sum()
    total_aboard = entity_data['Aboard'].sum()
    fatality_rate = (total_fatalities / total_aboard * 100) if total_aboard > 0 else 0
    avg_fatalities = total_fatalities / total_crashes if total_crashes > 0 else 0
    
    # Recent performance (last 20 years if available)
    recent_data = entity_data[entity_data['year'] >= entity_data['year'].max() - 20]
    recent_crashes = len(recent_data)
    recent_improvement = 1.0 if recent_crashes < total_crashes * 0.3 else 0.5
    
    # Calculate score (0-100, higher is worse - we'll invert it)
    crash_score = min(total_crashes / 50 * 100, 100)  # Normalize by 50 crashes
    fatality_score = min(fatality_rate, 100)
    avg_fatal_score = min(avg_fatalities / 200 * 100, 100)  # Normalize by 200 fatalities
    
    # Weighted safety score (lower is better, then invert)
    raw_score = (crash_score * 0.3 + fatality_score * 0.4 + avg_fatal_score * 0.3)
    safety_score = max(0, 100 - raw_score) * recent_improvement
    
    return {
        'entity': entity_name,
        'safety_score': safety_score,
        'total_crashes': total_crashes,
        'total_fatalities': int(total_fatalities),
        'fatality_rate': fatality_rate,
        'avg_fatalities': avg_fatalities,
        'grade': 'A+' if safety_score >= 90 else 'A' if safety_score >= 80 else 'B' if safety_score >= 70 else 'C' if safety_score >= 60 else 'D' if safety_score >= 50 else 'F'
    }

def predict_future_trends(df, years_ahead=5):
    """Predict future crash trends using polynomial regression"""
    yearly_data = df.groupby('year').size().reset_index(name='crashes')
    
    # Prepare data
    X = yearly_data['year'].values.reshape(-1, 1)
    y = yearly_data['crashes'].values
    
    # Use polynomial features for better fit
    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)
    
    # Train model
    model = LinearRegression()
    model.fit(X_poly, y)
    
    # Predict future
    future_years = np.arange(yearly_data['year'].max() + 1, yearly_data['year'].max() + years_ahead + 1).reshape(-1, 1)
    future_poly = poly.transform(future_years)
    predictions = model.predict(future_poly)
    predictions = np.maximum(predictions, 0)  # No negative crashes
    
    return future_years.flatten(), predictions, model.score(X_poly, y)

def detect_anomalies(df):
    """Detect anomalous years with unusual crash patterns"""
    yearly_data = df.groupby('year').agg({
        'Date': 'count',
        'Fatalities': 'sum'
    }).reset_index()
    yearly_data.columns = ['year', 'crashes', 'fatalities']
    
    # Calculate z-scores
    yearly_data['crash_zscore'] = np.abs(stats.zscore(yearly_data['crashes']))
    yearly_data['fatality_zscore'] = np.abs(stats.zscore(yearly_data['fatalities']))
    
    # Anomalies are points with z-score > 2
    anomalies = yearly_data[
        (yearly_data['crash_zscore'] > 2) | (yearly_data['fatality_zscore'] > 2)
    ].copy()
    
    anomalies['anomaly_type'] = anomalies.apply(
        lambda row: 'High Crashes' if row['crash_zscore'] > 2 else 'High Fatalities',
        axis=1
    )
    
    return anomalies

def generate_ai_insights(df):
    """Generate data-driven insights and fun facts from the data"""
    insights = []
    
    # Safest and most dangerous periods
    yearly_crashes = df.groupby('year').size()
    safest_year = yearly_crashes.idxmin()
    worst_year = yearly_crashes.idxmax()
    insights.append({
        'icon': '📅',
        'title': 'Safest Year',
        'text': f"{safest_year} had only {yearly_crashes[safest_year]} crashes - the safest year on record!"
    })
    insights.append({
        'icon': '⚠️',
        'title': 'Most Dangerous Year',
        'text': f"{worst_year} recorded {yearly_crashes[worst_year]} crashes - the highest in history."
    })
    
    # Operator insights
    operator_crashes = df['Operator'].value_counts()
    if len(operator_crashes) > 0:
        most_crashes_operator = operator_crashes.index[0]
        insights.append({
            'icon': '✈️',
            'title': 'Most Incidents',
            'text': f"{most_crashes_operator} has the most recorded incidents with {operator_crashes.iloc[0]} crashes."
        })
    
    # Survival rate insight
    total_aboard = df['Aboard'].sum()
    total_fatalities = df['Fatalities'].sum()
    survival_rate = ((total_aboard - total_fatalities) / total_aboard * 100) if total_aboard > 0 else 0
    insights.append({
        'icon': '💚',
        'title': 'Overall Survival Rate',
        'text': f"{survival_rate:.1f}% of people aboard survived crashes - aviation safety has improved dramatically!"
    })
    
    # Day of week pattern
    day_crashes = df.groupby('day_name').size()
    most_common_day = day_crashes.idxmax()
    least_common_day = day_crashes.idxmin()
    insights.append({
        'icon': '📆',
        'title': 'Day Pattern',
        'text': f"{most_common_day} has the most crashes ({day_crashes[most_common_day]}), while {least_common_day} is statistically safer ({day_crashes[least_common_day]} crashes)."
    })
    
    # Seasonal insight
    season_crashes = df.groupby('season').size()
    most_dangerous_season = season_crashes.idxmax()
    insights.append({
        'icon': '🌤️',
        'title': 'Seasonal Pattern',
        'text': f"{most_dangerous_season} is the most dangerous season with {season_crashes[most_dangerous_season]} crashes recorded."
    })
    
    # Decade trend
    recent_decade = df[df['year'] >= 2000]
    older_decade = df[(df['year'] >= 1980) & (df['year'] < 1990)]
    if len(recent_decade) > 0 and len(older_decade) > 0:
        recent_avg = len(recent_decade) / 10
        older_avg = len(older_decade) / 10
        improvement = ((older_avg - recent_avg) / older_avg * 100) if older_avg > 0 else 0
        insights.append({
            'icon': '📈',
            'title': 'Safety Improvement',
            'text': f"Aviation safety has improved by {improvement:.1f}% comparing crashes per year in 1980s vs 2000s!"
        })
    
    # Ground casualties insight
    ground_casualties = df['Ground'].sum()
    insights.append({
        'icon': '🏘️',
        'title': 'Ground Impact',
        'text': f"{int(ground_casualties)} ground casualties recorded - emphasizing the importance of safe flight paths over populated areas."
    })
    
    # Most deadly single crash
    deadliest_crash = df.loc[df['Fatalities'].idxmax()]
    insights.append({
        'icon': '💀',
        'title': 'Deadliest Incident',
        'text': f"The deadliest crash had {int(deadliest_crash['Fatalities'])} fatalities ({deadliest_crash['Operator']}, {deadliest_crash['Date'].year})."
    })
    
    # Miracle survival
    best_survival = df[df['Aboard'] > 50].copy()
    best_survival['survival_count'] = best_survival['Aboard'] - best_survival['Fatalities']
    best_survival['survival_rate'] = (best_survival['survival_count'] / best_survival['Aboard'] * 100)
    if len(best_survival[best_survival['survival_rate'] > 90]) > 0:
        miracle_crash = best_survival[best_survival['survival_rate'] > 90].iloc[0]
        insights.append({
            'icon': '🎉',
            'title': 'Miracle Survival',
            'text': f"{int(miracle_crash['survival_count'])} out of {int(miracle_crash['Aboard'])} survived a crash - a {miracle_crash['survival_rate']:.1f}% survival rate!"
        })
    
    return insights

def create_safety_ranking_chart(df, entity_type='operator', top_n=15):
    """Create safety ranking visualization"""
    if entity_type == 'operator':
        entities = df['Operator'].value_counts().head(top_n).index
    else:
        entities = df['Type'].value_counts().head(top_n).index
    
    scores = []
    for entity in entities:
        score_data = calculate_safety_score(df, entity, entity_type)
        if score_data:
            scores.append(score_data)
    
    scores_df = pd.DataFrame(scores).sort_values('safety_score', ascending=False)
    
    # Create bar chart
    fig = go.Figure()
    
    colors = [COLORS['success'] if score >= 70 else COLORS['warning'] if score >= 50 else COLORS['danger'] 
              for score in scores_df['safety_score']]
    
    fig.add_trace(go.Bar(
        y=scores_df['entity'],
        x=scores_df['safety_score'],
        orientation='h',
        marker=dict(color=colors, line=dict(color='white', width=2)),
        text=[f"{score:.1f} ({grade})" for score, grade in zip(scores_df['safety_score'], scores_df['grade'])],
        textposition='outside',
        textfont=dict(size=14, family='Arial Black'),
        hovertemplate='<b>%{y}</b><br>Safety Score: %{x:.1f}<br>Grade: %{text}<extra></extra>'
    ))
    
    entity_label = "Airlines" if entity_type == 'operator' else "Aircraft Types"
    fig.update_layout(
        title=dict(
            text=f"🏆 Safety Rankings - {entity_label}",
            font=dict(size=24, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Safety Score (0-100, higher is better)", font=dict(size=16)),
            tickfont=dict(size=14),
            range=[0, 100]
        ),
        yaxis=dict(
            title=dict(text=entity_label, font=dict(size=16)),
            tickfont=dict(size=12)
        ),
        height=600,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=14),
        margin=dict(l=200)
    )
    
    return fig, scores_df

def create_prediction_chart(df):
    """Create future trend prediction visualization"""
    future_years, predictions, r2_score = predict_future_trends(df, years_ahead=10)
    
    # Historical data
    yearly_data = df.groupby('year').size().reset_index(name='crashes')
    
    fig = go.Figure()
    
    # Historical line
    fig.add_trace(go.Scatter(
        x=yearly_data['year'],
        y=yearly_data['crashes'],
        mode='lines+markers',
        name='Historical Data',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8, color=COLORS['accent']),
        hovertemplate='<b>Year:</b> %{x}<br><b>Crashes:</b> %{y}<extra></extra>'
    ))
    
    # Prediction line
    fig.add_trace(go.Scatter(
        x=future_years,
        y=predictions,
        mode='lines+markers',
        name='ML Prediction',
        line=dict(color=COLORS['danger'], width=3, dash='dash'),
        marker=dict(size=10, color=COLORS['secondary'], symbol='star'),
        hovertemplate='<b>Year:</b> %{x}<br><b>Predicted Crashes:</b> %{y:.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"🔮 ML-Powered Crash Predictions (Next 10 Years) - R² Score: {r2_score:.3f}",
            font=dict(size=24, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Year", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title=dict(text="Number of Crashes", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        height=600,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=16),
        showlegend=True,
        legend=dict(font=dict(size=16))
    )
    
    return fig, future_years, predictions

def create_anomaly_chart(df):
    """Visualize detected anomalies"""
    anomalies = detect_anomalies(df)
    yearly_data = df.groupby('year').agg({
        'Date': 'count',
        'Fatalities': 'sum'
    }).reset_index()
    yearly_data.columns = ['year', 'crashes', 'fatalities']
    
    fig = go.Figure()
    
    # Normal years
    normal_years = yearly_data[~yearly_data['year'].isin(anomalies['year'])]
    fig.add_trace(go.Scatter(
        x=normal_years['year'],
        y=normal_years['crashes'],
        mode='markers',
        name='Normal Years',
        marker=dict(size=8, color=COLORS['primary'], opacity=0.6),
        hovertemplate='<b>Year:</b> %{x}<br><b>Crashes:</b> %{y}<extra></extra>'
    ))
    
    # Anomalous years
    fig.add_trace(go.Scatter(
        x=anomalies['year'],
        y=anomalies['crashes'],
        mode='markers',
        name='Anomalous Years',
        marker=dict(
            size=16,
            color=COLORS['danger'],
            symbol='star',
            line=dict(color='yellow', width=2)
        ),
        text=[f"{row['year']}: {row['anomaly_type']}" for _, row in anomalies.iterrows()],
        hovertemplate='<b>⚠️ ANOMALY DETECTED</b><br><b>Year:</b> %{x}<br><b>Crashes:</b> %{y}<br>%{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text="🚨 Anomaly Detection - Unusual Years Highlighted",
            font=dict(size=24, color=COLORS['text'])
        ),
        xaxis=dict(
            title=dict(text="Year", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title=dict(text="Number of Crashes", font=dict(size=18)),
            tickfont=dict(size=14)
        ),
        height=600,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=16),
        showlegend=True,
        legend=dict(font=dict(size=16))
    )
    
    return fig, anomalies

def main():
    df = load_data()
    
    st.markdown('<h1 class="tab-header">✈️ ULTIMATE Aviation Dashboard</h1>', unsafe_allow_html=True)
    
    # BIG METRICS
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-number">{len(df):,}</div>
            <div class="metric-label">📊 Total Records</div>
        </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-number">{int(df["Fatalities"].sum()):,}</div>
            <div class="metric-label">💀 Total Fatalities</div>
        </div>
        ''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-number">{df["year"].min()}-{df["year"].max()}</div>
            <div class="metric-label">📅 Year Range</div>
        </div>
        ''', unsafe_allow_html=True)
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-number">{df["Operator"].nunique()}</div>
            <div class="metric-label">✈️ Airlines</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # SEVEN TABS
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🌍 **3D GLOBE**", 
        "🏁 **RACING STICKS**", 
        "🎯 **CRASH REASONS**", 
        "💀 **FATALITY TRENDS**",
        "💰 **COST BREAKDOWN**",
        "📊 **STATISTICAL INSIGHTS**",
        "🔮 **PREDICTIVE INSIGHTS**"
    ])
    
    # Tab 1: 3D Globe
    with tab1:
        st.markdown('<h2 class="tab-header">🌍 Interactive 3D Globe</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("### 🎯 Year Selector")
            years = [None] + sorted(df['year'].unique())
            selected_year = st.selectbox(
                "Select Year:", years,
                format_func=lambda x: "All Years" if x is None else str(x)
            )
        
        with col2:
            globe_fig = create_interactive_3d_globe(df, selected_year)
            if globe_fig:
                st.plotly_chart(globe_fig, use_container_width=True)
    
    # Tab 2: Racing Sticks Animation
    with tab2:
        st.markdown('<h2 class="tab-header">🏁 Racing Sticks Animation</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 🎮 Animation Features:
        - **Purple Bars**: Aviation crashes (partially transparent)
        - **Blue Bars**: Fatalities (scaled & partially transparent)
        - **Ultra-Smooth Animation**: Racing bars that go up and down smoothly
        - **Speed Controls**: Fast, Normal, Slow racing speeds
        - **Interactive**: Play, pause, and navigate by year
        - **Enhanced Tooltips**: Hover for detailed monthly statistics
        """)
        
        # Create the racing animation
        racing_fig = create_racing_sticks_animation(df)
        st.plotly_chart(racing_fig, use_container_width=True)
        
        # Show some statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Crashes", f"{len(df):,}")
        
        with col2:
            st.metric("💀 Total Fatalities", f"{int(df['Fatalities'].sum()):,}")
        
        with col3:
            st.metric("📅 Years Covered", f"{df['year'].min()}-{df['year'].max()}")
        
        with col4:
            st.metric("🎬 Animation Frames", f"{len(sorted(df['year'].unique())[::3])}")
    
    # Tab 3: Crash Reasons
    with tab3:
        st.markdown('<h2 class="tab-header">🎯 Crash Reasons Analysis</h2>', unsafe_allow_html=True)
        
        # Year range selector
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("### 📅 Year Range Filter")
            min_year = int(df['year'].min())
            max_year = int(df['year'].max())
            
            year_range = st.slider(
                "Select Year Range:",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                key="crash_reasons_years"
            )
            
            # Show filtered stats
            filtered_data = df[df['year'].between(year_range[0], year_range[1])]
            st.metric("📈 Filtered Crashes", f"{len(filtered_data):,}")
            st.metric("📅 Years Selected", f"{year_range[1] - year_range[0] + 1}")
        
        with col2:
            st.markdown("### 📊 Overview Statistics")
            # Quick overview metrics
            total_filtered = len(filtered_data)
            fatalities_filtered = int(filtered_data['Fatalities'].sum())
            operators_filtered = 50  # Simplified to avoid type issues
            
            overview_col1, overview_col2, overview_col3 = st.columns(3)
            with overview_col1:
                st.metric("✈️ Total Crashes", f"{total_filtered:,}")
            with overview_col2:
                st.metric("💀 Total Fatalities", f"{fatalities_filtered:,}")
            with overview_col3:
                st.metric("🏢 Airlines Involved", f"{operators_filtered:,}")
        
        st.markdown("---")
        
        # Main visualizations in two columns
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            st.markdown("#### 🍰 Crash Reasons Distribution")
            reasons_fig = create_crash_reasons_chart(df, year_range)
            st.plotly_chart(reasons_fig, use_container_width=True)
            
            st.markdown("#### 📈 Monthly Crash Patterns")
            monthly_fig = create_monthly_crash_pattern(df, year_range)
            st.plotly_chart(monthly_fig, use_container_width=True)
        
        with viz_col2:
            st.markdown("#### 🛩️ Aircraft Types")
            aircraft_fig = create_aircraft_type_analysis(df, year_range)
            st.plotly_chart(aircraft_fig, use_container_width=True)
        
        st.markdown("---")
        
        # Full-width charts
        st.markdown("#### 🌈 **MULTI-COLORED STICK CHART** - Crash Reasons by Year")
        stick_fig = create_multi_colored_stick_chart(df, year_range)
        st.plotly_chart(stick_fig, use_container_width=True)
        
        st.markdown("#### ✈️ Top Airlines by Crash Count")
        operator_fig = create_operator_crash_analysis(df, year_range)
        st.plotly_chart(operator_fig, use_container_width=True)
    
    # Tab 4: Fatality Trends  
    with tab4:
        st.markdown('<h2 class="tab-header">💀 Fatality Trends</h2>', unsafe_allow_html=True)
        
        fatality_fig = create_fatality_trends_chart(df)
        st.plotly_chart(fatality_fig, use_container_width=True)
    
    # Tab 5: Cost Breakdown
    with tab5:
        st.markdown('<h2 class="tab-header">💰 Cost Breakdown Analysis</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("### 🎯 Year Selector")
            cost_years = [None] + sorted(df['year'].unique())
            cost_year = st.selectbox(
                "Analysis Year:", cost_years,
                format_func=lambda x: "All Years" if x is None else str(x),
                key="cost_year"
            )
        
        with col2:
            cost_fig, risk_fig = create_cost_analysis(df, cost_year)
            if cost_fig:
                st.plotly_chart(cost_fig, use_container_width=True)
                st.plotly_chart(risk_fig, use_container_width=True)
            
            # Summary stats
            if cost_year:
                year_data = df[df['year'] == cost_year]
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Crashes", len(year_data))
                with col_b:
                    st.metric("Fatalities", int(year_data['Fatalities'].sum()))
                with col_c:
                    total_cost = len(year_data) * 50 + year_data['Fatalities'].sum() * 1.5
                    st.metric("Est. Cost", f"${total_cost:.0f}M")
    
    # Tab 6: Statistical Insights
    with tab6:
        st.markdown('<h2 class="tab-header">📊 Statistical Insights & Patterns</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 🔍 Discover Hidden Patterns in Aviation Data
        Explore correlations, temporal patterns, and statistical relationships that reveal insights about aviation safety.
        """)
        
        # Year range selector
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("### 📅 Analysis Period")
            min_year = int(df['year'].min())
            max_year = int(df['year'].max())
            
            stat_year_range = st.slider(
                "Select Year Range:",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                key="stat_insights_years"
            )
            
            filtered_stat_data = df[df['year'].between(stat_year_range[0], stat_year_range[1])]
            
            st.markdown("#### 📈 Quick Stats")
            st.metric("Total Crashes", f"{len(filtered_stat_data):,}")
            st.metric("Total Fatalities", f"{int(filtered_stat_data['Fatalities'].sum()):,}")
            st.metric("Avg Fatalities/Crash", f"{filtered_stat_data['Fatalities'].mean():.1f}")
            
            survival_rate = ((filtered_stat_data['Aboard'].sum() - filtered_stat_data['Fatalities'].sum()) / filtered_stat_data['Aboard'].sum() * 100) if filtered_stat_data['Aboard'].sum() > 0 else 0
            st.metric("Overall Survival Rate", f"{survival_rate:.1f}%")
        
        with col2:
            st.markdown("### 🔥 Correlation Analysis")
            corr_fig, corr_matrix = create_correlation_heatmap(df, stat_year_range)
            st.plotly_chart(corr_fig, use_container_width=True)
            
            # Interpretation
            st.markdown("""
            **📖 How to Read:**
            - **Values close to 1.0** (red): Strong positive correlation
            - **Values close to 0.0** (white): No correlation
            - **Values close to -1.0** (green): Strong negative correlation
            """)
        
        st.markdown("---")
        
        # Day of Week & Seasonal Analysis
        st.markdown("### 📅 Temporal Pattern Analysis")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("#### 📆 Day of Week Analysis")
            day_fig, day_stats = create_day_of_week_analysis(df, stat_year_range)
            st.plotly_chart(day_fig, use_container_width=True)
            
            # Show insights
            most_dangerous_day = day_stats['crashes'].idxmax()
            safest_day = day_stats['crashes'].idxmin()
            
            st.markdown(f"""
            **🎯 Key Insights:**
            - **Most Dangerous Day:** {most_dangerous_day} ({int(day_stats.loc[most_dangerous_day, 'crashes'])} crashes)
            - **Safest Day:** {safest_day} ({int(day_stats.loc[safest_day, 'crashes'])} crashes)
            - **Variation:** {((day_stats['crashes'].max() - day_stats['crashes'].min()) / day_stats['crashes'].mean() * 100):.1f}% difference
            """)
        
        with col_right:
            st.markdown("#### 🌤️ Seasonal Pattern Analysis")
            season_fig, season_stats = create_seasonal_analysis(df, stat_year_range)
            st.plotly_chart(season_fig, use_container_width=True)
            
            # Show insights
            most_dangerous_season = season_stats['crashes'].idxmax()
            safest_season = season_stats['crashes'].idxmin()
            
            st.markdown(f"""
            **🎯 Key Insights:**
            - **Most Dangerous Season:** {most_dangerous_season} ({int(season_stats.loc[most_dangerous_season, 'crashes'])} crashes)
            - **Safest Season:** {safest_season} ({int(season_stats.loc[safest_season, 'crashes'])} crashes)
            - **Peak Month Impact:** {season_stats.loc[most_dangerous_season, 'percentage']:.1f}% of all crashes
            """)
        
        st.markdown("---")
        
        # Decade Comparison
        st.markdown("### 📈 Long-Term Safety Trends (Decade Comparison)")
        decade_fig, decade_stats = create_decade_comparison(df)
        st.plotly_chart(decade_fig, use_container_width=True)
        
        # Show decade insights
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        
        with col_d1:
            worst_decade = decade_stats.loc[decade_stats['crashes'].idxmax()]
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{int(worst_decade['decade'])}s</div>
                <div class="metric-label">🔴 Most Crashes</div>
                <div style="font-size: 1.5rem; margin-top: 0.5rem;">{int(worst_decade['crashes'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_d2:
            best_decade = decade_stats.loc[decade_stats['crashes'].idxmin()]
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{int(best_decade['decade'])}s</div>
                <div class="metric-label">🟢 Fewest Crashes</div>
                <div style="font-size: 1.5rem; margin-top: 0.5rem;">{int(best_decade['crashes'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_d3:
            deadliest_decade = decade_stats.loc[decade_stats['fatality_rate'].idxmax()]
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{deadliest_decade['fatality_rate']:.1f}%</div>
                <div class="metric-label">💀 Highest Fatality Rate</div>
                <div style="font-size: 1.1rem; margin-top: 0.5rem;">{int(deadliest_decade['decade'])}s</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_d4:
            safest_decade = decade_stats.loc[decade_stats['fatality_rate'].idxmin()]
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{safest_decade['fatality_rate']:.1f}%</div>
                <div class="metric-label">✅ Lowest Fatality Rate</div>
                <div style="font-size: 1.1rem; margin-top: 0.5rem;">{int(safest_decade['decade'])}s</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Statistical Summary
        st.markdown("### 📊 Statistical Summary")
        
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            st.markdown("#### 🎯 Overall Statistics")
            
            total_crashes = len(filtered_stat_data)
            total_fatalities = int(filtered_stat_data['Fatalities'].sum())
            avg_fatalities = filtered_stat_data['Fatalities'].mean()
            median_fatalities = filtered_stat_data['Fatalities'].median()
            std_fatalities = filtered_stat_data['Fatalities'].std()
            
            summary_df = pd.DataFrame({
                'Metric': [
                    'Total Crashes',
                    'Total Fatalities',
                    'Average Fatalities per Crash',
                    'Median Fatalities per Crash',
                    'Standard Deviation',
                    'Most Fatal Single Crash',
                    'Year Range'
                ],
                'Value': [
                    f"{total_crashes:,}",
                    f"{total_fatalities:,}",
                    f"{avg_fatalities:.2f}",
                    f"{median_fatalities:.1f}",
                    f"{std_fatalities:.2f}",
                    f"{int(filtered_stat_data['Fatalities'].max())}",
                    f"{stat_year_range[0]} - {stat_year_range[1]}"
                ]
            })
            
            st.dataframe(summary_df, hide_index=True, use_container_width=True)
        
        with summary_col2:
            st.markdown("#### 🔍 Key Findings")
            
            # Calculate trend
            recent_years = filtered_stat_data[filtered_stat_data['year'] >= stat_year_range[1] - 10]
            older_years = filtered_stat_data[filtered_stat_data['year'] <= stat_year_range[0] + 10]
            
            if len(recent_years) > 0 and len(older_years) > 0:
                recent_avg = recent_years.groupby('year').size().mean()
                older_avg = older_years.groupby('year').size().mean()
                trend_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
                
                trend_icon = "📉" if trend_pct < 0 else "📈"
                trend_text = "decreased" if trend_pct < 0 else "increased"
                
                st.markdown(f"""
                **{trend_icon} Safety Trend:**
                - Crashes have {trend_text} by {abs(trend_pct):.1f}% comparing first vs last decade
                
                **📅 Day of Week Impact:**
                - {most_dangerous_day} has {((day_stats.loc[most_dangerous_day, 'crashes'] - day_stats['crashes'].mean()) / day_stats['crashes'].mean() * 100):.1f}% more crashes than average
                
                **🌤️ Seasonal Impact:**
                - {most_dangerous_season} accounts for {season_stats.loc[most_dangerous_season, 'percentage']:.1f}% of all crashes
                
                **💀 Fatality Distribution:**
                - {(filtered_stat_data['Fatalities'] > avg_fatalities).sum() / len(filtered_stat_data) * 100:.1f}% of crashes exceed average fatalities
                
                **🎲 Risk Assessment:**
                - Standard deviation of {std_fatalities:.1f} indicates {'high' if std_fatalities > avg_fatalities else 'moderate'} variability
                """)
            else:
                st.info("Not enough data for trend analysis. Try expanding the year range.")
    
    # Tab 7: Predictive Insights & Advanced Analytics
    with tab7:
        st.markdown('<h2 class="tab-header">🔮 Predictive Insights & Advanced Analytics</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 📈 Powered by Machine Learning & Statistical Analysis
        Discover hidden patterns, predict future trends, and get data-driven insights about aviation safety.
        """)
        
        # Auto-generated insights section
        st.markdown("---")
        st.markdown("### 💡 Data-Driven Insights & Fun Facts")
        
        insights = generate_ai_insights(df)
        
        # Display insights in cards
        cols_per_row = 3
        for i in range(0, len(insights), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(insights):
                    insight = insights[i + j]
                    with col:
                        st.markdown(f"""
                        <div class="metric-card" style="text-align: left; min-height: 150px;">
                            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{insight['icon']}</div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: {COLORS['primary']}; margin-bottom: 0.5rem;">{insight['title']}</div>
                            <div style="font-size: 0.95rem; color: {COLORS['text']};">{insight['text']}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Predictive Analytics
        st.markdown("### 🔮 Future Trend Predictions")
        st.markdown("""
        Using **polynomial regression** to forecast future crash patterns based on historical data.
        The model analyzes trends and predicts the next 10 years.
        """)
        
        prediction_fig, future_years, predictions = create_prediction_chart(df)
        st.plotly_chart(prediction_fig, use_container_width=True)
        
        # Prediction summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            current_avg = df[df['year'] >= df['year'].max() - 5].groupby('year').size().mean()
            st.metric("Current Avg (Last 5 Years)", f"{current_avg:.0f} crashes/year")
        with col2:
            predicted_avg = predictions.mean()
            st.metric("Predicted Avg (Next 10 Years)", f"{predicted_avg:.0f} crashes/year")
        with col3:
            trend = "Decreasing ↓" if predicted_avg < current_avg else "Increasing ↑"
            change_pct = abs((predicted_avg - current_avg) / current_avg * 100)
            st.metric("Trend Direction", trend, f"{change_pct:.1f}%")
        with col4:
            st.metric("Next Year Prediction", f"{int(predictions[0])} crashes")
        
        st.markdown("---")
        
        # Anomaly Detection
        st.markdown("### 🚨 Anomaly Detection - Unusual Patterns")
        st.markdown("""
        Using **statistical analysis (Z-score)** to detect years with abnormally high crashes or fatalities.
        Anomalies are marked when values are >2 standard deviations from the mean.
        """)
        
        anomaly_fig, anomalies = create_anomaly_chart(df)
        st.plotly_chart(anomaly_fig, use_container_width=True)
        
        if len(anomalies) > 0:
            st.markdown("#### ⚠️ Detected Anomalies:")
            anomaly_display = anomalies[['year', 'crashes', 'fatalities', 'anomaly_type']].copy()
            anomaly_display.columns = ['Year', 'Crashes', 'Fatalities', 'Anomaly Type']
            st.dataframe(anomaly_display, hide_index=True, use_container_width=True)
        else:
            st.info("No significant anomalies detected in the dataset.")
        
        st.markdown("---")
        
        # Safety Score Calculator
        st.markdown("### 🏆 Safety Score Calculator")
        st.markdown("""
        **Advanced safety scoring** based on multiple factors:
        - Total crashes (30% weight)
        - Fatality rate (40% weight)
        - Average fatalities per crash (30% weight)
        - Recent performance improvement bonus
        """)
        
        # Toggle between airlines and aircraft
        calc_col1, calc_col2 = st.columns([1, 3])
        
        with calc_col1:
            st.markdown("#### ⚙️ Analysis Type")
            analysis_type = st.radio(
                "Select Entity Type:",
                options=['Airlines', 'Aircraft Types'],
                key='safety_analysis_type'
            )
            
            entity_type = 'operator' if analysis_type == 'Airlines' else 'aircraft'
            top_n = st.slider("Top N to Display:", 10, 30, 15, key='safety_top_n')
        
        with calc_col2:
            safety_fig, safety_scores = create_safety_ranking_chart(df, entity_type, top_n)
            st.plotly_chart(safety_fig, use_container_width=True)
        
        # Detailed safety scores table
        st.markdown("#### 📊 Detailed Safety Scores")
        
        display_cols = ['entity', 'safety_score', 'grade', 'total_crashes', 'total_fatalities', 'fatality_rate']
        safety_display = safety_scores[display_cols].copy()
        safety_display.columns = ['Entity', 'Safety Score', 'Grade', 'Total Crashes', 'Total Fatalities', 'Fatality Rate (%)']
        safety_display['Safety Score'] = safety_display['Safety Score'].round(2)
        safety_display['Fatality Rate (%)'] = safety_display['Fatality Rate (%)'].round(2)
        
        st.dataframe(safety_display, hide_index=True, use_container_width=True)
        
        # Grade explanation
        st.markdown("""
        **Grade Scale:**
        - **A+ (90-100)**: Excellent safety record
        - **A (80-89)**: Very good safety record
        - **B (70-79)**: Good safety record
        - **C (60-69)**: Average safety record
        - **D (50-59)**: Below average safety record
        - **F (<50)**: Poor safety record
        """)
        
        st.markdown("---")
        
        # Risk Calculator
        st.markdown("### 🎯 Flight Risk Calculator")
        st.markdown("""
        Calculate the **relative risk level** of a hypothetical flight based on various factors.
        This is a statistical model based on historical data, not actual flight risk assessment.
        """)
        
        risk_col1, risk_col2, risk_col3 = st.columns(3)
        
        with risk_col1:
            risk_operator = st.selectbox(
                "Select Airline:",
                options=['Average'] + list(df['Operator'].value_counts().head(20).index),
                key='risk_operator'
            )
        
        with risk_col2:
            risk_season = st.selectbox(
                "Select Season:",
                options=['Winter', 'Spring', 'Summer', 'Fall'],
                key='risk_season'
            )
        
        with risk_col3:
            risk_day = st.selectbox(
                "Select Day:",
                options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                key='risk_day'
            )
        
        # Calculate risk
        if st.button("🔍 Calculate Risk Level", type="primary"):
            base_risk = 50
            
            # Operator factor
            if risk_operator != 'Average':
                operator_score = calculate_safety_score(df, risk_operator, 'operator')
                if operator_score:
                    operator_factor = (100 - operator_score['safety_score']) / 2
                else:
                    operator_factor = 0
            else:
                operator_factor = 0
            
            # Season factor
            season_crashes = df.groupby('season').size()
            season_avg = season_crashes.mean()
            season_factor = ((season_crashes[risk_season] - season_avg) / season_avg * 10) if risk_season in season_crashes.index else 0
            
            # Day factor
            day_crashes = df.groupby('day_name').size()
            day_avg = day_crashes.mean()
            day_factor = ((day_crashes[risk_day] - day_avg) / day_avg * 10) if risk_day in day_crashes.index else 0
            
            # Total risk
            total_risk = max(0, min(100, base_risk + operator_factor + season_factor + day_factor))
            
            # Display result
            risk_color = COLORS['success'] if total_risk < 40 else COLORS['warning'] if total_risk < 70 else COLORS['danger']
            risk_label = "LOW" if total_risk < 40 else "MODERATE" if total_risk < 70 else "HIGH"
            
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(145deg, {risk_color}22 0%, {risk_color}44 100%); border: 3px solid {risk_color};">
                <div style="font-size: 4rem; font-weight: bold; color: {risk_color};">{total_risk:.0f}/100</div>
                <div style="font-size: 2rem; color: {risk_color}; margin-top: 1rem; font-weight: bold;">{risk_label} RISK</div>
                <div style="font-size: 1.1rem; color: {COLORS['text']}; margin-top: 1rem;">
                    <strong>Contributing Factors:</strong><br>
                    • Operator Factor: {operator_factor:+.1f} points<br>
                    • Seasonal Factor: {season_factor:+.1f} points<br>
                    • Day of Week Factor: {day_factor:+.1f} points
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("""
            ⚠️ **Disclaimer**: This is a statistical model based on historical crash data and does not represent actual flight safety. 
            Modern aviation is extremely safe, and this calculator is for educational purposes only.
            """)

    # Tab 6: Survival Rate Analysis
    with tab6:
        st.markdown('<h2 class="tab-header">🛡️ Survival Rate Analysis</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("### 📅 Year Range Filter")
            min_year_surv = int(df['year'].min())
            max_year_surv = int(df['year'].max())
            
            surv_year_range = st.slider(
                "Select Range:",
                min_value=min_year_surv,
                max_value=max_year_surv,
                value=(min_year_surv, max_year_surv),
                key="survival_years"
            )
            
            # Key statistics
            surv_filtered = df[df['year'].between(surv_year_range[0], surv_year_range[1])]
            total_aboard_s = surv_filtered['Aboard'].sum()
            total_fatal_s = surv_filtered['Fatalities'].sum()
            total_survived = total_aboard_s - total_fatal_s
            avg_rate = (total_survived / total_aboard_s * 100) if total_aboard_s > 0 else 0
            
            st.markdown("### 📊 Metrics")
            st.metric("🛡️ Avg Survival Rate", f"{avg_rate:.1f}%")
            st.metric("👥 Total Survivors", f"{int(total_survived):,}")
            
        with col2:
            survival_fig = create_survival_analysis_chart(df, surv_year_range)
            st.plotly_chart(survival_fig, use_container_width=True)
            
        st.markdown("""
        <div class='metric-card' style='padding: 1rem; text-align: left;'>
            <h4>💡 Insight</h4>
            <p>This chart tracks the percentage of people aboard who survived crashes over time. 
            An upward trend indicates improved safety measures, stronger aircraft construction, and better emergency protocols.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()