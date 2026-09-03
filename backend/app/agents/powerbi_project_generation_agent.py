import json
import re
from typing import Any, Dict, List


class PowerBIProjectGenerationAgent:
    """
    Generates a Power BI Project (PBIP) structure.

    Target structure:

        Project/
        ├── Project.pbip
        ├── Project.Report/
        │   ├── definition.pbir
        │   └── definition/
        │       └── pages/
        │           └── Overview/
        │               ├── page.json
        │               └── visuals/
        │                   ├── ...
        │
        └── Project.SemanticModel/
            ├── definition.pbism
            └── definition/
                ├── database.tmdl
                ├── model.tmdl
                └── tables/
                    └── Dataset.tmdl

    Note:
    This generates a structured PBIP-oriented project.
    Power BI Desktop compatibility still needs to be
    validated against the exact PBIP/PBIR/TMDL schemas.
    """

    def __init__(self):
        pass

    # ==========================================================
    # PUBLIC METHOD
    # ==========================================================

    def generate(
        self,
        profile: Dict[str, Any],
        dashboard: Dict[str, Any]
    ) -> Dict[str, Any]:

        dashboard_title = dashboard.get(
            "dashboard_title",
            "AI Generated Dashboard"
        )

        pages = dashboard.get("pages", [])

        project_name = self._create_project_name(
            dashboard_title
        )

        files: List[Dict[str, Any]] = []

        # ------------------------------------------------------
        # 1. PBIP PROJECT FILE
        # ------------------------------------------------------

        files.append({
            "path": f"{project_name}.pbip",
            "content": self._generate_pbip_file(
                project_name
            )
        })

        # ------------------------------------------------------
        # 2. REPORT DEFINITION
        # ------------------------------------------------------

        files.append({
            "path": (
                f"{project_name}.Report/"
                "definition.pbir"
            ),
            "content": self._generate_definition_pbir(
                project_name
            )
        })

        # ------------------------------------------------------
        # 3. REPORT PAGES + VISUALS
        # ------------------------------------------------------

        report_files = self._generate_report_files(
            project_name,
            pages
        )

        files.extend(report_files)

        # ------------------------------------------------------
        # 4. SEMANTIC MODEL DEFINITION
        # ------------------------------------------------------

        files.append({
            "path": (
                f"{project_name}.SemanticModel/"
                "definition.pbism"
            ),
            "content": self._generate_definition_pbism()
        })

        # ------------------------------------------------------
        # 5. TMDL SEMANTIC MODEL
        # ------------------------------------------------------

        semantic_files = self._generate_tmdl_files(
            project_name,
            profile
        )

        files.extend(semantic_files)

        # ------------------------------------------------------
        # RETURN
        # ------------------------------------------------------

        return {
            "project_name": project_name,
            "project_type": "Power BI Project",
            "status": "generated",
            "files": files
        }

    # ==========================================================
    # PROJECT NAME
    # ==========================================================

    def _create_project_name(
        self,
        dashboard_title: str
    ) -> str:

        name = dashboard_title.strip()

        if not name:
            name = "AI_Generated_Dashboard"

        name = re.sub(
            r"[^a-zA-Z0-9_]+",
            "_",
            name
        )

        name = re.sub(
            r"_+",
            "_",
            name
        )

        name = name.strip("_")

        if not name:
            name = "AI_Generated_Dashboard"

        return name

    # ==========================================================
    # PBIP
    # ==========================================================

    def _generate_pbip_file(
        self,
        project_name: str
    ) -> str:

        pbip = {
            "version": "1.0",
            "artifacts": [
                {
                    "report": {
                        "path": (
                            f"{project_name}.Report"
                        )
                    }
                }
            ]
        }

        return json.dumps(
            pbip,
            indent=4
        )

    # ==========================================================
    # DEFINITION.PBIR
    # ==========================================================

    def _generate_definition_pbir(
        self,
        project_name: str
    ) -> str:

        definition = {
            "$schema": (
                "https://developer.microsoft.com/"
                "json-schemas/fabric/item/"
                "report/definitionProperties/"
                "2.0.0/schema.json"
            ),
            "version": "4.0",
            "datasetReference": {
                "byPath": {
                    "path": (
                        f"../{project_name}"
                        ".SemanticModel"
                    )
                }
            }
        }

        return json.dumps(
            definition,
            indent=4
        )

    # ==========================================================
    # REPORT FILES
    # ==========================================================

    def _generate_report_files(
        self,
        project_name: str,
        pages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        files: List[Dict[str, Any]] = []

        if not pages:
            pages = [{
                "page_number": 1,
                "page_name": "Overview",
                "purpose": (
                    "AI generated dashboard overview."
                ),
                "visuals": []
            }]

        for page_index, page in enumerate(
            pages,
            start=1
        ):

            page_name = page.get(
                "page_name",
                f"Page {page_index}"
            )

            page_folder_name = (
                self._safe_folder_name(page_name)
            )

            page_path = (
                f"{project_name}.Report/"
                f"definition/pages/"
                f"{page_folder_name}"
            )

            # --------------------------------------------------
            # PAGE JSON
            # --------------------------------------------------

            page_definition = {
                "name": page_folder_name,
                "displayName": page_name,
                "width": 1280,
                "height": 720
            }

            files.append({
                "path": (
                    f"{page_path}/page.json"
                ),
                "content": json.dumps(
                    page_definition,
                    indent=4
                )
            })

            # --------------------------------------------------
            # VISUALS
            # --------------------------------------------------

            visuals = page.get(
                "visuals",
                []
            )

            for visual_index, visual in enumerate(
                visuals,
                start=1
            ):

                visual_id = visual.get(
                    "visual_id",
                    f"visual_{visual_index}"
                )

                visual_folder = (
                    self._safe_folder_name(
                        str(visual_id)
                    )
                )

                visual_definition = (
                    self._generate_visual_definition(
                        visual,
                        visual_id
                    )
                )

                files.append({
                    "path": (
                        f"{page_path}/"
                        f"visuals/"
                        f"{visual_folder}/"
                        "visual.json"
                    ),
                    "content": json.dumps(
                        visual_definition,
                        indent=4
                    )
                })

        return files

    # ==========================================================
    # VISUAL DEFINITION
    # ==========================================================

    def _generate_visual_definition(
        self,
        visual: Dict[str, Any],
        visual_id: str
    ) -> Dict[str, Any]:

        visual_type = visual.get(
            "visual_type",
            visual.get(
                "type",
                "chart"
            )
        )

        title = visual.get(
            "title",
            "AI Generated Visual"
        )

        position = visual.get(
            "position",
            {
                "x": 0,
                "y": 0,
                "width": 400,
                "height": 250
            }
        )

        configuration = visual.get(
            "configuration",
            {}
        )

        return {
            "id": visual_id,
            "visualType": visual_type,
            "name": title,
            "position": position,
            "configuration": configuration
        }

    # ==========================================================
    # SEMANTIC MODEL
    # ==========================================================

    def _generate_definition_pbism(self) -> str:

        definition = {
            "$schema": (
                "https://developer.microsoft.com/"
                "json-schemas/fabric/item/"
                "semanticModel/definitionProperties/"
                "2.0.0/schema.json"
            ),
            "version": 4
        }

        return json.dumps(
            definition,
            indent=4
        )

    # ==========================================================
    # TMDL FILES
    # ==========================================================

    def _generate_tmdl_files(
        self,
        project_name: str,
        profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        files: List[Dict[str, Any]] = []

        base_path = (
            f"{project_name}.SemanticModel/"
            "definition"
        )

        # ------------------------------------------------------
        # DATABASE.TMDL
        # ------------------------------------------------------

        database_tmdl = self._generate_database_tmdl()

        files.append({
            "path": (
                f"{base_path}/database.tmdl"
            ),
            "content": database_tmdl
        })

        # ------------------------------------------------------
        # MODEL.TMDL
        # ------------------------------------------------------

        model_tmdl = self._generate_model_tmdl()

        files.append({
            "path": (
                f"{base_path}/model.tmdl"
            ),
            "content": model_tmdl
        })

        # ------------------------------------------------------
        # DATASET TABLE
        # ------------------------------------------------------

        table_tmdl = self._generate_dataset_table_tmdl(
            profile
        )

        files.append({
            "path": (
                f"{base_path}/tables/"
                "Dataset.tmdl"
            ),
            "content": table_tmdl
        })

        return files

    # ==========================================================
    # DATABASE.TMDL
    # ==========================================================

    def _generate_database_tmdl(self) -> str:

        return """database
    compatibilityLevel: 1600
"""

    # ==========================================================
    # MODEL.TMDL
    # ==========================================================

    def _generate_model_tmdl(self) -> str:

        return """model Model
    culture: en-US
"""

    # ==========================================================
    # DATASET.TMDL
    # ==========================================================

    def _generate_dataset_table_tmdl(
        self,
        profile: Dict[str, Any]
    ) -> str:

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

        lines: List[str] = []

        lines.append(
            "table Dataset"
        )

        lines.append(
            "    lineageTag: "
            "00000000-0000-0000-0000-000000000001"
        )

        lines.append("")

        # ------------------------------------------------------
        # NUMERIC COLUMNS
        # ------------------------------------------------------

        for index, column in enumerate(
            numeric_columns,
            start=1
        ):

            safe_column = self._safe_tmdl_name(
                column
            )

            lines.append(
                f"    column {safe_column}"
            )

            lines.append(
                "        dataType: double"
            )

            lines.append(
                "        summarizeBy: sum"
            )

            lines.append(
                f"        lineageTag: "
                f"00000000-0000-0000-0000-"
                f"{index:012d}"
            )

            lines.append("")

        # ------------------------------------------------------
        # TEXT COLUMNS
        # ------------------------------------------------------

        for index, column in enumerate(
            categorical_columns,
            start=100
        ):

            safe_column = self._safe_tmdl_name(
                column
            )

            lines.append(
                f"    column {safe_column}"
            )

            lines.append(
                "        dataType: string"
            )

            lines.append(
                "        summarizeBy: none"
            )

            lines.append(
                f"        lineageTag: "
                f"00000000-0000-0000-0000-"
                f"{index:012d}"
            )

            lines.append("")

        # ------------------------------------------------------
        # DATE COLUMNS
        # ------------------------------------------------------

        for index, column in enumerate(
            date_columns,
            start=200
        ):

            safe_column = self._safe_tmdl_name(
                column
            )

            lines.append(
                f"    column {safe_column}"
            )

            lines.append(
                "        dataType: dateTime"
            )

            lines.append(
                "        summarizeBy: none"
            )

            lines.append(
                f"        lineageTag: "
                f"00000000-0000-0000-0000-"
                f"{index:012d}"
            )

            lines.append("")

        return "\n".join(lines)

    # ==========================================================
    # SAFE FOLDER NAME
    # ==========================================================

    def _safe_folder_name(
        self,
        value: str
    ) -> str:

        value = value.strip()

        value = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            value
        )

        value = re.sub(
            r"_+",
            "_",
            value
        )

        value = value.strip("_")

        if not value:
            return "Unnamed"

        return value

    # ==========================================================
    # SAFE TMDL NAME
    # ==========================================================

    def _safe_tmdl_name(
        self,
        value: str
    ) -> str:

        value = str(value).strip()

        value = re.sub(
            r"[^a-zA-Z0-9_]+",
            "_",
            value
        )

        value = value.strip("_")

        if not value:
            return "Column"

        return value