# Separate erratum to historical boundary logging

The original v1.4 log, script, classifications and checksums are preserved. In `scripts/log_boundary_batch.py`, line 9, the descriptive `note` default is the negative sentence “Visible terminal and initial text match the boundary context; no separator edit justified.” The default is evaluated independently of the explicitly supplied classification and boundary type. It can therefore coexist with AUTO-MECHANICAL and “missing separator between complete words.” The original invocation arguments have not been reconstructed.

The v1.9 investigation independently verified the fifteen readings. The exclusive v2.0 instruction now authorizes their local application. Fresh manuscript confirmation, original export context, exact source compatibility and mechanical protection checks support each entry below. This erratum supersedes the descriptive conclusion only in the new current record; it does not rewrite historical evidence or turn a historical automated class into individual human approval.

An additional reference correction concerns XIII.247 (`M14-B13-d5f6ea1941`). The preserved v1.9 machine register contains two exact `Iudaei / uero` pairs. Its prose report selected the first (2983/2985), belonging to a different occurrence. Full preceding/following context and the manuscript identify 3081/3085: “confirmans pactum finiret bellum. Iudaei” / “uero omnia perferre preter custodiam.” The v2.0 record explicitly selects that pair; no Latin letters, editorial reading or historical file is changed by this metadata correction.

| Candidate | Niese | Boundary | T-PEN export positions | Result |
|---|---|---|---|---|
| `M14-B13-48004f243c` | XIII.120 | ptolomei / militiam | 1461 / 1465 | One space inserted; marker unchanged |
| `M14-B13-477cdb858d` | XIII.154 | in / iudaea | 1907 / 1909 | One space inserted; marker unchanged |
| `M14-B13-c028dee2a1` | XIII.225 | tradens / ad | 2817 / 2819 | One space inserted; marker unchanged |
| `M14-B13-7899741b9f` | XIII.232 | magis / impetu | 2907 / 2911 | One space inserted; marker unchanged |
| `M14-B13-d5f6ea1941` | XIII.247 | Iudaei / uero | 3081 / 3085 | One space inserted; marker unchanged |
| `M14-B13-e406f2ca6b` | XIII.263 | prouinciam / aestiment | 3255 / 3259 | One space inserted; marker unchanged |
| `M14-B13-c0abf9e4f3` | XIII.271 | incursionibus / fratris | 3343 / 3345 | One space inserted; marker unchanged |
| `M14-B13-30b81dc20e` | XIII.293 | illi / posse | 3603 / 3607 | One space inserted; marker unchanged |
| `M14-B13-204148f34e` | XIII.327 | cedere / ocio | 4039 / 4041 | One space inserted; marker unchanged |
| `M14-B13-a7f1a6a8f5` | XIII.341 | exercitu / multi | 4213 / 4215 | One space inserted; marker unchanged |
| `M14-B13-f5fa29f54e` | XIII.358 | redisse / matremque | 4387 / 4389 | One space inserted; marker unchanged |
| `M14-B13-db4aa6b6c3` | XIII.394 | antiochi / dicitur, | 4821 / 4825 | One space inserted; marker unchanged |
| `M14-B13-5487ad9420` | XIII.408 | hyrcanus / socer | 4995 / 4999 | One space inserted; marker unchanged |
| `M14-B13-b4dbbb3471` | XIII.414 | nomen / auditum. | 5083 / 5085 | One space inserted; marker unchanged |
| `M14-B13-429234a8fe` | XIII.430 | regni / nono, | 5257 / 5259 | One space inserted; marker unchanged |

Each XML repair is exactly one ASCII space (`20` in hexadecimal), inserted at a source-bound position before the existing page or column marker. All marker bytes, all Latin letters, orthography, punctuation, abbreviations and Niese structure remain unchanged. Original export positions are not represented as polygon or physical line coordinates.

The machine-readable erratum records the original note and classification, original script SHA-256, original candidate-record hash, exact image/crop coordinates and current disposition. `historical_evidence_preservation.json` checks the original script and logging files against their v1.4 manifest. No corrected historical logging script is installed as part of this integration.
