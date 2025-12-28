# CCS LVF Compressed Files Explained

## Overview
Composite Current Source (CCS) Liberty Variation Format (LVF) compressed files contain timing and power models.

## File Extensions
- `.db` - Compiled Liberty database files
- `.lib` - ASCII Liberty files (uncompressed)

## Content
- Cell timing arcs
- Power consumption models
- Noise models
- Variation data

## Compression Benefits
- Faster loading in EDA tools
- Reduced file size
- Optimized for tool performance

## Usage in Tools
- **Synthesis**: Design Compiler, Genus
- **STA**: PrimeTime, Tempus
- **P&R**: ICC2, Innovus