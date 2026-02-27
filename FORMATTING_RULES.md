# Resume formatting – do not change

Resume generation must **preserve formatting exactly** from the reference document and metadata. In future work:

- **Do not change** font style, font size, spacing (paragraph or line), or any other formatting.
- All formatting comes from `metadata/format_metadata.json` and the reference docx only.
- Do not hardcode fonts, sizes, or spacing in code.
- Content (text) may be updated; formatting is always applied from metadata so output matches the reference.

See `scripts/enhanced_format_system.py` module docstring and `.cursor/rules/resume-formatting.mdc` for details.
