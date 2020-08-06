[![lifecycle](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://www.tidyverse.org/lifecycle/#experimental)
[![NSF-1928366](https://img.shields.io/badge/NSF-1928366-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1928366)

# Broader Impacts Grant Search

Using the NSF Grants stored in the Throughput Database, search for grants with particular keywords, link grants using a matching scheme (title match and year match).  Return linked grants, associated keywords and contacts.  This work is supported by the [National Sciences Foundation's EarthCube](http://earthcube.org) program.

## Contributors

This project is an open project, and contributions are welcome from any individual.  All contributors to this project are bound by a [code of conduct](CODE_OF_CONDUCT.md).  Please review and follow this code of conduct as part of your contribution.

  * [Simon James Goring](http://goring.org) [![orcid](https://img.shields.io/badge/orcid-0000--0002--2700--4605-brightgreen.svg)](https://orcid.org/0000-0002-2700-4605)

### Tips for Contributing

Issues and bug reports are always welcome.  Code clean-up, and feature additions can be done either through pull requests to project forks or branches.

All products of the Throughput Annotation Project are licensed under an [MIT License](LICENSE) unless otherwise noted.

## How to use this repository

A description of the files and directory structure in the repository.

### Workflow Overview

Th project uses grant information from the [National Sciences Foundation](https://www.nsf.gov/awardsearch/download.jsp) that has been processed into the knowledge graph of the Throughput Database.  Using data from xDD trigrams for key terms related to broader outcomes, the workflow attempts to discover grants that may have a significant relation to broader outcomes work.  Multi-institution grants are collected using approximate text matching, and results are then packaged with award IDs, matching terms, award descriptions and contact information for related PIs.

### System Requirements

This project is being developed using Python (v3.8.2) on a system running Linux Mint 20 (kernel 5.7.0-050700-generic). Python requirements are stored in the `requirements.txt` file, generated using the `pipreqs .` command.

### Data Requirements

The project uses data from the [Throughput Database](http://throughputdb.com).

### Key Outputs

This project generates JSON output in the `data/output` folder.

## Metrics

This project is to be evaluated using the following metrics. . .
