import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
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
        df = pd.read_csv('data\dataset.csv.csv', encoding="utf-8")
    except:
        df = pd.read_csv('data\dataset.csv.csv', encoding="latin1")
    
    df.columns = [c.strip() for c in df.columns]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['year'] = df['Date'].dt.year
    df['month'] = df['Date'].dt.month
    df['month_name'] = df['Date'].dt.strftime('%b')
    
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
        title=f"🌍 3D Globe - {len(filtered_df):,} Crashes" + (f" ({selected_year})" if selected_year else ""),
        height=650, paper_bgcolor='white', font=dict(color=COLORS['text'], size=14)
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
                    textfont=dict(size=12, color='purple'),
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
                    textfont=dict(size=12, color='steelblue'),
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
            'font': {'size': 28, 'color': COLORS['text']},
            'x': 0.5
        },
        xaxis={'title': "Months (Racing Arena)"},
        yaxis={
            'title': "Racing Values",
            'range': [0, max(max_crashes, max_fatalities * scale_factor) * 1.2]
        },
        height=800,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font={'color': COLORS['text'], 'size': 14},
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
        marker=dict(colors=colors[:len(reason_counts)]),
        textinfo='label+percent',
        textfont=dict(size=16, color='black'),
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=f"🎯 Crash Reasons{year_text}",
        height=600,
        paper_bgcolor=COLORS['light_bg'],
        font=dict(color=COLORS['text'], size=16)
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
            textposition='outside',
            textfont=dict(size=10, color=COLORS['text']),
            hovertext=hover_texts,
            hovertemplate="%{hovertext}<extra></extra>"
        ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=f"📊 Multi-Colored Stick Chart - Crash Reasons by Year{year_text}",
        xaxis_title="Year",
        yaxis_title="Number of Crashes",
        height=800,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=14),
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
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
        textfont=dict(size=12, color=COLORS['text']),
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=f"✈️ Top Airlines by Crash Count{year_text}",
        xaxis_title="Airlines",
        yaxis_title="Number of Crashes",
        height=700,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=14),
        xaxis=dict(tickangle=45)
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
        textfont=dict(size=12, color=COLORS['text']),
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=f"🛩️ Aircraft Types in Crashes{year_text}",
        xaxis_title="Number of Crashes",
        yaxis_title="Aircraft Type",
        height=700,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=14)
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
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color=COLORS['primary'], width=4),
        marker=dict(
            size=12,
            color=COLORS['accent'],
            line=dict(color='white', width=2)
        ),
        name='Crashes',
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=f"📈 Monthly Crash Patterns{year_text}",
        xaxis_title="Month",
        yaxis_title="Number of Crashes",
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
        line=dict(color=COLORS['danger'], width=4),
        marker=dict(size=10, color=COLORS['accent']),
        name='Total Fatalities',
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=f"💀 Fatality Trends{year_text}",
        xaxis_title="Year", yaxis_title="Total Fatalities",
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
        textfont=dict(size=12, color=COLORS['text']),
        hovertext=cost_hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    cost_fig.update_layout(
        title=f"💰 Airline Cost Breakdown{' - ' + str(selected_year) if selected_year else ''}",
        xaxis_title="Airlines", yaxis_title="Estimated Cost (Millions USD)",
        height=600, paper_bgcolor=COLORS['light_bg'], plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=14),
        xaxis=dict(tickangle=45)
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
        title="⚠️ Airline Risk Analysis",
        xaxis_title="Number of Crashes", yaxis_title="Fatality Rate (%)",
        height=600, paper_bgcolor=COLORS['light_bg'], plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=14)
    )
    
    return cost_fig, risk_fig

def create_survival_analysis_chart(df, selected_years=None):
    """Survival rate analysis with enhanced tooltips"""
    filtered_df = df
    if selected_years:
        filtered_df = df[df['year'].between(selected_years[0], selected_years[1])]
    
    yearly_stats = filtered_df.groupby('year').agg({
        'Aboard': 'sum',
        'Fatalities': 'sum',
        'Date': 'count'
    }).reset_index()
    
    yearly_stats['Survivors'] = yearly_stats['Aboard'] - yearly_stats['Fatalities']
    yearly_stats['Survival_Rate'] = (yearly_stats['Survivors'] / yearly_stats['Aboard'] * 100).fillna(0)
    
    # Enhanced hover text
    hover_texts = [
        f"<b>📅 Year:</b> {int(row['year'])}<br>"
        f"<b>🛡️ Survival Rate:</b> {row['Survival_Rate']:.1f}%<br>"
        f"<b>👥 Total Aboard:</b> {int(row['Aboard']):,}<br>"
        f"<b>🙏 Survivors:</b> {int(row['Survivors']):,}<br>"
        f"<b>💀 Fatalities:</b> {int(row['Fatalities']):,}"
        for _, row in yearly_stats.iterrows()
    ]
    
    fig = go.Figure()
    
    # Survival Rate Line
    fig.add_trace(go.Scatter(
        x=yearly_stats['year'], 
        y=yearly_stats['Survival_Rate'],
        mode='lines+markers',
        name='Survival Rate (%)',
        line=dict(color=COLORS['success'], width=4),
        marker=dict(size=8, color='white', line=dict(width=2, color=COLORS['success'])),
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>"
    ))
    
    year_text = f" ({selected_years[0]}-{selected_years[1]})" if selected_years else " (All Years)"
    fig.update_layout(
        title=f"🛡️ Annual Survival Rate Trends{year_text}",
        xaxis_title="Year",
        yaxis_title="Survival Rate (%)",
        yaxis=dict(range=[0, 105]), # 0 to 100%
        height=600,
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], size=14),
        showlegend=True
    )
    
    return fig

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
    
    # SIX TABS
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🌍 **3D GLOBE**", 
        "🏁 **RACING STICKS**", 
        "🎯 **CRASH REASONS**", 
        "💀 **FATALITY TRENDS**",
        "💰 **COST BREAKDOWN**",
        "🛡️ **SURVIVORS**"
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