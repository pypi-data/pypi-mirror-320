import pandas as pd
import os
import json
import gzip
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Union, Optional
from collections import defaultdict
from pydantic import ValidationError as PydanticValidationError
from subsetsio.models.chart import parse_chart
import requests
from tqdm import tqdm

class ChartSortField(str, Enum):
    UPDATED_AT = "updated_at"
    CREATED_AT = "created_at"
    TITLE = "title"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

@dataclass
class ValidationErrorSummary:
    error_type: str
    message: str
    examples: List[Dict[str, Any]]
    total_occurrences: int
    charts_affected: List[str]

class ValidationError(Exception):
    def __init__(self, error_summaries: List[ValidationErrorSummary], max_examples: int = 3):
        self.error_summaries = error_summaries
        self.max_examples = max_examples
        
        error_details = []
        for summary in error_summaries:
            examples = summary.examples[:max_examples]
            omitted = len(summary.examples) - max_examples if len(summary.examples) > max_examples else 0
            
            error_details.extend([
                f"\nError Type: {summary.error_type}",
                f"Message: {summary.message}",
                f"Affected Charts: {len(summary.charts_affected)}",
                f"Total Occurrences: {summary.total_occurrences}",
                "Examples:"
            ])
            
            error_details.extend(f"  - {example}" for example in examples)
            if omitted > 0:
                error_details.append(f"  ... {omitted} more similar errors omitted")
        
        super().__init__("Validation failed:\n" + "\n".join(error_details))

class SubsetsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = os.getenv("SUBSETS_API_URL", "https://api.subsets.io")
        self.headers = {
            "X-API-Key": api_key,
            "Content-Encoding": "gzip",
            "Accept-Encoding": "gzip"
        }
        self.data_dir = Path(os.getenv('DATA_DIR', 'data'))
        self.state_file = self.data_dir / 'sync_state.csv'

    def _group_validation_errors(self, errors: List[Dict[str, Any]], max_examples: int = 3) -> List[ValidationErrorSummary]:
        error_groups = defaultdict(list)
        
        for chart_idx, error in enumerate(errors):
            if "error" in error:
                if isinstance(error["error"], list):  # Pydantic validation errors
                    for e in error["error"]:
                        key = (e.get("type", "unknown"), str(e.get("msg", "")))
                        error_groups[key].append({
                            "chart_index": chart_idx,
                            "location": e.get("loc", []),
                            "detail": e
                        })
                else:  # Other exceptions
                    key = (error["error"].__class__.__name__, str(error["error"]))
                    error_groups[key].append({
                        "chart_index": chart_idx,
                        "detail": error["error"]
                    })

        return [
            ValidationErrorSummary(
                error_type=error_type,
                message=message,
                examples=group[:max_examples],
                total_occurrences=len(group),
                charts_affected=sorted(set(str(e["chart_index"]) for e in group))
            )
            for (error_type, message), group in sorted(
                error_groups.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )
        ]

    def validate(self, charts: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Validate a single chart or list of charts without making API calls."""
        # Convert single chart to list for consistent processing
        charts_list = charts if isinstance(charts, list) else [charts]
        
        errors = []
        for i, chart in enumerate(charts_list):
            try:
                parse_chart(chart)
            except PydanticValidationError as e:
                errors.append({"chart_index": i, "error": e.errors()})
            except Exception as e:
                errors.append({"chart_index": i, "error": e})
        
        if errors:
            raise ValidationError(self._group_validation_errors(errors))
        return []

    def _gzip_json(self, data: Any) -> bytes:
        return gzip.compress(json.dumps(data).encode('utf-8'))

    def _load_state(self) -> Dict[str, str]:
        return pd.read_csv(self.state_file).set_index('source_id')['last_update'].to_dict() if self.state_file.exists() else {}

    def _save_state(self, state: Dict[str, str]):
        self.data_dir.mkdir(exist_ok=True)
        pd.DataFrame([{'source_id': k, 'last_update': v} for k, v in state.items()]).to_csv(self.state_file, index=False)

    def create(self, charts: Union[Dict[str, Any], List[Dict[str, Any]]], validate: bool = True) -> Union[str, List[str]]:
        """Create new charts in batches
        
        Args:
            charts: A single chart dict or list of chart dicts to create
            validate: Whether to validate charts before sending to API
            
        Returns:
            For a single chart: The chart ID as a string
            For multiple charts: A list of chart IDs
        """
        if not isinstance(charts, list):
            charts = [charts]
            
        if len(charts) == 0:
            raise ValueError("No charts provided")
            
        # Validate all charts if requested
        if validate:
            self.validate(charts)
        
        all_chart_ids = []
        batch_size = 5000
        for i in tqdm(range(0, len(charts), batch_size), desc="Creating charts"):
            batch = charts[i:i + batch_size]
            response = requests.post(
                f"{self.api_url}/chart",
                headers=self.headers,
                data=self._gzip_json(batch)
            )
            response.raise_for_status()
            result = response.json()
            
            # Handle single ID or list of IDs
            if isinstance(result, str):
                all_chart_ids.append(result)
            elif isinstance(result, list):
                all_chart_ids.extend(result)
            else:
                raise ValueError(f"Unexpected response format from API: {type(result)}")
        
        # Return single ID if only one chart was created, otherwise return list
        return all_chart_ids[0] if len(all_chart_ids) == 1 else all_chart_ids

    def update(self, charts: Union[Dict[str, Any], List[Dict[str, Any]]], validate: bool = True) -> Dict[str, Any]:
        """Update existing charts with metadata and/or data"""
        if not isinstance(charts, list):
            charts = [charts]
            
        # temp disable, need to use partial models for updates
        # Validate charts if requested
        # if validate:
        #     self.validate(charts)
        
        # Send request
        response = requests.put(
            f"{self.api_url}/chart",
            headers=self.headers,
            data=self._gzip_json(charts)
        )
        response.raise_for_status()
        return response.json()

    def add_data_rows(self, updates: Dict[str, List[List[Any]]], validate: bool = True) -> Dict[str, Any]:
        """Append new data rows to existing charts"""
        # Send request
        response = requests.post(
            f"{self.api_url}/chart/data/rows",
            headers=self.headers,
            data=self._gzip_json(updates)
        )
        response.raise_for_status()
        return response.json()

    def delete(
        self,
        chart_ids: Optional[List[str]] = None,
        chart_types: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
        created_after: Optional[Union[datetime, str]] = None,
        created_before: Optional[Union[datetime, str]] = None,
        updated_after: Optional[Union[datetime, str]] = None,
        updated_before: Optional[Union[datetime, str]] = None,
        is_draft: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Delete charts matching the specified filters.
        
        Args:
            chart_ids: List of specific chart IDs to delete
            chart_types: List of chart types to filter by
            tags: Dictionary of tags to filter by
            created_after: Delete charts created after this timestamp
            created_before: Delete charts created before this timestamp
            updated_after: Delete charts updated after this timestamp
            updated_before: Delete charts updated before this timestamp
            is_draft: Filter by draft status
            
        Returns:
            Dict containing deletion results
        """
        filters = {
            "chart_ids": chart_ids,
            "chart_types": chart_types,
            "tags": tags,
            "created_after": created_after.isoformat() if isinstance(created_after, datetime) else created_after,
            "created_before": created_before.isoformat() if isinstance(created_before, datetime) else created_before,
            "updated_after": updated_after.isoformat() if isinstance(updated_after, datetime) else updated_after,
            "updated_before": updated_before.isoformat() if isinstance(updated_before, datetime) else updated_before,
            "is_draft": is_draft
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        response = requests.delete(
            f"{self.api_url}/chart",
            headers=self.headers,
            json=filters
        )
        response.raise_for_status()
        return response.json()

    def get(
        self,
        chart_ids: Optional[List[str]] = None,
        chart_types: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
        created_after: Optional[Union[datetime, str]] = None,
        created_before: Optional[Union[datetime, str]] = None,
        updated_after: Optional[Union[datetime, str]] = None,
        updated_before: Optional[Union[datetime, str]] = None,
        text_search: Optional[str] = None,
        is_draft: Optional[bool] = None,
        sort_by: ChartSortField = None,
        sort_order: SortOrder = None,
        limit = None,
        offset = None
    ) -> Dict[str, Any]:
        """
        Get charts matching the specified filters.
        
        Args:
            chart_ids: List of specific chart IDs to retrieve
            chart_types: List of chart types to filter by
            tags: Dictionary of tags to filter by
            created_after: Get charts created after this timestamp
            created_before: Get charts created before this timestamp
            updated_after: Get charts updated after this timestamp
            updated_before: Get charts updated before this timestamp
            text_search: Search in chart title, subtitle, and description
            is_draft: Filter by draft status
            sort_by: Field to sort results by
            sort_order: Sort direction (asc or desc)
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            Dict containing matched charts and metadata
        """
        params = {
            "chart_ids": chart_ids,
            "chart_types": chart_types,
            "tags": tags,
            "created_after": created_after.isoformat() if created_after else None,
            "created_before": created_before.isoformat() if created_before else None,
            "updated_after": updated_after.isoformat() if updated_after else None,
            "updated_before": updated_before.isoformat() if updated_before else None,
            "text_search": text_search,
            "is_draft": is_draft,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "limit": limit,
            "offset": offset
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}        
        response = requests.get(
            f"{self.api_url}/chart",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def get_by_id(self, chart_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single chart by its ID.
        
        Args:
            chart_id: The unique identifier of the chart to retrieve
            
        Returns:
            Dict containing the chart data if found, None otherwise
        
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        response = requests.get(
            f"{self.api_url}/chart/{chart_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def sync(self, charts: List[Dict], validate: bool = True) -> None:
        """Sync charts with server, creating new ones or updating existing ones"""
        # Validate all charts if requested
        if validate:
            self.validate(charts)
        
        state = self._load_state()
        by_source = {chart['tags']['id']: chart for chart in charts}
        
        to_create = []
        to_update = {}
        
        for source_id, chart in by_source.items():
            if not (data := chart.get('data')):
                continue
                
            last_date = data[-1][0]  # Assuming timestamp is first element
            if source_id not in state:
                to_create.append(chart)
            elif last_date > state[source_id]:
                to_update[source_id] = [p for p in data if p[0] > state[source_id]]
            state[source_id] = last_date
            
        if to_create:
            self.create(to_create, validate=validate)
            
        if to_update:
            self.add_data_rows(to_update, validate=validate)
            
        self._save_state(state)