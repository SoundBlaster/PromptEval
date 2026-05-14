import shutil
import tempfile
from pathlib import Path

from prompt_eval.fsd_check import check_fsd_structure


def _make_tree(files: dict[str, str]) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="peval-fsd-test-"))
    for rel, content in files.items():
        target = tmp / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    return tmp


def _by_name(results, name):
    return next(r for r in results if r.name == name)


def test_clean_fsd_layout_passes_all_rules():
    tree = _make_tree(
        {
            "src/shared/api/index.ts": "export {}\n",
            "src/entities/user/index.ts": "export {}\n",
            "src/entities/user/ui/badge.tsx": "import { httpGet } from '@/shared/api';\n",
            "src/features/login/index.ts": "export {}\n",
            "src/features/login/ui/form.tsx": "import { httpGet } from '@/shared/api';\nimport { Badge } from '@/entities/user';\n",
            "src/pages/auth/index.ts": "export {}\n",
            "src/pages/auth/ui/page.tsx": "import { LoginForm } from '@/features/login';\n",
        }
    )
    try:
        results = check_fsd_structure(tree)
        for r in results:
            assert r.passed, f"{r.name} failed: {r.detail}"
    finally:
        shutil.rmtree(tree, ignore_errors=True)


def test_upward_import_is_flagged():
    tree = _make_tree(
        {
            "src/entities/user/ui/badge.tsx": "import { LoginForm } from '@/features/login';\n",
            "src/features/login/index.ts": "export {}\n",
            "src/features/login/ui/form.tsx": "export const F = 1;\n",
        }
    )
    try:
        results = check_fsd_structure(tree)
        layer = _by_name(results, "fsd_structure:layer_hierarchy")
        assert not layer.passed
        assert "upper layer" in layer.detail
    finally:
        shutil.rmtree(tree, ignore_errors=True)


def test_sibling_slice_import_is_flagged():
    tree = _make_tree(
        {
            "src/features/like-post/ui/btn.tsx": (
                "import { ActionButton } from '@/features/send-comment/ui/button';\n"
            ),
            "src/features/send-comment/ui/button.tsx": "export const ActionButton = 1;\n",
        }
    )
    try:
        results = check_fsd_structure(tree)
        layer = _by_name(results, "fsd_structure:layer_hierarchy")
        assert not layer.passed
        assert "sibling slice" in layer.detail
    finally:
        shutil.rmtree(tree, ignore_errors=True)


def test_public_api_bypass_is_flagged():
    tree = _make_tree(
        {
            "src/entities/product/index.ts": "export {}\n",
            "src/entities/product/model/product.ts": "export const x = 1;\n",
            "src/widgets/grid/ui/grid.tsx": "import { x } from '@/entities/product/model/product';\n",
        }
    )
    try:
        results = check_fsd_structure(tree)
        api = _by_name(results, "fsd_structure:public_api")
        assert not api.passed
        assert "bypasses public API" in api.detail
    finally:
        shutil.rmtree(tree, ignore_errors=True)


def test_same_slice_internal_imports_allowed():
    tree = _make_tree(
        {
            "src/features/login/index.ts": "export {}\n",
            "src/features/login/ui/form.tsx": "import { useLogin } from '../model/use-login';\n",
            "src/features/login/model/use-login.ts": "export const useLogin = () => null;\n",
        }
    )
    try:
        results = check_fsd_structure(tree)
        for r in results:
            assert r.passed, f"{r.name} failed: {r.detail}"
    finally:
        shutil.rmtree(tree, ignore_errors=True)


def test_forbidden_segment_name_is_flagged():
    tree = _make_tree(
        {
            "src/features/login/components/form.tsx": "export const F = 1;\n",
            "src/features/login/index.ts": "export {}\n",
        }
    )
    try:
        results = check_fsd_structure(tree)
        seg = _by_name(results, "fsd_structure:segment_names")
        assert not seg.passed
        assert "components" in seg.detail
    finally:
        shutil.rmtree(tree, ignore_errors=True)


def test_cross_entity_x_import_is_allowed():
    tree = _make_tree(
        {
            "src/entities/user/@x/order.ts": "export type UserSummary = { id: string };\n",
            "src/entities/order/model/order.ts": "import type { UserSummary } from '@/entities/user/@x/order';\n",
            "src/entities/order/index.ts": "export {}\n",
            "src/entities/user/index.ts": "export {}\n",
        }
    )
    try:
        results = check_fsd_structure(tree)
        for r in results:
            assert r.passed, f"{r.name} failed unexpectedly: {r.detail}"
    finally:
        shutil.rmtree(tree, ignore_errors=True)


def test_no_fsd_layers_present_is_flagged():
    tree = _make_tree(
        {
            "src/components/Card.tsx": "export const Card = 1;\n",
            "src/hooks/use-thing.ts": "export const useThing = () => 0;\n",
            "src/services/api.ts": "export const api = 1;\n",
            "src/main.tsx": "import { Card } from './components/Card';\n",
        }
    )
    try:
        results = check_fsd_structure(tree)
        layers = _by_name(results, "fsd_structure:layers_present")
        assert not layers.passed
        assert "no FSD layer" in layers.detail
    finally:
        shutil.rmtree(tree, ignore_errors=True)


def test_missing_src_returns_failed_result():
    tmp = Path(tempfile.mkdtemp(prefix="peval-fsd-test-"))
    try:
        results = check_fsd_structure(tmp)
        assert len(results) == 1
        assert not results[0].passed
        assert "no src" in results[0].detail
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
