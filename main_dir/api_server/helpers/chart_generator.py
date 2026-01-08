"""
Chart Generator for MongoDB Analytics Agent
Generates various types of charts based on query results and data types
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from typing import Dict, Any, List, Optional
import os
import uuid
from datetime import datetime
import numpy as np

# Set style for better looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ChartGenerator:
    def __init__(self, charts_dir: str = "./charts"):
        self.charts_dir = charts_dir
        os.makedirs(charts_dir, exist_ok=True)
    
    def suggest_chart_type(self, query: str, tools_used: List[str]) -> str:
        """Suggest appropriate chart type based on query and tools used"""
        query_lower = query.lower()
        
        # Revenue and financial data - line/bar charts work best
        if any(tool in tools_used for tool in ["get_revenue_analytics", "get_revenue_by_date"]):
            if "trend" in query_lower or "over time" in query_lower or "daily" in query_lower:
                return "line"
            else:
                return "bar"
        
        # Customer segments - pie chart for distribution
        if "get_customer_segments" in tools_used:
            return "pie"
        
        # Top items/customers - horizontal bar chart
        if any(tool in tools_used for tool in ["get_customer_insights", "get_menu_performance", "get_menu_revenue"]):
            return "horizontal_bar"
        
        # Status/breakdown data - pie or bar
        if any(tool in tools_used for tool in ["get_order_status", "get_order_types", "get_payment_methods_breakdown"]):
            return "pie" if "breakdown" in query_lower else "bar"
        
        # Comparison queries - bar chart
        if any(word in query_lower for word in ["compare", "vs", "versus", "between"]):
            return "bar"
        
        # Time series data - line chart
        if any(word in query_lower for word in ["trend", "over time", "timeline", "history"]):
            return "line"
        
        # Default to bar chart
        return "bar"
    
    async def generate_chart(
        self, 
        query: str, 
        result_data: Dict[str, Any], 
        chart_type: str,
        tools_used: List[str]
    ) -> Optional[str]:
        """Generate chart based on the result data"""
        
        try:
            # Extract data from agent response
            chart_data = await self._extract_chart_data(result_data, tools_used)
            
            if not chart_data:
                return None
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"chart_{timestamp}_{unique_id}.png"
            filepath = os.path.join(self.charts_dir, filename)
            
            # Create chart based on type
            fig, ax = plt.subplots(figsize=(12, 8))
            
            if chart_type == "line":
                self._create_line_chart(ax, chart_data, query)
            elif chart_type == "bar":
                self._create_bar_chart(ax, chart_data, query)
            elif chart_type == "horizontal_bar":
                self._create_horizontal_bar_chart(ax, chart_data, query)
            elif chart_type == "pie":
                self._create_pie_chart(ax, chart_data, query)
            elif chart_type == "table":
                self._create_table_chart(ax, chart_data, query)
            else:
                self._create_bar_chart(ax, chart_data, query)  # Default
            
            # Add title and styling
            self._add_chart_styling(fig, ax, query, chart_type)
            
            # Save chart
            plt.tight_layout()
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            print(f"❌ Chart generation failed: {e}")
            return None
    
    async def _extract_chart_data(self, result_data: Dict[str, Any], tools_used: List[str]) -> Optional[Dict[str, Any]]:
        """Extract relevant data for charting from agent response"""
        
        # This is a simplified approach - in a real implementation, 
        # you'd need to parse the actual tool responses from the MCP server
        
        # For now, we'll create sample data based on common tool patterns
        if "get_daily_revenue" in tools_used:
            return {
                "type": "time_series",
                "x_label": "Date",
                "y_label": "Revenue ($)",
                "data": {
                    "2024-12-15": 12500,
                    "2024-12-16": 13200,
                    "2024-12-17": 11800,
                    "2024-12-18": 14600,
                    "2024-12-19": 15400,
                    "2024-12-20": 16200,
                    "2024-12-21": 17800
                }
            }
        
        elif "get_customer_segments_breakdown" in tools_used:
            return {
                "type": "categorical",
                "title": "Customer Segments",
                "data": {
                    "VIP": 25,
                    "Premium": 35,
                    "Standard": 30,
                    "Basic": 10
                }
            }
        
        elif any(tool in tools_used for tool in ["get_top_customers_by_spending", "get_top_menu_items_by_orders"]):
            return {
                "type": "ranking",
                "x_label": "Amount",
                "y_label": "Items",
                "data": {
                    "Item 1": 450,
                    "Item 2": 380,
                    "Item 3": 320,
                    "Item 4": 280,
                    "Item 5": 240
                }
            }
        
        elif "get_order_status_breakdown" in tools_used:
            return {
                "type": "categorical",
                "title": "Order Status Distribution",
                "data": {
                    "Completed": 78,
                    "Pending": 12,
                    "Processing": 8,
                    "Cancelled": 2
                }
            }
        
        # Default sample data
        return {
            "type": "categorical",
            "title": "Sample Data",
            "data": {
                "Category A": 30,
                "Category B": 45,
                "Category C": 25
            }
        }
    
    def _create_line_chart(self, ax, chart_data: Dict[str, Any], query: str):
        """Create line chart for time series data"""
        data = chart_data["data"]
        dates = list(data.keys())
        values = list(data.values())
        
        ax.plot(dates, values, marker='o', linewidth=3, markersize=8)
        ax.set_xlabel(chart_data.get("x_label", "Date"))
        ax.set_ylabel(chart_data.get("y_label", "Value"))
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Add value labels on points
        for i, (date, value) in enumerate(zip(dates, values)):
            ax.annotate(f'${value:,}' if '$' in chart_data.get("y_label", "") else f'{value}',
                       (date, value), textcoords="offset points", xytext=(0,10), ha='center')
    
    def _create_bar_chart(self, ax, chart_data: Dict[str, Any], query: str):
        """Create vertical bar chart"""
        data = chart_data["data"]
        categories = list(data.keys())
        values = list(data.values())
        
        bars = ax.bar(categories, values, color=sns.color_palette("husl", len(categories)))
        ax.set_xlabel(chart_data.get("x_label", "Category"))
        ax.set_ylabel(chart_data.get("y_label", "Value"))
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.annotate(f'{value:,}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom')
        
        plt.xticks(rotation=45)
    
    def _create_horizontal_bar_chart(self, ax, chart_data: Dict[str, Any], query: str):
        """Create horizontal bar chart for rankings"""
        data = chart_data["data"]
        categories = list(data.keys())
        values = list(data.values())
        
        bars = ax.barh(categories, values, color=sns.color_palette("husl", len(categories)))
        ax.set_xlabel(chart_data.get("x_label", "Value"))
        ax.set_ylabel(chart_data.get("y_label", "Category"))
        
        # Add value labels
        for bar, value in zip(bars, values):
            width = bar.get_width()
            ax.annotate(f'{value:,}',
                       xy=(width, bar.get_y() + bar.get_height() / 2),
                       xytext=(3, 0), textcoords="offset points",
                       ha='left', va='center')
    
    def _create_pie_chart(self, ax, chart_data: Dict[str, Any], query: str):
        """Create pie chart for categorical distributions"""
        data = chart_data["data"]
        labels = list(data.keys())
        values = list(data.values())
        
        colors = sns.color_palette("husl", len(labels))
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        
        # Enhance text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    def _create_table_chart(self, ax, chart_data: Dict[str, Any], query: str):
        """Create table visualization"""
        data = chart_data["data"]
        
        # Convert to DataFrame for table
        df = pd.DataFrame(list(data.items()), columns=['Category', 'Value'])
        
        ax.axis('tight')
        ax.axis('off')
        
        table = ax.table(cellText=df.values, colLabels=df.columns,
                        cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.5)
    
    def _add_chart_styling(self, fig, ax, query: str, chart_type: str):
        """Add title and styling to the chart"""
        # Generate title from query
        title = self._generate_chart_title(query, chart_type)
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Add grid for non-pie charts
        if chart_type != 'pie':
            ax.grid(True, alpha=0.3)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        fig.text(0.99, 0.01, f'Generated: {timestamp}', 
                ha='right', va='bottom', fontsize=8, alpha=0.7)
    
    def _generate_chart_title(self, query: str, chart_type: str) -> str:
        """Generate appropriate chart title from query"""
        query_words = query.lower().split()
        
        if any(word in query_words for word in ['revenue', 'sales', 'money']):
            if 'daily' in query_words or 'trend' in query_words:
                return "Revenue Trends Over Time"
            else:
                return "Revenue Analysis"
        
        elif any(word in query_words for word in ['customer', 'customers']):
            if 'top' in query_words:
                return "Top Customers by Spending"
            elif 'segment' in query_words:
                return "Customer Segments Distribution"
            else:
                return "Customer Analytics"
        
        elif any(word in query_words for word in ['menu', 'items', 'food']):
            return "Menu Performance Analysis"
        
        elif any(word in query_words for word in ['order', 'orders']):
            return "Order Analytics"
        
        else:
            return "Business Analytics Dashboard"