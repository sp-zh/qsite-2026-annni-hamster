# Tested environments

Scientific: Python3.14.5, NumPy2.5.3, SciPy1.18.1, PennyLane0.44.1, Matplotlib3.11.2, nbformat5.11.1, nbclient0.11.0. Original requirements.lock.txt remains byte-identical. V1/V2 with SDK, representative V3, notebook execution and the full 125-test suite pass. The older 25-test receipt in provenance/verification/release_tests.log records the original release subset.

Portable data/redraw/check environment: Python3.12.14, NumPy2.3.5, SciPy1.17.0, Matplotlib3.10.8, nbformat5.10.4, nbclient0.10.4, nbconvert7.16.6, ipykernel6.30.1. Full installed lock is portable-python312.lock.txt. This isolated environment does not certify full optimization/DMRG or the PennyLane SDK. V1/V2 and notebook+HTML execute; V3 explicitly skips on mismatch.

The retained portable execution logs include a sandbox psutil/sysctl permission warning during kernel shutdown. It occurs after all9 cells succeed, not during numerical validation; retained execution logs distinguish it from cell errors. It does not change stored scientific data. No workaround suppresses an assertion failure.

Document builder: bundled Python3.12.14, ReportLab4.4.9, python-pptx1.0.2, Pillow12.3.0. Rendering: LibreOfficeDev26.8.0.0.alpha0; officecli1.0.143 schema/issues checks; Poppler rendering. Fonts are referenced, never bundled.

No research environment was upgraded. Release portable packages are installed in an isolated temporary environment.
