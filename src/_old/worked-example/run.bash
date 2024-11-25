#!/bin/bash

source optparse.bash

optparse.define short=d long=date desc="Optional date value to leverage pre-computed results" variable=DATE default=$(date +"%m-%d-%Y")
optparse.define short=y long=year desc="Year to search for documents" variable=YEAR default=2014
optparse.define short=s long=sample desc="Sample size" variable=SAMPLE default=0.5

source $( optparse.build )

DATA_PATH="./data/"

# 1. Search through journal
python3.10 getData_plos.py \
    --output $DATA_PATH/searchResponse_${YEAR}_plos_${DATE}.json \
    --year $YEAR

# 2. Sample data
python3.10 sample.py \
    --input $DATA_PATH/searchResponse_${YEAR}_plos_${DATE}.json \
    --output $DATA_PATH/sampled_searchResponse_${YEAR}_plos_${DATE}.json \
    --sample $SAMPLE

# 3. Filter sampled data
python3.10 filterData_plos.py \
    --input $DATA_PATH/sampled_searchResponse_${YEAR}_plos_${DATE}.json \
    --output $DATA_PATH/filtered_sampled_searchResponse_${YEAR}_plos_${DATE}.json

# 4. Plot data
python3.10 plot.py \
    --input $DATA_PATH/filtered_sampled_searchResponse_${YEAR}_plos_${DATE}.json \
    --output $DATA_PATH/filtered_sampled_searchResponse_plot_${YEAR}_plos_${DATE}.png



# # 3. Open data
# python3.10 openSamples.py \
#     --input $DATA_PATH/filter_sampled_searchResponse_${YEAR}_plos_${DATE}.json
