"""Generated intake question tables.

DO NOT EDIT BY HAND. This file is regenerated from the
``## Intake Interview Questions`` blocks in
``plugins/*/templates/*.md`` and ``plugins/arckit-claude/plugins/**/templates/*.md``,
plus the MANDATORY-tier prerequisite inputs of the producing command
(same conventions as ``scripts/generate-mcp-gates.py``). Run
``python scripts/generate-mcp-intake.py`` after editing a template.

Shape:

    INTAKE[code] = {"questions": [...], "mandatory_inputs": [code, ...],
                    "source": "plugins/.../...md"}
    COVERAGE[code] = "covered" | "no-static-questions"
    PARSER_NOTES: comment-only list of templates the generator
    could not resolve (see the notes below).
"""

from __future__ import annotations

# PARSER_NOTES:
#   - plugins/arckit-agent-architecture/templates/agent-design-template.md: no resolvable doc-type code
#   - plugins/arckit-agent-architecture/templates/agent-governance-template.md: no resolvable doc-type code
#   - plugins/arckit-agent-architecture/templates/agent-integration-template.md: no resolvable doc-type code
#   - plugins/arckit-agent-architecture/templates/agent-maturity-template.md: no resolvable doc-type code
#   - plugins/arckit-agent-architecture/templates/agent-security-template.md: no resolvable doc-type code
#   - plugins/arckit-togaf-adm/templates/adm-preliminary-template.md: no resolvable doc-type code
#   - plugins/arckit-togaf-adm/templates/architecture-board-template.md: no resolvable doc-type code
#   - plugins/arckit-togaf-adm/templates/architecture-change-template.md: no resolvable doc-type code
#   - plugins/arckit-togaf-adm/templates/capability-map-template.md: no resolvable doc-type code
#   - plugins/arckit-togaf-adm/templates/data-architecture-template.md: no resolvable doc-type code
#   - plugins/arckit-togaf-adm/templates/rationalization-template.md: no resolvable doc-type code
#   - plugins/arckit-togaf-adm/templates/tech-architecture-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/CHANGELOG.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/commands/agent-design.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/commands/agent-governance.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/commands/agent-integration.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/commands/agent-inventory.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/agent/architecture/commands/agent-maturity.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/commands/agent-security.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/references/agent-architecture-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/templates/agent-design-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/templates/agent-governance-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/templates/agent-integration-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/templates/agent-maturity-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/agent/architecture/templates/agent-security-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/commands/at-bvergg.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/commands/at-dsgvo.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/commands/at-nisg.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/templates/at-bvergg-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/templates/at-dsgvo-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/at/templates/at-nisg-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/CHANGELOG.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/commands/au-ai-assurance.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/commands/au-disp-attestation.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/commands/au-dss.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/commands/au-e8-posture.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/commands/au-ism-controls.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/commands/au-ndb-playbook.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/commands/au-ot-security.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/commands/au-pia.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/commands/au-pspf.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/commands/au-soci-cirmp.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/CHANGELOG.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/commands/au-aescsf.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/commands/au-energy-compliance.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/templates/au-aescsf-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/energy/templates/au-energy-compliance-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/au-ai-assurance-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/au-disp-attestation-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/au-dss-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/au-e8-posture-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/au-ism-controls-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/au-ndb-playbook-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/au-ot-security-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/au-pia-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/au-pspf-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/au/templates/au-soci-cirmp-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/commands/ca-aia.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/commands/ca-atip.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/commands/ca-charter.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/commands/ca-cloud-residency.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/commands/ca-fitaa.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/commands/ca-gc-digital-standards.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/commands/ca-itsg-33.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/commands/ca-ocap.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/commands/ca-ola.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/commands/ca-pia.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/commands/ca-pspc.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/commands/ca-soia.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/ca-aia-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/ca-atip-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/ca-charter-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/ca-cloud-residency-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/ca-fitaa-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/ca-gc-digital-standards-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/ca-itsg-33-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/ca-ocap-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/ca-ola-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/ca-pia-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/ca-pspc-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/ca/templates/ca-soia-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/commands/eu-ai-act.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/commands/eu-cra.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/commands/eu-data-act.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/commands/eu-dora.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/commands/eu-dsa.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/commands/eu-nis2.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/commands/eu-rgpd.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/templates/eu-ai-act-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/templates/eu-cra-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/templates/eu-data-act-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/templates/eu-dora-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/templates/eu-dsa-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/templates/eu-nis2-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/eu/templates/eu-rgpd-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fde/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fde/commands/create.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fde/references/config-schema.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/commands/fr-algorithme-public.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/commands/fr-anssi-carto.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/commands/fr-anssi.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/commands/fr-code-reuse.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/commands/fr-dinum.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/commands/fr-dr.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/commands/fr-ebios.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/commands/fr-irn.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/commands/fr-marche-public.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/commands/fr-pssi.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/commands/fr-rgpd.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/commands/fr-secnumcloud.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/fr-algorithme-public-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/fr-anssi-carto-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/fr-anssi-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/fr-code-reuse-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/fr-dinum-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/fr-dr-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/fr-ebios-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/fr-irn-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/fr-marche-public-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/fr-pssi-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/fr-rgpd-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/fr/templates/fr-secnumcloud-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/CHANGELOG.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/commands/it4it-consume-fulfil.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/commands/it4it-develop-test.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/commands/it4it-operate-assure.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/commands/it4it-strategy-portfolio.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/commands/it4it-value-network.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/it4it/commands/it4it-value-stream.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/it4it/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/references/functional-components-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/references/intake-discovery-dimensions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/references/value-streams-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/schemas/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/templates/it4it-consume-fulfil-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/templates/it4it-develop-test-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/templates/it4it-operate-assure-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/it4it/templates/it4it-strategy-portfolio-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/CHANGELOG.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/commands/agile-governance.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/oaa/commands/agile-security.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/oaa/commands/agile-strategy.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/oaa/commands/oaa-adm-lite.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/commands/product-architecture.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/oaa/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/references/intake-discovery-dimensions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/references/oaa-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/schemas/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/oaa/templates/oaa-adm-lite-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/repo/CHANGELOG.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/repo/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/repo/commands/repo-audit.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/repo/commands/repo-docs.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/repo/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/repo/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/repo/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/repo/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/repo/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/repo/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/repo/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/repo/templates/codebase-audit-template.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/togaf/adm/CHANGELOG.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/commands/adm-preliminary.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/commands/application-inventory.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/togaf/adm/commands/application-rationalization.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/commands/architecture-board.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/commands/architecture-change.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/commands/architecture-repository.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/togaf/adm/commands/business-capability-map.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/togaf/adm/commands/data-architecture.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/commands/discovery.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/togaf/adm/commands/gap-analysis.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/togaf/adm/commands/technology-architecture.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/togaf/adm/commands/transition-architecture.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/togaf/adm/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/references/togaf-adm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/templates/adm-preliminary-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/templates/architecture-board-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/templates/architecture-change-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/templates/capability-map-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/templates/data-architecture-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/templates/rationalization-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/togaf/adm/templates/tech-architecture-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/commands/uae-ai-autonomy-tier.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/commands/uae-ai-charter.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/commands/uae-classification.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/commands/uae-cloud-residency.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/commands/uae-data-sharing.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/commands/uae-digital-records.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/commands/uae-ias.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/commands/uae-pdpl.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/commands/uae-priorities-alignment.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/commands/uae-procurement.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/commands/uae-uaepass.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/commands/uae-zero-bureaucracy.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/uae-ai-autonomy-tier-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/uae-ai-charter-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/uae-classification-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/uae-cloud-residency-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/uae-data-sharing-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/uae-digital-records-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/uae-ias-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/uae-pdpl-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/uae-priorities-alignment-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/uae-procurement-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/uae-uaepass-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uae/templates/uae-zero-bureaucracy-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/CHANGELOG.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/commands/uk-fs-consumer-duty.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/commands/uk-fs-ctp-dependency.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/commands/uk-fs-safeguarding.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/commands/uk-fs-sca-rts.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/templates/uk-fs-consumer-duty-board-report-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/templates/uk-fs-consumer-duty-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/templates/uk-fs-ctp-dependency-register-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/templates/uk-fs-ctp-dependency-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/templates/uk-fs-safeguarding-reconciliation-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/templates/uk-fs-safeguarding-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/templates/uk-fs-sca-rts-exemption-matrix-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/finance/templates/uk-fs-sca-rts-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/commands/declaration.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/commands/gcloud-competitors.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/commands/pricing.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/commands/review.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/commands/sdd-lot1.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/commands/sdd-lot2.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/commands/sdd-lot3.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/commands/security.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/commands/service-design.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/uk/gcloud/commands/submission-pack.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/commands/supplier-profile.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/uk/gcloud/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/skills/cloud-security/SKILL.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/skills/cloud-security/references/compliance-frameworks.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/skills/gcloud-framework/SKILL.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/skills/gcloud-framework/references/framework-questions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/skills/sfia-skills/SKILL.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/skills/sfia-skills/references/sfia-skills.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/templates/declaration-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/templates/pricing-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/templates/sdd-lot1-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/templates/sdd-lot2-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/templates/sdd-lot3-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/templates/security-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/gcloud/templates/service-design-template.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/uk/gcloud/templates/supplier-profile-template.md: no parseable questions under '## Intake Interview Questions'
#   - plugins/arckit-claude/plugins/uk/nhs/CHANGELOG.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/commands/uk-mdr-classification.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/commands/uk-nhs-dcb0129.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/commands/uk-nhs-dcb0160.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/commands/uk-nhs-dtac.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/references/duaa2025.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/references/hazard-archetypes.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/references/nhs-clinical-safety-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/uk-mdr-classification-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/uk-nhs-dcb0129-case-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/uk-nhs-dcb0129-hazard-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/uk-nhs-dcb0129-safety-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/uk-nhs-dcb0129-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/uk-nhs-dcb0160-deployment-case-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/uk-nhs-dcb0160-deployment-hazard-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/uk-nhs-dcb0160-deployment-safety-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/uk-nhs-dcb0160-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/uk/nhs/templates/uk-nhs-dtac-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/CHANGELOG.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/README.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/commands/us-ai-impact.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/commands/us-ai-rmf.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/commands/us-fedramp-readiness.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/commands/us-fedramp-ssp.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/commands/us-fisma-categorization.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/commands/us-icam.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/commands/us-nist-800-53.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/commands/us-privacy-pia.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/commands/us-sbom-eo-14028.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/commands/us-zero-trust.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/references/bmm-reference.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/references/citation-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/references/intake-instructions.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/references/quality-checklist.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/_partials/RENDERING.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/_partials/document-control-uae.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/_partials/document-control-uk.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/us-ai-impact-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/us-ai-rmf-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/us-fedramp-readiness-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/us-fedramp-ssp-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/us-fisma-categorization-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/us-icam-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/us-nist-800-53-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/us-privacy-pia-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/us-sbom-eo-14028-template.md: no resolvable doc-type code
#   - plugins/arckit-claude/plugins/us/templates/us-zero-trust-template.md: no resolvable doc-type code

