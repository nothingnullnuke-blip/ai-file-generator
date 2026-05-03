from typing import Dict, Any
from datetime import datetime

class ReportTemplate:
    @staticmethod
    def create(title: str, content: Dict[str, Any] = None) -> Dict[str, Any]:
        if content is None:
            content = {}
        
        return {
            "title": title,
            "description": f"Business report generated on {datetime.now().strftime('%Y-%m-%d')}",
            "color_scheme": "professional",
            "sections": [
                {
                    "type": "heading",
                    "content": {"text": "Executive Summary"},
                    "order": 0
                },
                {
                    "type": "text",
                    "content": {
                        "text": content.get("summary", 
                            "This report provides a comprehensive analysis of key business metrics "
                            "and performance indicators.")
                    },
                    "order": 1
                },
                {
                    "type": "heading",
                    "content": {"text": "Key Metrics"},
                    "order": 2
                },
                {
                    "type": "table",
                    "content": {
                        "title": "Performance Summary",
                        "headers": ["Metric", "Value", "Target", "Status"],
                        "rows": [
                            ["Revenue Growth", "12%", "10%", "✓ Above Target"],
                            ["Customer Satisfaction", "4.5/5", "4.0/5", "✓ Exceeds"],
                            ["Operational Efficiency", "85%", "80%", "✓ Meets"]
                        ]
                    },
                    "order": 3
                }
            ],
            "metadata": {
                "generated": True,
                "template": "report",
                "created_at": datetime.now().isoformat()
            }
        }

class InvoiceTemplate:
    @staticmethod
    def create(company: str, amount: float) -> Dict[str, Any]:
        return {
            "title": f"Invoice - {company}",
            "description": f"Invoice for {company}",
            "color_scheme": "professional",
            "sections": [
                {
                    "type": "text",
                    "content": {"text": f"Company: {company}\nAmount Due: ${amount:.2f}"},
                    "order": 0
                },
                {
                    "type": "table",
                    "content": {
                        "title": "Invoice Details",
                        "headers": ["Description", "Quantity", "Rate", "Total"],
                        "rows": [
                            ["Professional Services", "1", f"${amount:.2f}", f"${amount:.2f}"]
                        ]
                    },
                    "order": 1
                }
            ],
            "metadata": {
                "template": "invoice",
                "created_at": datetime.now().isoformat()
            }
        }

class DashboardTemplate:
    @staticmethod
    def create(title: str = "Performance Dashboard", metrics: Dict[str, float] = None) -> Dict[str, Any]:
        if metrics is None:
            metrics = {
                "Active Users": 1250,
                "Revenue": 45000,
                "Conversion Rate": 3.5,
                "Customer Satisfaction": 4.7
            }
        
        return {
            "title": title,
            "description": f"Dashboard as of {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "color_scheme": "modern",
            "sections": [
                {
                    "type": "heading",
                    "content": {"text": "Key Performance Indicators"},
                    "order": 0
                },
                {
                    "type": "table",
                    "content": {
                        "title": "Metric Summary",
                        "headers": ["Metric", "Current Value", "Change", "Status"],
                        "rows": [
                            [
                                name,
                                f"{value:.0f}" if isinstance(value, (int, float)) else str(value),
                                "+12%",
                                "✓"
                            ]
                            for name, value in list(metrics.items())[:5]
                        ]
                    },
                    "order": 1
                }
            ],
            "metadata": {
                "generated": True,
                "template": "dashboard",
                "created_at": datetime.now().isoformat()
            }
        }