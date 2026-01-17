
risk_color = "#FF0000"
total_risk = 50.0
COLORS = {"text": "#000000"}
operator_factor = 1.0
season_factor = 1.0
day_factor = 1.0
risk_label = "HIGH"

text = f"""
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
            """
print("Success")
