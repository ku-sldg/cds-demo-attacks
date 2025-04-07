# CDS Demo Attacks

This repository exists to help enumerate the possible attacks on the CDS demo and show whether or not they are detectable.

| Component      | Change Config | Implemented?                                                                                                                                                                                                                                                                   | Change Behavior | Implemented?                                     |
| -------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- | ------------------------------------------------ |
| Hardware       | &cross;       |                                                                                                                                                                                                                                                                                | &cross;         |                                                  |
| TPM            | &check;       |                                                                                                                                                                                                                                                                                | &cross;         |                                                  |
| Boot Loader    | &check;       |                                                                                                                                                                                                                                                                                | &cross;         |                                                  |
| LKIM           | &check;       |                                                                                                                                                                                                                                                                                | &cross;         |                                                  |
| Kernel         | &check;       |                                                                                                                                                                                                                                                                                | &check;         |                                                  |
| IMA            | &check;       |                                                                                                                                                                                                                                                                                | &check;         | &cross; "Covered by Invart Test Root-Kit Attack" |
| SELinux        | &check;       | &check; "SELinux.Config"                                                                                                                                                                                                                                                       | &check;         | &cross; "Covered by Invary Test Root-Kit Attack" |
| AMs            | &check;       | &cross; Since the AM's phrase is restricted, and we utilize the MAESTRO toolchain, the configuration of the AM is dynamically generated on AM start based upon the given phrase. With a restricted phrase and since MAESTRO binaries are measured by IMA, this is not possible | &check;         | &check; "AM.Behavior"                            |
| ASPs           | &check;       | &cross; ASPs are static and only configured by the attestation manager. Since AM phrase is restricted, attacks here not demonstratable                                                                                                                                         | &check;         | &check; "ASP.Behavior"                           |
| CDS Components | &check;       | &check; "CDS.Config"                                                                                                                                                                                                                                                           | &check;         | &check; "CDS.Behavior"                           |
