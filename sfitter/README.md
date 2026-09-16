## SFitter :blush:

### Installation

```sh
# clone the repository
git clone https://github.com/heidelberg-hepml/SFitterAgents
# then install in dev mode
cd sfitter
pip install --editable .
```

### Usage

Run SFitter using parameter file:
```sh
sfitter run params/test.yaml --verbose
```

Repeat fitting for given run:
```sh
sfitter fit yyyymmdd_hhmmss_run_name --verbose
```

Repeat plotting for given run using the saved fit results:
```sh
sfitter plot yyyymmdd_hhmmss_run_name
```
