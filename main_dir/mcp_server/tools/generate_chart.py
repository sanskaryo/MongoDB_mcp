"""Chart generation tool for MCP server."""

import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import matplotlib
import pandas as pd
import seaborn as sns
from pydantic import BaseModel, ConfigDict, Field

matplotlib.use("Agg")  # Set backend before importing pyplot
import matplotlib.pyplot as plt

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class GenerateChartInput(BaseModel):
    """Strict input schema for generate_chart_from_data."""

    model_config = ConfigDict(extra="forbid")

    data_source: str
    chart_type: str = "bar"
    title: Optional[str] = None
    x_field: Optional[str] = None
    y_field: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@mcp.tool()
def generate_chart_from_data(params: GenerateChartInput) -> Dict[str, Any]:
        """Generate chart from MongoDB data
        
        Args:
            data_source: Source of data ('revenue_daily', 'customer_segments', 'top_menu_items', etc.)
            chart_type: Type of chart ('bar', 'line', 'pie', 'horizontal_bar')
            title: Optional chart title
            x_field: X-axis field name
            y_field: Y-axis field name  
            limit: Number of data points to include
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)
            y_field: Y-axis field name  
            limit: Number of data points to include
            
        Returns:
            Chart file information and data summary
        """
        try:
            data_source = params.data_source
            chart_type = params.chart_type
            title = params.title
            x_field = params.x_field
            y_field = params.y_field
            limit = params.limit
            start_date = params.start_date
            end_date = params.end_date

            db = mongo_client.db
            # Create charts directory
            charts_dir = "./charts"
            os.makedirs(charts_dir, exist_ok=True)
            
            # Get data based on source
            chart_data = None
            
            # Add date filtering to pipeline if dates provided
            date_match = {}
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                date_match = {"$match": {"order_date": date_filter}}

            if data_source == "revenue_daily":
                pipeline = []
                if date_match:
                    pipeline.append(date_match)
                pipeline.extend([
                    {"$group": {
                        "_id": "$order_date",
                        "value": {"$sum": "$total_amount"},
                        "count": {"$sum": 1}
                    }},
                    {"$project": {"order_date": "$_id", "value": 1, "count": 1, "_id": 0}},
                    {"$sort": {"order_date": 1}},
                    {"$limit": limit}
                ])
                chart_data = list(db["orders"].aggregate(pipeline))
                x_field = x_field or "order_date"
                y_field = y_field or "value"
                title = title or "Daily Revenue Trends"
                chart_type = "line"  # Force line chart for time series data
                
            elif data_source == "customer_segments":
                pipeline = [
                    {"$group": {
                        "_id": "$segment",
                        "value": {"$sum": 1},
                        "avg_spending": {"$avg": "$total_spent"}
                    }},
                    {"$project": {"segment": "$_id", "value": 1, "avg_spending": 1, "_id": 0}},
                    {"$sort": {"value": -1}}
                ]
                chart_data = list(db["customers"].aggregate(pipeline))
                x_field = x_field or "segment"
                y_field = y_field or "value"
                title = title or "Customer Segments Distribution"
                chart_type = "pie"
                
            elif data_source == "top_menu_items":
                pipeline = []
                if date_match:
                    pipeline.append(date_match)
                pipeline.extend([
                    {"$unwind": "$items"},
                    {"$group": {
                        "_id": "$items.name",
                        "value": {"$sum": "$items.quantity"},
                        "revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}}
                    }},
                    {"$project": {"item_name": "$_id", "value": 1, "revenue": 1, "_id": 0}},
                    {"$sort": {"value": -1}},
                    {"$limit": limit}
                ])
                chart_data = list(db["orders"].aggregate(pipeline))
                x_field = x_field or "item_name"
                y_field = y_field or "value"
                title = title or f"Top {limit} Menu Items"
                chart_type = "horizontal_bar"
                
            elif data_source == "order_status":
                pipeline = []
                if date_match:
                    pipeline.append(date_match)
                pipeline.extend([
                    {"$group": {
                        "_id": "$status",
                        "value": {"$sum": 1},
                        "revenue": {"$sum": "$total_amount"}
                    }},
                    {"$project": {"status": "$_id", "value": 1, "revenue": 1, "_id": 0}},
                    {"$sort": {"value": -1}}
                ])
                chart_data = list(db["orders"].aggregate(pipeline))
                x_field = x_field or "status"
                y_field = y_field or "value"
                title = title or "Order Status Distribution"
                chart_type = "pie"
                
            elif data_source == "order_types":
                pipeline = []
                if date_match:
                    pipeline.append(date_match)
                pipeline.extend([
                    {"$group": {
                        "_id": "$order_type",
                        "value": {"$sum": 1},
                        "revenue": {"$sum": "$total_amount"}
                    }},
                    {"$project": {"order_type": "$_id", "value": 1, "revenue": 1, "_id": 0}},
                    {"$sort": {"value": -1}}
                ])
                chart_data = list(db["orders"].aggregate(pipeline))
                x_field = x_field or "order_type"
                y_field = y_field or "value"
                title = title or "Order Types Distribution"
                chart_type = "pie"
                
            else:
                return {"error": f"Unknown data source: {data_source}"}
            
            if not chart_data:
                return {"error": "No data found for chart generation"}
            
            # Generate chart
            chart_path = _create_chart(chart_data, chart_type, title, x_field, y_field, charts_dir)
            
            if chart_path:
                filename = os.path.basename(chart_path)
                return {
                    "success": True,
                    "chart_file": filename,
                    "chart_path": chart_path,
                    "chart_type": chart_type,
                    "data_points": len(chart_data),
                    "title": title,
                    "data_summary": chart_data[:5] if len(chart_data) > 5 else chart_data  # Show first 5 points
                }
            else:
                return {"error": "Failed to generate chart"}
                
        except Exception as e:
            return {"error": f"Chart generation failed: {str(e)}"}

