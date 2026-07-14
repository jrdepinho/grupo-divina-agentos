from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app.project_intelligence.dispatcher import dispatch_capability, list_capabilities
from app.project_intelligence.planner import build_project_intelligence_plan
from app.project_intelligence.scanners import (
    generate_architecture,
    scan_backend,
    scan_database,
    scan_frontend,
    scan_memory,
    scan_project,
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class ProjectIntelligenceTests(unittest.TestCase):
    def build_sample_project(self, root: Path) -> None:
        write(
            root / "package.json",
            json.dumps({"dependencies": {"next": "15.0.0", "react": "19.0.0", "@supabase/supabase-js": "2.0.0"}}),
        )
        write(root / "README.md", "# Sample\n\nTODO: documentar fluxo comercial\n")
        write(root / "app/page.jsx", "export default function Page() { return <main />; }\n")
        write(root / "app/components/Card.jsx", "export function Card() { return null; }\n")
        write(root / "app/api/orders/route.js", "export async function GET() { return Response.json({ ok: true }); }\n")
        write(
            root / "backend/api.py",
            "from fastapi import FastAPI\napp = FastAPI()\n@app.post('/orders')\ndef create_order():\n    pass\n",
        )
        write(root / "backend/services/order_service.py", "# NOTE: regra comercial pendente\n")
        write(
            root / "migrations/001_create_orders.sql",
            "create table customers (id int primary key);\n"
            "create table orders (id int primary key, customer_id int, foreign key(customer_id) references customers(id));\n"
            "create index idx_orders_customer on orders(customer_id);\n",
        )

    def test_scanners_detect_project_layers(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_sample_project(root)

            project = scan_project(str(root))
            frontend = scan_frontend(str(root))
            backend = scan_backend(str(root))
            database = scan_database(str(root))
            memory = scan_memory(str(root))

            self.assertEqual(project["capability"], "project.scan")
            self.assertGreaterEqual(project["modules_found"], 2)
            self.assertIn("Next", frontend["frameworks"])
            self.assertIn("FastAPI", backend["frameworks"])
            self.assertIn("Supabase", database["orm"])
            self.assertIn("orders", database["tables"])
            self.assertTrue(any(item["marker"] == "TODO" for item in memory["markers"]))

    def test_goal_planner_builds_project_intelligence_sequence(self) -> None:
        plan = build_project_intelligence_plan("Analise o módulo Comercial")

        self.assertTrue(plan["triggered"])
        self.assertEqual(plan["module"], "Comercial")
        self.assertEqual([step["capability"] for step in plan["plan"]][0], "context.build")
        self.assertEqual([step["capability"] for step in plan["plan"]][-1], "architecture.generate")
        self.assertEqual(plan["scan_sequence"][0], "project.scan")

    def test_dispatcher_and_architecture_generation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_sample_project(root)

            capabilities = {item["name"] for item in list_capabilities()}
            self.assertIn("project.scan", capabilities)
            self.assertIn("context.build", capabilities)
            self.assertIn("architecture.generate", capabilities)

            context = dispatch_capability("context.build", {"path": str(root), "module": "Comercial"})
            dispatched = dispatch_capability("architecture.generate", {"path": str(root), "module": "Comercial"})
            direct = generate_architecture(str(root), module="Comercial")

            self.assertTrue(context["ok"])
            self.assertIn("project_context", context["result"])
            self.assertTrue(dispatched["ok"])
            self.assertIn("markdown", dispatched["result"])
            self.assertIn("Roadmap sugerido", direct["markdown"])


if __name__ == "__main__":
    unittest.main()