INTAKE: dict = {
    "AAGI": {
        'questions': ["**Agents:** Which AI agents exist or are planned? For each: purpose, model, deployment target, owner, risk level, and oversight mode.", "**Scope:** Which environments and use cases does the inventory cover?", "**Status:** Which agents are in production vs. staging vs. planned, and which are retired?", "**Risk basis:** On what evidence is each agent's risk level assigned?", "**Oversight:** Which agents need human-in-the-loop / on-the-loop oversight, and who is accountable?"],
        'mandatory_inputs': [],
        'source': "plugins/arckit-agent-architecture/templates/agent-inventory-template.md",
    },
    "APP": {
        'questions': ["**Portfolio:** Which applications exist today? For each: owner, status (active/deprecated/planned), and lifecycle stage.", "**Fit:** Which applications are fit-for-purpose, and which are workaround or shadow systems?", "**Dependencies:** Which applications integrate with which, and through what patterns (API, batch, file)?", "**Data flows:** Which applications produce or consume the key data assets?", "**Pain points:** Where do application-level pain points, license risk, or security debt surface?", "**Inventory scope:** What is the scope of this application inventory? Options: `All applications` | `Business Unit` | `Specific Project` (default: `All applications`)."],
        'mandatory_inputs': ["ADMP"],
        'source': "plugins/arckit-togaf-adm/templates/application-inventory-template.md",
    },
    "DISC": {
        'questions': ["**Business context:** What is the strategic direction, and what are the key drivers and the current operating model?", "**Capability state:** Which capabilities exist today, at what maturity, and which are obsolete or legacy?", "**Application landscape:** Which applications exist, who owns them, and which are deprecated or planned for retirement?", "**Data state:** Which data systems exist, who owns the data, and what classification levels apply?", "**Technology baseline:** Which infrastructure, platforms, and hosting environments are in use?", "**Constraints:** What legacy dependencies, compliance requirements, and budget limits constrain any future state?", "**Pain points:** Where are the most acute operational, data, or technology problems today?"],
        'mandatory_inputs': [],
        'source': "plugins/arckit-togaf-adm/templates/discovery-template.md",
    },
    "GAPS": {
        'questions': ["**Current state:** What is the evidenced current state for the dimensions in scope (capability, application, data, technology)?", "**Target state:** What is the agreed target state each gap is measured against?", "**Gaps:** For each gap: what exactly is missing, and what is its business impact?", "**Root causes:** What is causing each gap (capability, funding, skills, technology, process)?", "**Mitigations:** What closes each gap, and which mitigation maps to which transition work package?", "**Gap severity weighting:** How should gap severity be weighted? Options: `Balanced` | `Strategic-risk` | `Operational` (default: `Balanced`):", "Balanced", "Strategic-risk", "Operational"],
        'mandatory_inputs': ["BPCM"],
        'source': "plugins/arckit-togaf-adm/templates/gap-analysis-template.md",
    },
    "ITCF": {
        'questions': ["**Service catalog:** What service offerings are in the catalog, and how are they defined/published?", "**Consumer lifecycle:** How do consumers select, agree, subscribe, and receive support/status?", "**Chargeback:** What is the chargeback contract and record model?", "**Fulfillment:** How are changes managed, resources provisioned, and usage tracked?", "**Consume components (S261 Ch. 8):** Which consume components are in scope \u2014 consumption experience, identity, offering, order, chargeback?", "**Fulfill components (S261 Ch. 8):** Which fulfill components are in scope \u2014 change, fulfillment orchestration, resource, fulfillment, usage?", "**Service Offering backbone (S261 Ch. 11):** How are the Service Offering, Order, and Subscription KDOs structured, and what is their system of record?", "**Service Contract (S261 Ch. 8):** How is the Service Contract (Digital Product Contract) created, updated, and enforced?"],
        'mandatory_inputs': ["PRIN"],
        'source': "plugins/arckit-it4it/templates/it4it-consume-fulfil-template.md",
    },
    "ITDT": {
        'questions': ["**Product backlog:** What is the product backlog structure, and how are items prioritised?", "**Pipeline shape:** What are the CI/CD pipeline stages, and what guardrails apply at each?", "**Build packages:** What are the build package rules, and how do build packages compose into a Product Release?", "**Testing model:** How are test cases and test plans traced to requirements, and what is the defect lifecycle?", "**Develop components (S261 Ch. 7):** Which develop components are in scope \u2014 product backlog, requirement, product design, source control, pipeline, build package, release composition?", "**Test components (S261 Ch. 7):** How are test cases, test plans, and defects structured, and how do they trace to requirements?", "**Integrate stream mapping (S261 Ch. 5):** How do the Integrate stages \u2014 Plan Product Release \u2192 Design & Develop \u2192 Build, Integrate, & Test \u2192 Accept & Publish Release \u2014 map onto the functional components?", "**Quality gates (S261 Ch. 7):** What are the quality gates at each Integrate stage, and what are the exit criteria?"],
        'mandatory_inputs': ["PRIN"],
        'source': "plugins/arckit-it4it/templates/it4it-develop-test-template.md",
    },
    "ITOA": {
        'questions': ["**Service levels:** What KPIs/SLOs are measured against the Service Contract?", "**Incident & problem:** What is the incident/problem lifecycle and prioritisation model?", "**Monitoring & assurance:** What service monitors, logs, and events are in scope?", "**Remediation:** What runbooks exist, and what are the automated-remediation boundaries?", "**Supporting functions:** Which supporting functions (financial, GRC, workforce, sourcing, intelligence, collaboration) apply?", "**Support components (S261 Ch. 9):** Which support components are in scope \u2014 service level, incident, problem, knowledge?", "**Assure components (S261 Ch. 9):** Which assure components are in scope \u2014 configuration, monitoring, event, diagnostics & remediation?", "**Operate stream mapping (S261 Ch. 5):** How do the Operate stages \u2014 Detect Issue \u2192 Diagnose Issue \u2192 Resolve Issue \u2014 map onto the functional components?", "**Supporting functions (S261 Ch. 10):** Which supporting functions attach to this operating model, and how?"],
        'mandatory_inputs': ["PRIN"],
        'source': "plugins/arckit-it4it/templates/it4it-operate-assure-template.md",
    },
    "ITSF": {
        'questions': ["**Policy framework:** What is the policy review/approval/audit cadence, and applicable geography?", "**Strategy:** What strategic themes and strategic objectives govern this portfolio?", "**Portfolio backlog:** How are Portfolio Backlog Items prioritised, and what demand profile / cost estimation model is used?", "**Resource plans:** How are funding packages (resource plans) structured, and what is the proposal state machine?", "**Policy component (S261 Ch. 6):** Which policies govern the digital products, and what is their lifecycle (create \u2192 review \u2192 approve \u2192 audit)?", "**Strategy component (S261 Ch. 6):** What are the strategic themes (direction + priorities) and the strategic objectives (actionable + measurable) they summarise?", "**Portfolio backlog component (S261 Ch. 6):** What is the PBI lifecycle, and how are PBIs related to Strategic Objectives, Architecture Roadmap Items, Policies, Resource Plans, and Digital Products?", "**Proposal component (S261 Ch. 6):** What are the states of a resource plan / proposal \u2014 proposed, approved, active, deferred, rejected \u2014 and what moves between them?"],
        'mandatory_inputs': ["PRIN"],
        'source': "plugins/arckit-it4it/templates/it4it-strategy-portfolio-template.md",
    },
    "ITVN": {
        'questions': ["**Scope:** Which IT product portfolio or programme is this Value Network for?", "**Digital Product:** What is the Digital Product (the anchor KDO bundle) at the centre of the network?", "**Stream coverage:** Are all seven value streams in scope, or is this a partial network view?", "**Scenarios:** Which scenarios from the S261 scenario catalog does this view cover?", "**Feedback loop:** How does the Operate stream feed findings back into Evaluate?", "**Seven streams (S261 Ch. 5):** Confirm the trigger, primary stakeholder, and stage sequence for each of the seven streams \u2014 Evaluate, Explore, Integrate, Deploy, Publish, Consume, Operate.", "**Cross-stream dependencies (S261 Ch. 5):** Which handoff KDOs cross stream boundaries, and what is the contract (cardinality + system-of-record obligation) at each handoff?", "**Digital Product backbone (S261 Ch. 11):** How are the Digital Product Backbone (Digital Product, Digital Product Contract, Service Offering, System) and the Service Offering Backbone (Service Offering, Order, Subscription) positioned per stream?", "**Scenarios (S261 Ch. 5):** Which scenarios does this network view cover, and which are out of scope?"],
        'mandatory_inputs': ["PRIN"],
        'source': "plugins/arckit-it4it/templates/it4it-value-network-template.md",
    },
    "ITVS": {
        'questions': ["**Which value stream:** Evaluate, Explore, Integrate, Deploy, Publish, Consume, or Operate?", "**Scenario:** Which of the stream's scenarios does this artefact cover (e.g. \"Deploy a New Product Release Version\")?", "**Trigger:** What triggers the stream \u2014 portfolio planning cycle, changed resource plan, backlog pull, approved release, consumer selection, or detected issue?", "**Primary stakeholder:** Who owns the stream \u2014 Digital Product Portfolio Manager, Digital Product Manager, Catalog Manager, or Consumer?", "**Cross-stream inputs/outputs:** Which upstream stream feeds this one, and what does this one hand downstream?", "**Stage sequence (S261 Ch. 5):** Which of the stream's stage sequence applies, and where does customisation or extension occur?", "**Participating functional components (S261 Ch. 6\u201310):** Which functional components support each stage (e.g. Portfolio Backlog, Proposal for Evaluate; Product Backlog, Pipeline for Integrate)?", "**Key data objects (S261 Ch. 11):** Which KDOs flow through the stages \u2014 which originate here, which are consumed from upstream, which are published downstream?", "**Systems of record:** Which system is the authoritative source for each KDO this stream controls?"],
        'mandatory_inputs': ["PRIN"],
        'source': "plugins/arckit-it4it/templates/it4it-value-stream-template.md",
    },
    "OAAL": {
        'questions': ["**Engagement scope:** What is the scope of this 2-4 week engagement (product, capability, or platform)?", "**Vision:** What is the outcome this sprint map is working toward, and what does \"done\" look like?", "**Stakeholders:** Who are the stakeholders, and what will each measure as success?", "**Outcome dimensions:** What are the Value, Outcome, Experience, and Adoption targets for the engagement, and how is value defined \u2014 functional benefits plus the emotional dimension (C208 \u00a74.2.3)?", "**Constraints:** What jurisdiction, budget, timeline, and regulatory controls apply?", "**Current state:** What is the current technology / data / team state relevant to this engagement?", "**Risks:** What is the top risk to the sprint map, and what de-risks it?", "**Building-block selection (C208 \u00a74.2):** Which O-AA building blocks does this engagement need \u2014 Strategy, Value, the three perspectives (Experience, Work System, Technical System), and Data/Information & AI?", "**Strategy & assumptions (C208 \u00a74.2.1):** What is the strategic positioning in scope, and which strategic assumptions must be experimentally verified (not assumed) during the engagement?", "**Perspective scoping (C208 \u00a74.2.4):** For the Experience perspective, which job-to-be-done, pain points and gains are in scope; for Work System, which value-stream activities; for Technical System, which systems and interfaces?", "**Refactoring waves (C208 \u00a76):** What are the continuous-refactoring waves, and what is the exit/definition-of-done criterion that closes each sprint's architectural increment?"],
        'mandatory_inputs': ["PRIN"],
        'source': "plugins/arckit-oaa/templates/oaa-adm-lite-template.md",
    },
    "OAGOV": {
        'questions': ["**Review cadence:** What does the sprint architecture review (pre/post sprint) check, and who runs it?", "**Debt:** What architecture debt categories exist, and what threshold triggers a debt backlog entry?", "**Health:** What does the quarterly architecture health rubric measure, and who scores it?", "**Compliance:** Which continuous compliance checks (compliance-as-code) gate the pipeline, and where do they run?", "**Decision rights (C208 \u00a78):** Which decision rights (authority) are allocated to which teams \u2014 architect, tech lead, compliance owner \u2014 and is accountability matched to each?", "**Guardrails over standards (C208 \u00a78.2\u20138.3):** Which standards become guardrails (policy intent) that teams apply bottom-up, rather than a top-down approved-catalog mandate?", "**Integrated business+IT governance (C208 \u00a78.3):** How do Quarterly Business Reviews, sponsor resource-release, and post-mortems operate across the tribes, and how is IT investment treated as a subset of business investment?", "**Alignment levers (C208 \u00a78.3):** What shared purpose, shared consciousness, forcing functions, and feedback loops keep autonomous teams aligned?", "**Model scope (C208 \u00a78):** Which governance model is targeted \u2014 digital governance or TOGAF architecture governance \u2014 and what formally replaces the classical architecture review board?"],
        'mandatory_inputs': ["PRIN"],
        'source': "plugins/arckit-oaa/templates/agile-governance-template.md",
    },
    "OAPR": {
        'questions': ["**Mission:** What is the product mission in one sentence?", "**Outcome:** What are the Value / Outcome / Experience / Adoption targets and their measurements?", "**Principles:** Which product architecture principles (grounded in O-AA axioms) will the team follow?", "**Team:** What is the cross-functional team composition, and who is the architect on it?", "**Backlog:** Which epics and architecture items are already on the product backlog?", "**Roadmap:** What do the next release waves target, and what gate criteria apply?", "**Current state (TOGAF 10 D5):** What is the product's current state (systems, data, operating model) that the roadmap moves away from?", "**Pain points (TOGAF 10 D8):** What are the sharpest user or delivery pain points this architecture must relieve?", "**Partitioning (C208 \u00a714.1):** How is the product's functional elements mapped to its building blocks/components, and what does the Design Structure Matrix show about coupling?", "**Modularity\u2013integrality trade-off (C208 \u00a714.2\u201314.3):** Where do you favour modularity (loose coupling, team autonomy) over integrality (performance), and what propagation cost do you accept?", "**Product platforms (C208 \u00a714.4):** Is this a product platform/product line? Which shared components and preplanned variation mechanisms (parameterization, inheritance) does it expose?", "**Decision typing (C208 \u00a75.2):** Which decisions are Type 1 (one-way, hard to reverse) vs Type 2 (two-way), and at what scope (team / team-of-teams) is each decided?", "**ADRs (C208 \u00a75.3):** Which architecturally significant decisions need an Architecture Decision Record (context, decision, consequences, status), and who owns the ADR?", "**Time horizon (C208 \u00a75.1):** Is this enterprise architecture (long horizon) or product/solution architecture (release horizon), and how do the two stay aligned?"],
        'mandatory_inputs': ["PRIN"],
        'source': "plugins/arckit-oaa/templates/product-architecture-template.md",
    },
    "OASEC": {
        'questions': ["**Embedded security:** What security stories and estimates enter sprint planning, and who owns them?", "**Compliance gates:** Which compliance-as-code gates run in CI/CD, and which regulation/standard each enforces?", "**Sprint-gate validation:** What evidence closes the sprint security gate (tests, attestations, reviews)?", "**Metrics:** Which security KPIs feed the metrics dashboard, and what are their targets?", "**Minimum Security Architecture (Playbook \u00a72):** What is the MSA that guides this sprint's MVP, and where are the security sub-system boundaries (each with its own lifecycle)?", "**Layers of controls (Playbook \u00a74.1):** Which of the five layers (assets, security systems, computing/network, physical, personnel) are in scope, and which protection objective (confidentiality/integrity/availability) each serves?", "**Risk appetite (Playbook \u00a74):** What is the defined risk threshold \u2014 and the risk-based scan thresholds that gate a sprint (vulnerability, dependency, secret) \u2014 quantified via Open FAIR (Loss Event Frequency \u00d7 Loss Magnitude) or a documented methodology?", "**DevSecOps pipeline (Playbook \u00a74.2):** Where do threat-modeling, static analysis, dynamic scanning, and penetration testing sit, and what gates each stage?", "**Roles (Playbook \u00a73):** Who is the agile security architect/champion, and how do they team with risk management, cloud/network providers, and enterprise security?", "**Security-architecture quality (Playbook \u00a75):** Is the architecture deployable today, testable/falsifiable, roll-backable, and does it provide built-in monitoring and traceability?"],
        'mandatory_inputs': ["PRIN"],
        'source': "plugins/arckit-oaa/templates/agile-security-template.md",
    },
    "OASTR": {
        'questions': ["**Vision (TOGAF 10 D1):** What is the digital transformation vision, and which outcomes does it prioritize?", "**Digital dimension:** What changes in technology, product, and operating model \u2014 and what is the current state of each?", "**Agile dimension:** What organizational, cultural, and team agility changes are required?", "**Resilience:** Which failure scenarios must the strategy prepare for, and what does each map to?", "**Waves:** What are the transformation waves, their targets, and their dependencies?", "**Pain points (TOGAF 10 D8):** What are the top current-state pain points and capability gaps this strategy addresses?", "**Situational awareness (C208 \u00a711.1.1):** What front-line \"Gemba\" evidence informs the strategy, and which incumbent mental models must be challenged?", "**Hard-to-reverse choices (C208 \u00a711.1.2):** What are the big bets / breakthrough objectives \u2014 the Type 1 hard-to-reverse choices the strategy commits to?", "**Stability vs dynamism (C208 \u00a711.1.4\u201311.1.5):** How are stable strategic priorities decoupled from dynamic quarterly re-planning, and what cadence do the strategy dialogs run at?", "**Cross-silo deployment (C208 \u00a711.1.6):** Which breakthrough objectives require cross-functional decomposition, and how are objectives/OKRs cascaded and funded?", "**Unintended consequences (C208 \u00a711.2):** Which hypotheses underlie the strategy, what experiments test them, and what countermeasures bend the law of unintended consequences?", "**Axioms as constraints (C208 \u00a79):** Which of the 16 O-AA axioms are adopted as binding constraints, and which conflict with current practice?"],
        'mandatory_inputs': ["PRIN"],
        'source': "plugins/arckit-oaa/templates/agile-strategy-template.md",
    },
    "REPO": {
        'questions': ["**Scope:** Which artefact families does this repository cover (strategy, capability, application, data, technology, transition)?", "**Owners:** Who owns each artefact family and the repository itself?", "**Retention:** What is the retention / versioning policy for retired artefacts?", "**Access:** Who can read, edit, or approve repository content?", "**Tooling:** Where is the repository hosted, and how is it kept in sync with the source of truth?"],
        'mandatory_inputs': ["PRIN"],
        'source': "plugins/arckit-togaf-adm/templates/architecture-repository-template.md",
    },
    "TRANS": {
        'questions': ["**Milestones:** What are the transition milestones / release waves, with target dates?", "**Work packages:** Which work packages close which gaps, and what is their dependency order?", "**Exit criteria:** What must be true at each milestone gate to proceed?", "**Enablers:** What organizational enablers (training, funding, governance) are required in transition?", "**Risk:** What is the top transition risk, and what is its mitigation?", "**Transition waves:** How many transition architectures (migration waves) should the plan cover? Options: `2 waves` | `3 waves (Recommended)` | `4 waves` (default: `3 waves`):", "2 waves", "3 waves (Recommended)", "4 waves"],
        'mandatory_inputs': ["GAPA"],
        'source': "plugins/arckit-togaf-adm/templates/transition-architecture-template.md",
    },
}

