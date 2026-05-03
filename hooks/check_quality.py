#!/usr/bin/env python3
"""Quality scoring for knowledge base JSON files.

Usage:
    python hooks/check_quality.py <json_file> [json_file2 ...]

Examples:
    # Single file
    python hooks/check_quality.py knowledge/articles/2025-05-03_articles.json

    # Multiple files with glob pattern
    python hooks/check_quality.py knowledge/articles/*.json
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union


@dataclass
class DimensionScore:
    score: float
    max_score: float
    details: str


@dataclass
class QualityReport:
    file_path: Path
    article_id: str
    dimensions: dict[str, DimensionScore]
    total_score: float
    grade: str


BUZZWORDS_CN = [
    "赋能",
    "抓手",
    "闭环",
    "打通",
    "全链路",
    "底层逻辑",
    "颗粒度",
    "对齐",
    "拉通",
    "沉淀",
    "强大的",
    "革命性的",
]

BUZZWORDS_EN = [
    "groundbreaking",
    "revolutionary",
    "game-changing",
    "cutting-edge",
    "industry-leading",
    "best-in-class",
    "world-class",
    "state-of-the-art",
    "next-generation",
    "paradigm-shifting",
]

TECH_KEYWORDS = [
    "api",
    "sdk",
    "framework",
    "library",
    "algorithm",
    "model",
    "neural",
    "transformer",
    "embedding",
    "vector",
    "agent",
    "llm",
    "gpt",
    "claude",
    "openai",
    "pytorch",
    "tensorflow",
    "docker",
    "kubernetes",
    "microservice",
    "architecture",
    "pipeline",
    "workflow",
    "orchestration",
    "rag",
    "fine-tuning",
    "inference",
    "training",
    "deployment",
]

VALID_TAGS = {
    "ai",
    "agent",
    "llm",
    "ml",
    "nlp",
    "cv",
    "computer-vision",
    "deep-learning",
    "machine-learning",
    "neural-network",
    "transformer",
    "gpt",
    "openai",
    "claude",
    "pytorch",
    "tensorflow",
    "docker",
    "kubernetes",
    "api",
    "sdk",
    "framework",
    "library",
    "tool",
    "tutorial",
    "research",
    "paper",
    "arxiv",
    "github",
    "opensource",
    "python",
    "javascript",
    "typescript",
    "rust",
    "go",
    "java",
    "cpp",
    "database",
    "vector-db",
    "rag",
    "fine-tuning",
    "inference",
    "training",
    "deployment",
    "mlops",
    "devops",
    "security",
    "privacy",
    "ethics",
    "benchmark",
    "evaluation",
    "dataset",
    "model",
    "embedding",
    "prompt",
    "prompt-engineering",
    "langchain",
    "autogpt",
    "chatbot",
    "assistant",
    "automation",
    "workflow",
    "orchestration",
}


def score_summary_quality(summary: str) -> DimensionScore:
    max_score = 25.0
    score = 0.0
    reasons = []

    length = len(summary)

    if length >= 50:
        score += 15
        reasons.append(f"长度优秀({length}字)")
    elif length >= 20:
        score += 10
        reasons.append(f"长度合格({length}字)")
    else:
        score += max(0, length // 4)
        reasons.append(f"长度不足({length}字)")

    summary_lower = summary.lower()
    keyword_count = sum(1 for kw in TECH_KEYWORDS if kw in summary_lower)

    if keyword_count >= 3:
        score += 10
        reasons.append(f"技术关键词丰富({keyword_count}个)")
    elif keyword_count >= 1:
        score += 5
        reasons.append(f"含技术关键词({keyword_count}个)")

    score = min(score, max_score)

    return DimensionScore(
        score=score,
        max_score=max_score,
        details="; ".join(reasons),
    )


def score_technical_depth(article_score: Any) -> DimensionScore:
    max_score = 25.0

    if article_score is None:
        return DimensionScore(
            score=0,
            max_score=max_score,
            details="无 score 字段",
        )

    if not isinstance(article_score, (int, float)):
        return DimensionScore(
            score=0,
            max_score=max_score,
            details=f"score 类型错误: {type(article_score).__name__}",
        )

    normalized = min(max(article_score, 1), 10)
    score = (normalized / 10) * max_score

    return DimensionScore(
        score=score,
        max_score=max_score,
        details=f"score={article_score} → {score:.1f}分",
    )


def score_format_compliance(data: dict[str, Any]) -> DimensionScore:
    max_score = 20.0
    score = 0.0
    reasons = []

    checks = [
        ("id", lambda v: isinstance(v, str) and re.match(r"^[a-z]+-\d{8}-\d{3}$", v)),
        ("title", lambda v: isinstance(v, str) and len(v) >= 5),
        ("source_url", lambda v: isinstance(v, str) and v.startswith(("http://", "https://"))),
        ("status", lambda v: isinstance(v, str) and v in {"draft", "review", "published", "archived"}),
    ]

    for field_name, validator in checks:
        if field_name in data:
            try:
                if validator(data[field_name]):
                    score += 4
                    reasons.append(f"{field_name}✓")
                else:
                    reasons.append(f"{field_name}格式错误")
            except Exception:
                reasons.append(f"{field_name}校验失败")
        else:
            reasons.append(f"{field_name}缺失")

    timestamp_fields = ["created_at", "updated_at", "published_at"]
    has_timestamp = any(
        f in data and isinstance(data[f], str) and "T" in data[f]
        for f in timestamp_fields
    )
    if has_timestamp:
        score += 4
        reasons.append("时间戳✓")
    else:
        reasons.append("时间戳缺失")

    return DimensionScore(
        score=score,
        max_score=max_score,
        details="; ".join(reasons),
    )


def score_tag_precision(tags: Any) -> DimensionScore:
    max_score = 15.0
    score = 0.0
    reasons = []

    if tags is None:
        return DimensionScore(
            score=0,
            max_score=max_score,
            details="无 tags 字段",
        )

    if not isinstance(tags, list):
        return DimensionScore(
            score=0,
            max_score=max_score,
            details=f"tags 类型错误: {type(tags).__name__}",
        )

    tag_count = len(tags)

    if tag_count == 0:
        return DimensionScore(
            score=0,
            max_score=max_score,
            details="标签数量为 0",
        )

    valid_tags = [t for t in tags if isinstance(t, str) and t.lower() in VALID_TAGS]
    invalid_tags = [t for t in tags if not isinstance(t, str) or t.lower() not in VALID_TAGS]

    if 1 <= tag_count <= 3:
        score += 10
        reasons.append(f"标签数量适中({tag_count}个)")
    elif tag_count >= 4:
        score += 5
        reasons.append(f"标签数量偏多({tag_count}个)")

    if valid_tags:
        ratio = len(valid_tags) / tag_count
        score += 5 * ratio
        reasons.append(f"标准标签{len(valid_tags)}/{tag_count}")

    if invalid_tags:
        reasons.append(f"非标准标签: {invalid_tags[:3]}")

    return DimensionScore(
        score=score,
        max_score=max_score,
        details="; ".join(reasons),
    )


def score_buzzword_detection(text: str) -> DimensionScore:
    max_score = 15.0
    score = max_score
    reasons = []

    text_lower = text.lower()

    found_cn = [w for w in BUZZWORDS_CN if w in text]
    found_en = [w for w in BUZZWORDS_EN if w in text_lower]

    total_buzzwords = len(found_cn) + len(found_en)

    if total_buzzwords == 0:
        reasons.append("无空洞词")
    else:
        deduction = min(total_buzzwords * 3, max_score)
        score -= deduction

        if found_cn:
            reasons.append(f"中文空洞词: {found_cn}")
        if found_en:
            reasons.append(f"英文空洞词: {found_en}")

    return DimensionScore(
        score=max(0, score),
        max_score=max_score,
        details="; ".join(reasons),
    )


def calculate_grade(total_score: float) -> str:
    if total_score >= 80:
        return "A"
    elif total_score >= 60:
        return "B"
    else:
        return "C"


def check_quality(data: dict[str, Any], file_path: Path) -> QualityReport:
    dimensions: dict[str, DimensionScore] = {}

    summary = data.get("summary", "")
    text_to_check = f"{summary} {data.get('title', '')} {data.get('description', '')}"

    dimensions["摘要质量"] = score_summary_quality(summary)
    dimensions["技术深度"] = score_technical_depth(data.get("score"))
    dimensions["格式规范"] = score_format_compliance(data)
    dimensions["标签精度"] = score_tag_precision(data.get("tags"))
    dimensions["空洞词检测"] = score_buzzword_detection(text_to_check)

    total_score = sum(d.score for d in dimensions.values())
    grade = calculate_grade(total_score)

    return QualityReport(
        file_path=file_path,
        article_id=data.get("id", "unknown"),
        dimensions=dimensions,
        total_score=total_score,
        grade=grade,
    )


def draw_progress_bar(score: float, max_score: float, width: int = 20) -> str:
    ratio = score / max_score if max_score > 0 else 0
    filled = int(ratio * width)
    empty = width - filled

    bar = "█" * filled + "░" * empty
    return f"[{bar}] {score:5.1f}/{max_score:.0f}"


def print_report(report: QualityReport) -> None:
    print(f"\n{'=' * 70}")
    print(f"文件: {report.file_path}")
    print(f"ID:   {report.article_id}")
    print(f"{'=' * 70}")

    for dim_name, dim_score in report.dimensions.items():
        bar = draw_progress_bar(dim_score.score, dim_score.max_score)
        print(f"{dim_name:12} {bar}  {dim_score.details}")

    print(f"{'-' * 70}")
    total_bar = draw_progress_bar(report.total_score, 100)
    print(f"{'总分':12} {total_bar}")

    grade_color = {"A": "🟢", "B": "🟡", "C": "🔴"}
    print(f"{'等级':12} {grade_color.get(report.grade, '⚪')} {report.grade}")
    print(f"{'=' * 70}\n")


def load_json_file(file_path: Path) -> tuple[Optional[Any], Optional[str]]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"JSON 解析错误: {e}"
    except Exception as e:
        return None, f"文件读取错误: {e}"


def expand_file_patterns(patterns: list[str]) -> list[Path]:
    files = []
    for pattern in patterns:
        path = Path(pattern)
        if path.exists():
            files.append(path)
        else:
            parent = path.parent if path.parent.exists() else Path(".")
            matched = list(parent.glob(path.name))
            if matched:
                files.extend(sorted(matched))
            else:
                print(f"Warning: No files match pattern: {pattern}", file=sys.stderr)

    return files


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python hooks/check_quality.py <json_file> [json_file2 ...]")
        return 1

    files = expand_file_patterns(sys.argv[1:])

    if not files:
        print("Error: No files to check", file=sys.stderr)
        return 1

    all_reports: list[QualityReport] = []
    grade_c_count = 0

    for file_path in files:
        data, error = load_json_file(file_path)

        if error:
            print(f"Error loading {file_path}: {error}", file=sys.stderr)
            continue

        if isinstance(data, dict):
            report = check_quality(data, file_path)
            all_reports.append(report)
            if report.grade == "C":
                grade_c_count += 1
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                if isinstance(item, dict):
                    report = check_quality(item, file_path)
                    report.article_id = f"[{idx}] {report.article_id}"
                    all_reports.append(report)
                    if report.grade == "C":
                        grade_c_count += 1

    for report in all_reports:
        print_report(report)

    print(f"\n{'=' * 70}")
    print(f"质量检查汇总")
    print(f"{'=' * 70}")
    print(f"检查文件: {len(files)} 个")
    print(f"知识条目: {len(all_reports)} 个")

    grade_counts = {"A": 0, "B": 0, "C": 0}
    for r in all_reports:
        grade_counts[r.grade] += 1

    print(f"\n等级分布:")
    print(f"  🟢 A 级 (≥80分): {grade_counts['A']} 个")
    print(f"  🟡 B 级 (≥60分): {grade_counts['B']} 个")
    print(f"  🔴 C 级 (<60分): {grade_counts['C']} 个")

    avg_score = sum(r.total_score for r in all_reports) / len(all_reports) if all_reports else 0
    print(f"\n平均得分: {avg_score:.1f} 分")
    print(f"{'=' * 70}\n")

    if grade_c_count > 0:
        print(f"⚠️  发现 {grade_c_count} 个 C 级条目，建议优化")
        return 1
    else:
        print("✅ 所有条目质量合格")
        return 0


if __name__ == "__main__":
    sys.exit(main())
