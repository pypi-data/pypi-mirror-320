# version 0.28 (2025/01/12)

## new things
- Added function to calculate absorption per atom for Rb.
  It uses interpolation and significantly faster then calling
  for absorption directly. Another decision, it works per atom
  which makes it suitable for fast fitting of absorption spectra.

# version 0.27 (2025/01/09)

## new things
- ported Rb atom relevant calculations for D1 and D2 line
  from https://github.com/DawesLab/rubidium
    - we have absorption, pressure, density and other methods
    - introduce bug fixes and new formula for pressure calculation

## fixes
- reworked `tox.ini` to make it truly work
- code now is `black` formatted and `ruff` linter approved
- test with table reflow does not trigger `pandas` warning

