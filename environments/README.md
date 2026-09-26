# Tested environments

The scientific environment uses Python 3.14.5, NumPy 2.5.3, SciPy 1.18.1, PennyLane 0.44.1, Matplotlib 3.11.2, nbformat 5.11.1 and nbclient 0.11.0. The original requirements.lock.txt remains byte-identical. Recorded checks pass V1/V2 with SDK, representative V3, notebook execution and the full 125-test suite. The older 25-test receipt in provenance/verification/release_tests.log covers the original release subset.

The portable environment supports data reconstruction, plotting and checks. It uses Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8, nbformat 5.10.4, nbclient 0.10.4, nbconvert 7.16.6 and ipykernel 6.30.1. Its full installed lock is portable-python312.lock.txt. V1/V2 and notebook/HTML execution pass in this environment; V3 skips on an environment mismatch. Full optimization, DMRG and the PennyLane SDK are outside its verified scope.

The portable execution logs record a sandbox psutil/sysctl permission warning during kernel shutdown, after all 9 cells succeed. The logs distinguish this warning from cell errors. It does not change stored scientific data, and no workaround suppresses assertion failures.

Document generation uses bundled Python 3.12.14 with ReportLab 4.4.9, python-pptx 1.0.2 and Pillow 12.3.0. Rendering uses LibreOfficeDev 26.8.0.0.alpha0 and Poppler; officecli 1.0.143 checks schema and layout issues. Fonts are referenced without being bundled.

The research environment has not been upgraded. Portable release packages are installed in an isolated temporary environment.
