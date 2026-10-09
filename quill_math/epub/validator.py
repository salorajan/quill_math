"""EPUB Accessibility 1.2 and MathML validator."""

from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from quill_math.core.mathml import is_valid_mathml


@dataclass
class ValidationIssue:
    severity: str  # "error", "warning", "info"
    message: str
    location: str = ""


@dataclass
class ValidationReport:
    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def validate_epub(epub_path: Path) -> ValidationReport:
    """Audit an EPUB package for accessibility and MathML standard compliance."""
    issues: list[ValidationIssue] = []
    path = Path(epub_path)

    if not path.is_file():
        return ValidationReport(
            is_valid=False,
            issues=[ValidationIssue(severity="error", message=f"File not found: {path}")],
        )

    try:
        with zipfile.ZipFile(path, "r") as archive:
            namelist = archive.namelist()

            # 1. mimetype check
            if "mimetype" not in namelist:
                issues.append(ValidationIssue(severity="error", message="Missing 'mimetype' file."))
            else:
                first_file = archive.infolist()[0]
                if first_file.filename != "mimetype" or first_file.compress_type != zipfile.ZIP_STORED:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message="'mimetype' must be the first file and uncompressed (ZIP_STORED).",
                        )
                    )

            # 2. container check
            if "META-INF/container.xml" not in namelist:
                issues.append(
                    ValidationIssue(severity="error", message="Missing 'META-INF/container.xml'.")
                )
                return ValidationReport(is_valid=False, issues=issues)

            container_data = archive.read("META-INF/container.xml")
            container_root = ET.fromstring(container_data)
            rootfile = container_root.find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile")
            if rootfile is None:
                issues.append(
                    ValidationIssue(severity="error", message="No rootfile found in container.xml.")
                )
                return ValidationReport(is_valid=False, issues=issues)

            opf_path = rootfile.attrib.get("full-path", "")
            if not opf_path or opf_path not in namelist:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"OPF package file '{opf_path}' declared in container is missing.",
                    )
                )
                return ValidationReport(is_valid=False, issues=issues)

            # 3. OPF metadata audit
            opf_data = archive.read(opf_path)
            opf_root = ET.fromstring(opf_data)

            metadata = opf_root.find("{http://www.idpf.org/2007/opf}metadata")
            if metadata is None:
                issues.append(ValidationIssue(severity="error", message="Missing <metadata> in OPF."))
            else:
                title_el = metadata.find("{http://purl.org/dc/elements/1.1/}title")
                lang_el = metadata.find("{http://purl.org/dc/elements/1.1/}language")
                id_el = metadata.find("{http://purl.org/dc/elements/1.1/}identifier")

                if title_el is None or not (title_el.text or "").strip():
                    issues.append(ValidationIssue(severity="error", message="Missing required <dc:title>."))
                if lang_el is None or not (lang_el.text or "").strip():
                    issues.append(ValidationIssue(severity="error", message="Missing required <dc:language>."))
                if id_el is None or not (id_el.text or "").strip():
                    issues.append(ValidationIssue(severity="error", message="Missing required <dc:identifier>."))

                # Check accessibility metadata
                meta_props = [
                    m.attrib.get("property", "")
                    for m in metadata.findall("{http://www.idpf.org/2007/opf}meta")
                ]
                if not any("accessibilitySummary" in p for p in meta_props):
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message="Missing 'schema:accessibilitySummary' metadata (recommended for EPUB A11y 1.2).",
                        )
                    )
                if not any("conformsTo" in p for p in meta_props):
                    issues.append(
                        ValidationIssue(
                            severity="info",
                            message="Missing 'dcterms:conformsTo' declaration (e.g. 'epub-a11y-12').",
                        )
                    )

            # 4. Check chapter files & MathML integrity
            for name in namelist:
                if name.lower().endswith((".xhtml", ".html", ".htm")):
                    content = archive.read(name).decode("utf-8", errors="ignore")
                    math_chunks = re_find_math(content)
                    for math_chunk in math_chunks:
                        if not is_valid_mathml(math_chunk):
                            issues.append(
                                ValidationIssue(
                                    severity="error",
                                    message=f"Malformed MathML detected: {math_chunk[:50]}...",
                                    location=name,
                                )
                            )
                        # Double-speaking hazard audit
                        if 'alttext="' in math_chunk.lower() or 'aria-label="' in math_chunk.lower():
                            issues.append(
                                ValidationIssue(
                                    severity="warning",
                                    message="Double-speaking hazard: <math> has alttext or aria-label alongside structured MathML nodes.",
                                    location=name,
                                )
                            )

    except Exception as exc:
        issues.append(ValidationIssue(severity="error", message=f"Failed to read EPUB: {exc}"))

    has_errors = any(i.severity == "error" for i in issues)
    return ValidationReport(is_valid=not has_errors, issues=issues)


def re_find_math(html_text: str) -> list[str]:
    import re

    return re.findall(r"<math\b[^>]*>.*?</math>", html_text, flags=re.DOTALL | re.IGNORECASE)
