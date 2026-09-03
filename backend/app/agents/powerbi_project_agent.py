from typing import Any, Dict, List


class PowerBIProjectGenerationAgent:
    """
    Generates a Power BI Project structure from the
    dashboard configuration.

    This module generates project metadata and report/
    semantic-model configuration files.

    It does not generate a binary .pbix file.
    """

    def __init__(self):
        pass

    # =====================================================
    # MAIN GENERATION FUNCTION
    # =====================================================

    def generate(
        self,
        profile: Dict[str, Any],
        dashboard: Dict[str, Any]
    ) -> Dict[str, Any]:

        dashboard_title = dashboard.get(
            "dashboard_title",
            "AI Generated Dashboard"
        )

        pages = dashboard.get(
            "pages",
            []
        )

        project_name = self._create_project_name(
            dashboard_title
        )

        files = []

        # -------------------------------------------------
        # 1. Project file
        # -------------------------------------------------

        project_file = self._generate_project_file(
            project_name
        )

        files.append({
            "path": f"{project_name}.pbip",
            "content": project_file
        })

        # -------------------------------------------------
        # 2. Report definition
        # -------------------------------------------------

        report_definition = self._generate_report_definition(
            dashboard_title,
            pages
        )

        files.append({
            "path": (
                f"{project_name}.Report/"
                "definition/report.json"
            ),
            "content": report_definition
        })

        # -------------------------------------------------
        # 3. Semantic model
        # -------------------------------------------------

        semantic_model = self._generate_semantic_model(
            profile
        )

        files.append({
            "path": (
                f"{project_name}.SemanticModel/"
                "definition/model.json"
            ),
            "content": semantic_model
        })

        # -------------------------------------------------
        # 4. Report metadata
        # -------------------------------------------------

        report_metadata = self._generate_report_metadata(
            dashboard_title
        )

        files.append({
            "path": (
                f"{project_name}.Report/"
                "definition/metadata.json"
            ),
            "content": report_metadata
        })

        # -------------------------------------------------
        # 5. Semantic model metadata
        # -------------------------------------------------

        model_metadata = self._generate_model_metadata(
            project_name
        )

        files.append({
            "path": (
                f"{project_name}.SemanticModel/"
                "definition/metadata.json"
            ),
            "content": model_metadata
        })

        return {
            "project_name": project_name,
            "project_type": "Power BI Project",
            "status": "generated",
            "files": files
        }

    # =====================================================
    # PROJECT NAME
    # =====================================================

    def _create_project_name(
        self,
        dashboard_title: str
    ) -> str:

        name = dashboard_title.strip()

        if not name:
            name = "AI_Generated_Dashboard"

        name = name.replace(" ", "_")

        allowed_characters = (
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789_"
        )

        name = "".join(
            character
            for character in name
            if character in allowed_characters
        )

        if not name:
            name = "AI_Generated_Dashboard"

        return name

    # =====================================================
    # PROJECT FILE
    # =====================================================

    def _generate_project_file(
        self,
        project_name: str
    ) -> str:

        return f'''{{
    "version": "1.0",
    "project": {{
        "name": "{project_name}",
        "type": "PowerBI"
    }}
}}'''

    # =====================================================
    # REPORT DEFINITION
    # =====================================================

    def _generate_report_definition(
        self,
        dashboard_title: str,
        pages: List[Dict[str, Any]]
    ) -> str:

        report_pages = []

        for page in pages:

            page_number = page.get(
                "page_number",
                len(report_pages) + 1
            )

            page_name = page.get(
                "page_name",
                f"Page {page_number}"
            )

            visuals = page.get(
                "visuals",
                []
            )

            report_pages.append({
                "page_number": page_number,
                "page_name": page_name,
                "visual_count": len(visuals),
                "visuals": visuals
            })

        report = {
            "report": {
                "title": dashboard_title,
                "pages": report_pages
            }
        }

        import json

        return json.dumps(
            report,
            indent=4
        )

    # =====================================================
    # SEMANTIC MODEL
    # =====================================================

    def _generate_semantic_model(
        self,
        profile: Dict[str, Any]
    ) -> str:

        import json

        numeric_columns = profile.get(
            "numeric_columns",
            []
        )

        categorical_columns = profile.get(
            "categorical_columns",
            []
        )

        date_columns = profile.get(
            "date_columns",
            []
        )

        columns = []

        # -------------------------------------------------
        # Numeric columns
        # -------------------------------------------------

        for column in numeric_columns:

            columns.append({
                "name": column,
                "data_type": "numeric"
            })

        # -------------------------------------------------
        # Categorical columns
        # -------------------------------------------------

        for column in categorical_columns:

            columns.append({
                "name": column,
                "data_type": "text"
            })

        # -------------------------------------------------
        # Date columns
        # -------------------------------------------------

        for column in date_columns:

            columns.append({
                "name": column,
                "data_type": "date"
            })

        model = {
            "semantic_model": {
                "tables": [
                    {
                        "name": "Dataset",
                        "columns": columns
                    }
                ]
            }
        }

        return json.dumps(
            model,
            indent=4
        )

    # =====================================================
    # REPORT METADATA
    # =====================================================

    def _generate_report_metadata(
        self,
        dashboard_title: str
    ) -> str:

        import json

        metadata = {
            "name": dashboard_title,
            "type": "report",
            "generated_by": "Prompt-Driven AI Agent"
        }

        return json.dumps(
            metadata,
            indent=4
        )

    # =====================================================
    # MODEL METADATA
    # =====================================================

    def _generate_model_metadata(
        self,
        project_name: str
    ) -> str:

        import json

        metadata = {
            "name": project_name,
            "type": "semantic_model",
            "generated_by": "Prompt-Driven AI Agent"
        }

        return json.dumps(
            metadata,
            indent=4
        )