# CCS Power Files Explained

## Overview
CCS Power files contain detailed power consumption models for standard cells.

## Power Models
- **Static Power**: Leakage current models
- **Dynamic Power**: Switching power models
- **Internal Power**: Cell internal power consumption

## File Format
Liberty format with CCS power extensions:
```
power_lut_template(power_template_7x7) {
  variable_1 : input_net_transition;
  variable_2 : total_output_net_capacitance;
  index_1 ("0.01, 0.02, 0.04, 0.08, 0.16, 0.32, 0.64");
  index_2 ("0.01, 0.02, 0.04, 0.08, 0.16, 0.32, 0.64");
}
```

## Usage
Essential for power analysis and optimization in:
- Power estimation tools
- Low-power design flows
- Battery life analysis