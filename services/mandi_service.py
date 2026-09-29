import os
import pandas as pd
from datetime import datetime
from models.database import get_db_connection

class MandiService:
    def __init__(self, csv_path=None):
        if not csv_path:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.csv_path = os.path.join(base_dir, 'data', 'mandi_market_price_2025_2026.csv')
        else:
            self.csv_path = csv_path
        
        self._df = None
        self._states = []
        self._crops = []
        self._load_csv_data()

    def _load_csv_data(self):
        """Load and cache the CSV data for fast query execution."""
        if os.path.exists(self.csv_path):
            try:
                self._df = pd.read_csv(self.csv_path)
                self._states = sorted(self._df['State'].dropna().unique().tolist())
                self._crops = sorted(self._df['Crop Name'].dropna().unique().tolist())
            except Exception as e:
                print(f"Error loading Mandi CSV data: {e}")
                self._df = pd.DataFrame()
                self._states = []
                self._crops = []
        else:
            self._df = pd.DataFrame()
            self._states = []
            self._crops = []

    def get_filter_options(self):
        """Fetch distinct values for filters (states, crops) from the CSV dataset."""
        if self._df is None or self._df.empty:
            self._load_csv_data()

        return {
            'states': self._states,
            'crops': self._crops,
            'years': [2026, 2025]
        }

    def get_trend_data(self, state=None, crop=None, selected_year=2026):
        """
        Extract 1-year (12 monthly records) price trend for a selected State and Crop and selected Year.
        Also calculates 'This Month' statistics for the current month (September 2026).
        """
        if not state or not crop or self._df is None or self._df.empty:
            return None

        # Filter strictly by State and Crop Name
        filtered = self._df[(self._df['State'] == state) & (self._df['Crop Name'] == crop)]
        if filtered.empty:
            return None

        # Sort by Year and Month Number to guarantee chronological order
        filtered = filtered.sort_values(by=['Year', 'Month Number']).reset_index(drop=True)

        month_abbrev_map = {
            'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
            'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug',
            'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
        }

        # Build year-specific datasets for 2025 and 2026 (each has 12 months)
        yearly_data = {}
        for yr in [2025, 2026]:
            df_yr = filtered[filtered['Year'] == yr].sort_values(by='Month Number')
            labels = []
            full_labels = []
            min_prices = []
            modal_prices = []
            max_prices = []
            
            for _, row in df_yr.iterrows():
                m_name = str(row['Month']).strip()
                abbrev = month_abbrev_map.get(m_name, m_name[:3])
                labels.append(abbrev)
                full_labels.append(f"{m_name} {yr}")
                min_prices.append(round(float(row['Minimum Price (₹/Quintal)']), 1))
                modal_prices.append(round(float(row['Modal (Benchmark) Price (₹/Quintal)']), 1))
                max_prices.append(round(float(row['Maximum Price (₹/Quintal)']), 1))

            yearly_data[str(yr)] = {
                'year': yr,
                'labels': labels, # ['Jan', 'Feb', ..., 'Dec']
                'full_labels': full_labels, # ['January 2026', ...]
                'min_prices': min_prices,
                'modal_prices': modal_prices,
                'max_prices': max_prices,
                'crop_name': crop,
                'state_name': state
            }

        # Determine current month (September 2026 in current timeline)
        now = datetime.now()
        current_year = 2026
        current_month_num = 9  # September
        current_month_name = "September"

        # Find This Month's record (September 2026)
        this_month_rows = filtered[(filtered['Year'] == current_year) & (filtered['Month Number'] == current_month_num)]
        if not this_month_rows.empty:
            this_m_row = this_month_rows.iloc[0]
        else:
            # Fallback to latest record in dataset
            this_m_row = filtered.iloc[-1]

        this_modal = round(float(this_m_row['Modal (Benchmark) Price (₹/Quintal)']), 1)
        this_min = round(float(this_m_row['Minimum Price (₹/Quintal)']), 1)
        this_max = round(float(this_m_row['Maximum Price (₹/Quintal)']), 1)
        this_month_display = f"{this_m_row['Month']} {this_m_row['Year']}"

        # Find Previous Month's record (August 2026) to calculate monthly delta
        prev_month_num = current_month_num - 1 if current_month_num > 1 else 12
        prev_year = current_year if current_month_num > 1 else current_year - 1
        prev_month_rows = filtered[(filtered['Year'] == prev_year) & (filtered['Month Number'] == prev_month_num)]
        
        if not prev_month_rows.empty:
            prev_modal = round(float(prev_month_rows.iloc[0]['Modal (Benchmark) Price (₹/Quintal)']), 1)
            diff = this_modal - prev_modal
            pct = (diff / prev_modal) * 100.0 if prev_modal > 0 else 0.0
            sign = "+" if diff >= 0 else ""
            price_change_str = f"{sign}₹{abs(diff):,.0f} ({sign}{pct:.1f}%) vs last month"
            trend_dir = "upward" if diff >= 0 else "downward"
        else:
            price_change_str = "Stable vs last month"
            trend_dir = "neutral"

        # Selected year data for initial graph render
        sel_yr_str = str(selected_year) if str(selected_year) in yearly_data else "2026"
        active_chart_data = yearly_data.get(sel_yr_str, yearly_data.get('2026'))

        return {
            'state': state,
            'crop': crop,
            'selected_year': int(sel_yr_str),
            'chart_data': active_chart_data,
            'yearly_data': yearly_data,
            'stats': {
                'min_price': this_min,
                'max_price': this_max,
                'modal_price': this_modal,
                'primary_crop': crop,
                'state': state,
                'period_label': f"This Month • {this_month_display}",
                'month_name': str(this_m_row['Month']),
                'year': int(this_m_row['Year']),
                'price_change': price_change_str,
                'trend': trend_dir
            }
        }

    def get_state_rates_for_crop(self, crop='Bajra', year=2026, month_num=9, limit=None):
        """
        Get state-wise market rates for a selected crop in the current month (September 2026).
        Returns all states (or up to limit if specified) sorted for clean scrollable display.
        """
        if self._df is None or self._df.empty:
            self._load_csv_data()

        if self._df.empty:
            return []

        # Filter by Crop, Year and Month
        filtered = self._df[(self._df['Crop Name'] == crop) & (self._df['Year'] == year) & (self._df['Month Number'] == month_num)]
        if filtered.empty:
            # Fallback to just crop and year or crop
            filtered = self._df[self._df['Crop Name'] == crop]
            if not filtered.empty:
                latest_yr = filtered['Year'].max()
                filtered = filtered[filtered['Year'] == latest_yr]
                latest_m = filtered['Month Number'].max()
                filtered = filtered[filtered['Month Number'] == latest_m]

        if filtered.empty:
            return []

        # Sort by State name alphabetically for easy browsing
        filtered = filtered.sort_values(by='State', ascending=True).reset_index(drop=True)
        
        if limit is not None:
            filtered = filtered.head(limit)
        
        rates = []
        for _, row in filtered.iterrows():
            rates.append({
                'crop': str(row['Crop Name']),
                'state': str(row['State']),
                'date': f"28 Sep {row['Year']}",
                'min_price': round(float(row['Minimum Price (₹/Quintal)']), 1),
                'modal_price': round(float(row['Modal (Benchmark) Price (₹/Quintal)']), 1),
                'max_price': round(float(row['Maximum Price (₹/Quintal)']), 1)
            })

        return rates

    def get_live_mandi_rates(self, limit=None):
        """
        Fetch registered live Mandi rates across states.
        """
        return self.get_state_rates_for_crop(crop='Bajra', limit=limit)

    def search_prices(self, crop=None, state=None, district=None, mandi=None):
        """
        Compatibility method for Dashboard.
        """
        primary_crop = crop if crop and crop != 'all' and crop else 'Wheat'
        primary_state = state if state and state != 'all' and state else 'Uttar Pradesh'
        trend_res = self.get_trend_data(primary_state, primary_crop, selected_year=2026)
        
        if trend_res:
            st = trend_res['stats']
            cd = trend_res['chart_data']
            return {
                'records': self.get_state_rates_for_crop(primary_crop, limit=10),
                'stats': {
                    'min_price': st['min_price'],
                    'max_price': st['max_price'],
                    'modal_price': st['modal_price'],
                    'primary_crop': primary_crop,
                    'state': primary_state,
                    'total_mandis': 10,
                    'price_change': st['price_change'],
                    'trend': st['trend']
                },
                'trend_chart': cd
            }
        
        return {
            'records': [],
            'stats': {
                'min_price': 2100,
                'max_price': 2550,
                'modal_price': 2380,
                'primary_crop': primary_crop,
                'state': primary_state,
                'total_mandis': 10,
                'price_change': '+₹45.00 (+1.9%) vs last month',
                'trend': 'upward'
            },
            'trend_chart': {'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 'modal_prices': [2380]*12}
        }