def _create_chart(data, chart_type, title, x_field, y_field, charts_dir):
    """Create chart file from data with robust error handling"""
    try:
        # Validate inputs
        if not data:
            print("Chart creation error: No data provided")
            return None
        
        if not isinstance(data, list) or len(data) == 0:
            print("Chart creation error: Data must be a non-empty list")
            return None
        
        # Check data structure
        sample_item = data[0]
        if not isinstance(sample_item, dict):
            print("Chart creation error: Data items must be dictionaries")
            return None
        
        available_fields = list(sample_item.keys())
        print(f"Available fields in data: {available_fields}")
        
        # Fallback to first available fields if requested fields are missing
        if x_field not in available_fields:
            old_x = x_field
            x_field = available_fields[0]
            print(f"⚠️ x_field '{old_x}' not found, falling back to '{x_field}'")
            
        if y_field not in available_fields:
            old_y = y_field
            # Try to find a numeric field for y
            numeric_fields = [f for f, v in sample_item.items() if isinstance(v, (int, float))]
            if numeric_fields:
                y_field = numeric_fields[0]
            else:
                y_field = available_fields[1] if len(available_fields) > 1 else available_fields[0]
            print(f"⚠️ y_field '{old_y}' not found, falling back to '{y_field}'")
        
        # Generate safe filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"chart_{timestamp}_{unique_id}.png"
        filepath = os.path.join(charts_dir, filename)
        
        # Extract and validate data
        x_values = []
        y_values = []
        
        for item in data:
            try:
                x_val = item.get(x_field)
                y_val = item.get(y_field)
                
                if x_val is not None and y_val is not None:
                    x_values.append(x_val)  # Keep original data type
                    y_values.append(float(y_val) if isinstance(y_val, (int, float)) else 0)
            except (ValueError, TypeError) as e:
                print(f"Skipping invalid data item: {item}, error: {e}")
                continue
        
        if not x_values or not y_values:
            print("Chart creation error: No valid data points after processing")
            return None
        
        # Create figure with error handling
        plt.clf()  # Clear any existing plots
        fig, ax = plt.subplots(figsize=(12, 8))
        
        try:
            if chart_type == "pie":
                # Handle pie chart specially
                if len(set(y_values)) == 1 and y_values[0] == 0:
                    print("Chart creation error: All pie chart values are zero")
                    return None
                    
                colors = plt.cm.Set3(range(len(x_values)))
                wedges, texts, autotexts = ax.pie(
                    y_values, 
                    labels=x_values, 
                    autopct='%1.1f%%',
                    colors=colors, 
                    startangle=90
                )
                
                # Enhance text readability
                for text in texts:
                    text.set_fontsize(10)
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(9)
                    
            elif chart_type == "horizontal_bar":
                colors = plt.cm.Set3(range(len(x_values)))
                bars = ax.barh(x_values, y_values, color=colors)
                ax.set_xlabel(y_field.replace('_', ' ').title())
                ax.set_ylabel(x_field.replace('_', ' ').title())
                
                # Add value labels
                for bar, value in zip(bars, y_values):
                    width = bar.get_width()
                    ax.annotate(f'{int(value):,}', 
                               xy=(width, bar.get_y() + bar.get_height() / 2),
                               xytext=(3, 0), textcoords="offset points", 
                               ha='left', va='center', fontsize=9)
                
            elif chart_type == "line":
                # For line charts, use numeric positions if x_values are strings
                if all(isinstance(x, str) for x in x_values):
                    positions = range(len(x_values))
                    ax.plot(positions, y_values, marker='o', linewidth=2, markersize=6)
                    ax.set_xticks(positions)
                    ax.set_xticklabels(x_values, rotation=45, ha='right')
                else:
                    ax.plot(x_values, y_values, marker='o', linewidth=2, markersize=6)
                    ax.tick_params(axis='x', rotation=45)
                ax.set_xlabel(x_field.replace('_', ' ').title())
                ax.set_ylabel(y_field.replace('_', ' ').title())
                
            else:  # Default to bar chart
                colors = plt.cm.Set3(range(len(x_values)))
                
                # For bar charts, use numeric positions if x_values are strings
                if all(isinstance(x, str) for x in x_values):
                    positions = range(len(x_values))
                    bars = ax.bar(positions, y_values, color=colors)
                    ax.set_xticks(positions)
                    ax.set_xticklabels(x_values, rotation=45, ha='right')
                    
                    # Add value labels on bars (using positions)
                    for i, (bar, value) in enumerate(zip(bars, y_values)):
                        height = bar.get_height()
                        ax.annotate(f'{int(value):,}', 
                                   xy=(i, height),
                                   xytext=(0, 3), textcoords="offset points", 
                                   ha='center', va='bottom', fontsize=9)
                else:
                    bars = ax.bar(x_values, y_values, color=colors)
                    ax.tick_params(axis='x', rotation=45)
                    
                    # Add value labels on bars (using x_values)
                    for bar, value in zip(bars, y_values):
                        height = bar.get_height()
                        ax.annotate(f'{int(value):,}', 
                                   xy=(bar.get_x() + bar.get_width() / 2, height),
                                   xytext=(0, 3), textcoords="offset points", 
                                   ha='center', va='bottom', fontsize=9)
                
                ax.set_xlabel(x_field.replace('_', ' ').title())
                ax.set_ylabel(y_field.replace('_', ' ').title())
            
            # Add title and styling
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            if chart_type not in ['pie']:
                ax.grid(True, alpha=0.3, axis='y')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
            
            # Add timestamp
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            fig.text(0.99, 0.01, f'Generated: {timestamp_str}', 
                    ha='right', va='bottom', fontsize=8, alpha=0.6)
            
            # Save with tight layout
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close(fig)  # Explicitly close figure
            
            print(f"Chart successfully created: {filepath}")
            return filepath
            
        except Exception as plot_error:
            plt.close(fig)  # Ensure figure is closed on error
            print(f"Chart plotting error: {plot_error}")
            return None
        
    except Exception as e:
        print(f"Chart creation error: {str(e)}")
        if 'fig' in locals():
            plt.close(fig)
        return None