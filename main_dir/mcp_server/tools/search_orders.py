"""Search orders by criteria tool."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class SearchOrdersInput(BaseModel):
    """Strict input schema for search_orders_by_criteria."""

    model_config = ConfigDict(extra="forbid")

    customer_segment: Optional[str] = None
    order_type: Optional[str] = None
    status: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=500)


@mcp.tool()
def search_orders_by_criteria(params: SearchOrdersInput) -> List[Dict[str, Any]]:
        """Search orders by multiple criteria

        Args:
            customer_segment: Filter by customer segment (vip, standard, etc.)
            order_type: Filter by order type (dine-in, delivery, etc.)
            status: Filter by order status
            min_amount: Minimum order amount
            max_amount: Maximum order amount
            start_date: Start date filter (YYYY-MM-DD format)
            end_date: End date filter (YYYY-MM-DD format)
            limit: Number of results to return (default: 10)
            
        Returns:
            List of orders matching the criteria
            
        WORKFLOW:
            For custom searches, first use:
            1. mongodb_get_collections() - to see available collections
            2. mongodb_describe_collection() - to understand field names and structure
        """
        try:
            db = mongo_client.db
            customer_segment = params.customer_segment
            order_type = params.order_type
            status = params.status
            min_amount = params.min_amount
            max_amount = params.max_amount
            start_date = params.start_date
            end_date = params.end_date
            limit = params.limit
            # Build match criteria
            match_criteria = {}
            
            if min_amount is not None or max_amount is not None:
                amount_filter = {}
                if min_amount is not None:
                    amount_filter["$gte"] = min_amount
                if max_amount is not None:
                    amount_filter["$lte"] = max_amount
                match_criteria["total_amount"] = amount_filter
            
            if start_date is not None or end_date is not None:
                date_filter = {}
                if start_date is not None:
                    date_filter["$gte"] = start_date
                if end_date is not None:
                    date_filter["$lte"] = end_date
                match_criteria["order_date"] = date_filter
            
            if order_type:
                match_criteria["order_type"] = order_type
            
            if status:
                match_criteria["status"] = status
            
            # Pipeline with customer lookup if segment filter needed
            pipeline = []
            
            if customer_segment:
                pipeline.extend([
                    {"$lookup": {
                        "from": "customers",
                        "localField": "customer_id", 
                        "foreignField": "customer_id",
                        "as": "customer"
                    }},
                    {"$unwind": "$customer"},
                    {"$match": {"customer.segment": customer_segment}}
                ])
            
            if match_criteria:
                pipeline.append({"$match": match_criteria})
            
            pipeline.extend([
                {"$sort": {"order_date": -1, "order_time": -1}},
                {"$limit": limit},
                {"$project": {
                    "order_id": 1,
                    "customer_id": 1,
                    "order_date": 1,
                    "order_time": 1,
                    "order_type": 1,
                    "status": 1,
                    "total_amount": 1,
                    "customer_segment": "$customer.segment" if customer_segment else None
                }}
            ])
            
            # Remove None values from projection
            if pipeline[-1]["$project"]["customer_segment"] is None:
                del pipeline[-1]["$project"]["customer_segment"]
            
            return list(db["orders"].aggregate(pipeline))
            
        except Exception as e:
            return [{"error": f"Order search failed: {str(e)}"}]