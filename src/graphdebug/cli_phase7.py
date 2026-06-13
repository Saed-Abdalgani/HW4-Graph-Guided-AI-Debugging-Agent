"""Phase 7 CLI (keeps ``cli_handlers`` under the line budget)."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def run_phase7_cli(args: argparse.Namespace) -> None:
    from graphdebug.sdk.api import (
        apply_approved_patch,
        capture_after_knowledge_snapshot,
        merge_bug_analysis_report,
        review_patch_for_symptom_masks,
        run_phase7_verification,
        scaffold_patch_comparison,
        write_vault_knowledge_delta,
    )

    root = (args.project_root or Path.cwd()).resolve()
    step = args.p7_step
    if step == "review-patch":
        if not args.diff:
            raise SystemExit("phase7 review-patch requires --diff")
        text = Path(args.diff).read_text(encoding="utf-8")
        r = review_patch_for_symptom_masks(text)
        print("phase7 review-patch:", f"ok={r.ok}", f"warnings={list(r.warnings)}")
    elif step == "apply":
        if not args.diff or not args.target_root:
            raise SystemExit("phase7 apply requires --diff and --target-root")
        out = apply_approved_patch(
            Path(args.diff),
            Path(args.target_root),
            project_root=root,
        )
        print("phase7 apply:", f"saved={out}")
    elif step == "verify":
        if not args.target_root or not args.tests:
            raise SystemExit("phase7 verify requires --target-root and at least one --test")
        tests = tuple(args.tests) if args.tests else ()
        res = run_phase7_verification(
            Path(args.target_root),
            tests,
            project_root=root,
            baseline_red=Path(args.baseline_red) if args.baseline_red else None,
            suite_args=tuple(args.suite_args) if args.suite_args else (),
        )
        print(
            "phase7 verify:",
            f"target_passed={res.target_tests_passed}",
            f"new_failures={list(res.new_failures_vs_baseline)}",
            f"green={res.baseline_green_path}",
        )
    elif step == "snapshot-after":
        p = capture_after_knowledge_snapshot(project_root=root)
        print("phase7 snapshot-after:", p)
    elif step == "vault-diff":
        p = write_vault_knowledge_delta(project_root=root)
        print("phase7 vault-diff:", p)
    elif step == "patch-compare":
        if not args.ours or not args.official:
            raise SystemExit("phase7 patch-compare requires --ours and --official")
        p = scaffold_patch_comparison(
            Path(args.ours),
            Path(args.official),
            project_root=root,
        )
        print("phase7 patch-compare:", p)
    elif step == "merge-docs":
        hyp = (
            Path(args.hypothesis_file).read_text(encoding="utf-8")
            if args.hypothesis_file
            else ""
        )
        fix = Path(args.fix_file).read_text(encoding="utf-8") if args.fix_file else ""
        ver = (
            Path(args.verification_file).read_text(encoding="utf-8")
            if args.verification_file
            else ""
        )
        p = merge_bug_analysis_report(
            hypothesis=hyp or args.hypothesis_inline,
            fix_summary=fix or args.fix_inline,
            verification=ver or args.verification_inline,
            project_root=root,
        )
        print("phase7 merge-docs:", p)
    else:
        raise SystemExit(f"unknown phase7 step: {step}")


def add_phase7_parser(subparsers: Any) -> None:
    p7 = subparsers.add_parser(
        "phase7",
        help="Apply patch, pytest verify, vault snapshots (Phase 7 / M4).",
    )
    p7.add_argument(
        "p7_step",
        choices=(
            "review-patch",
            "apply",
            "verify",
            "snapshot-after",
            "vault-diff",
            "patch-compare",
            "merge-docs",
        ),
        help="Workflow step.",
    )
    p7.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="graphdebug repo root (default: cwd).",
    )
    p7.add_argument("--diff", type=Path, default=None, help="Unified diff file.")
    p7.add_argument("--target-root", type=Path, default=None, help="Subject repo root.")
    p7.add_argument(
        "--test",
        action="append",
        dest="tests",
        metavar="NODEID",
        help="Pytest node id (repeatable); used with verify.",
    )
    p7.add_argument("--baseline-red", type=Path, default=None, help="Full suite red log.")
    p7.add_argument(
        "--suite-arg",
        action="append",
        dest="suite_args",
        help="Extra pytest args for full suite (default: '.').",
    )
    p7.add_argument("--ours", type=Path, default=None, help="Our patch file.")
    p7.add_argument("--official", type=Path, default=None, help="Official / upstream patch.")
    p7.add_argument("--hypothesis-file", type=Path, default=None)
    p7.add_argument("--fix-file", type=Path, default=None)
    p7.add_argument("--verification-file", type=Path, default=None)
    p7.add_argument("--hypothesis-inline", default="", help="Short text if no file.")
    p7.add_argument("--fix-inline", default="")
    p7.add_argument("--verification-inline", default="")


__all__ = ["add_phase7_parser", "run_phase7_cli"]
