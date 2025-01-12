# DBNN (Difference Boosting Neural Network)

A GPU-optimized implementation of Difference Boosting Neural Networks for classification tasks.


## Usage

1. Create a configuration file `<dataset_name>.conf` in your working directory:

{
"file_path": "your_data.csv",
"target_column": "your_data_target_name",
"separator": ",",
"has_header": true,
"likelihood_config": {
"feature_group_size": 2,
"max_combinations": 1000
}
}

## Installation