COVERAGE: dict = {
    "AAGI": "covered",
    "AAGR": "no-static-questions",
    "AAIN": "no-static-questions",
    "AAMT": "no-static-questions",
    "AAOV": "no-static-questions",
    "AASE": "no-static-questions",
    "ACHG": "no-static-questions",
    "ADMP": "no-static-questions",
    "ADR": "no-static-questions",
    "AIA": "no-static-questions",
    "AIACT": "no-static-questions",
    "AICH": "no-static-questions",
    "AIIA": "no-static-questions",
    "AIPB": "no-static-questions",
    "AIRMF": "no-static-questions",
    "ALGO": "no-static-questions",
    "ANAL": "no-static-questions",
    "ANSSI": "no-static-questions",
    "APP": "covered",
    "APPR": "no-static-questions",
    "ARCH": "no-static-questions",
    "ATDSG": "no-static-questions",
    "ATIP": "no-static-questions",
    "ATNISG": "no-static-questions",
    "ATRS": "no-static-questions",
    "AUAESCSF": "no-static-questions",
    "AUAIA": "no-static-questions",
    "AUDISP": "no-static-questions",
    "AUDSS": "no-static-questions",
    "AUE8": "no-static-questions",
    "AUENERGY": "no-static-questions",
    "AUISM": "no-static-questions",
    "AUNDB": "no-static-questions",
    "AUOT": "no-static-questions",
    "AUPIA": "no-static-questions",
    "AUPSPF": "no-static-questions",
    "AUSOCI": "no-static-questions",
    "AUTI": "no-static-questions",
    "AWRS": "no-static-questions",
    "AZRS": "no-static-questions",
    "BKLG": "no-static-questions",
    "BMM": "no-static-questions",
    "BORD": "no-static-questions",
    "BPCM": "no-static-questions",
    "BVERGG": "no-static-questions",
    "CACR": "no-static-questions",
    "CARTO": "no-static-questions",
    "CDAU": "no-static-questions",
    "CHRT": "no-static-questions",
    "CLAS": "no-static-questions",
    "CMPT": "no-static-questions",
    "CNIL": "no-static-questions",
    "CONF": "no-static-questions",
    "CRA": "no-static-questions",
    "CRES": "no-static-questions",
    "DATA": "no-static-questions",
    "DATAACT": "no-static-questions",
    "DECK": "no-static-questions",
    "DECL": "no-static-questions",
    "DEVOPS": "no-static-questions",
    "DFD": "no-static-questions",
    "DIAG": "no-static-questions",
    "DIGSTD": "no-static-questions",
    "DINUM": "no-static-questions",
    "DISC": "covered",
    "DLDR": "no-static-questions",
    "DMC": "no-static-questions",
    "DORA": "no-static-questions",
    "DOS": "no-static-questions",
    "DPIA": "no-static-questions",
    "DR": "no-static-questions",
    "DREC": "no-static-questions",
    "DSA": "no-static-questions",
    "DSCT": "no-static-questions",
    "DSHR": "no-static-questions",
    "EBIOS": "no-static-questions",
    "EVAL": "no-static-questions",
    "FINOPS": "no-static-questions",
    "FIPS199": "no-static-questions",
    "FITAA": "no-static-questions",
    "FPRO": "no-static-questions",
    "FRRR": "no-static-questions",
    "FRSSP": "no-static-questions",
    "FSCD": "no-static-questions",
    "FSCTP": "no-static-questions",
    "FSSAFE": "no-static-questions",
    "FSSCA": "no-static-questions",
    "FWRK": "no-static-questions",
    "GAPA": "no-static-questions",
    "GAPS": "covered",
    "GCLC": "no-static-questions",
    "GCLD": "no-static-questions",
    "GCMP": "no-static-questions",
    "GCRS": "no-static-questions",
    "GCRV": "no-static-questions",
    "GCSR": "no-static-questions",
    "GLND": "no-static-questions",
    "GLOS": "no-static-questions",
    "GOVR": "no-static-questions",
    "GRNT": "no-static-questions",
    "HLDR": "no-static-questions",
    "IAS": "no-static-questions",
    "ICAM": "no-static-questions",
    "IRN": "no-static-questions",
    "ITCF": "covered",
    "ITDT": "covered",
    "ITOA": "covered",
    "ITSF": "covered",
    "ITSG": "no-static-questions",
    "ITVN": "covered",
    "ITVS": "covered",
    "JSP936": "no-static-questions",
    "MARPUB": "no-static-questions",
    "MLOPS": "no-static-questions",
    "MMOD": "no-static-questions",
    "NHSDTAC": "no-static-questions",
    "NHSMDR": "no-static-questions",
    "NIS2": "no-static-questions",
    "NIST": "no-static-questions",
    "NPRA": "no-static-questions",
    "OAAL": "covered",
    "OAGOV": "covered",
    "OAPR": "covered",
    "OASEC": "covered",
    "OASTR": "covered",
    "OCAP": "no-static-questions",
    "OLA": "no-static-questions",
    "OPS": "no-static-questions",
    "PDPL": "no-static-questions",
    "PIA": "no-static-questions",
    "PLAN": "no-static-questions",
    "PLAT": "no-static-questions",
    "PRES": "no-static-questions",
    "PRIC": "no-static-questions",
    "PRIN": "no-static-questions",
    "PRIN-COMP": "no-static-questions",
    "PROC": "no-static-questions",
    "PSSI": "no-static-questions",
    "REPO": "covered",
    "REQ": "no-static-questions",
    "REUSE": "no-static-questions",
    "RGPD": "no-static-questions",
    "RISK": "no-static-questions",
    "ROAD": "no-static-questions",
    "RSCH": "no-static-questions",
    "SBOM": "no-static-questions",
    "SDD": "no-static-questions",
    "SECA": "no-static-questions",
    "SECD": "no-static-questions",
    "SECD-MOD": "no-static-questions",
    "SECNUM": "no-static-questions",
    "SNOW": "no-static-questions",
    "SOBC": "no-static-questions",
    "SOIA": "no-static-questions",
    "SOLN": "no-static-questions",
    "SOW": "no-static-questions",
    "STKE": "no-static-questions",
    "STORY": "no-static-questions",
    "STRAT": "no-static-questions",
    "SUPP": "no-static-questions",
    "SVCASS": "no-static-questions",
    "SVCD": "no-static-questions",
    "TCOP": "no-static-questions",
    "TECH": "no-static-questions",
    "TNDR": "no-static-questions",
    "TRAC": "no-static-questions",
    "TRANS": "covered",
    "UPASS": "no-static-questions",
    "USPIA": "no-static-questions",
    "VEND": "no-static-questions",
    "WARD": "no-static-questions",
    "WCLM": "no-static-questions",
    "WDOC": "no-static-questions",
    "WGAM": "no-static-questions",
    "WVCH": "no-static-questions",
    "ZBUR": "no-static-questions",
    "ZTA": "no-static-questions",
}
