# Samsung BOM TCL Example

## Samsung-Specific Library Configuration

```tcl
# Samsung 8nm Library Configuration
set FOUNDRY "Samsung"
set NODE "8LPU"
set LIBRARY_NAME "sa08nvghlogl20hsf068f"

# Physical Files
set LIBRARY(gds) "/ori/STD_Cell/0711_install/v-logic_${LIBRARY_NAME}/gds/${LIBRARY_NAME}.gds"
set LIBRARY(lef) "/ori/STD_Cell/0711_install/v-logic_${LIBRARY_NAME}/lef/${LIBRARY_NAME}.lef"

# Timing Libraries
set LIBRARY(ccs_lvf) "/ori/STD_Cell/0711_install/v-logic_${LIBRARY_NAME}/liberty/ccs_lvf/${LIBRARY_NAME}_ffpg0p825vn40c.db"
set LIBRARY(ccs_power) "/ori/STD_Cell/0711_install/v-logic_${LIBRARY_NAME}/liberty/ccs_power/${LIBRARY_NAME}_tt0p75v125c.db"

# Verilog Models
set LIBRARY(verilog) "/ori/STD_Cell/0711_install/v-logic_${LIBRARY_NAME}/verilog/${LIBRARY_NAME}.v"
```

## PVT Corner Mapping
- `ffpg0p825vn40c` → sigcmin (best case)
- `sspg0p675v125c` → sigcmax (worst case)  
- `tt0p75v125c` → typical