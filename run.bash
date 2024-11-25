#!/bin/bash

source optparse.bash

optparse.define short=e long=email desc="Email to leverage OpenAlex polite pool" variable=EMAIL
optparse.define short=d long=date desc="Optional date value to leverage pre-computed results" variable=DATE default=$(date +"%m-%d-%Y")

source $( optparse.build )

if [ -z "$EMAIL" ]; then
    echo "-e, --email can't be empty."
    exit 1
fi

PLOS_PATH="../data/plos"

# 1. Search for documents within mega journals
aius-search \
    --journal plos \
    --output $PLOS_PATH/search_$DATE.parquet

# 2. Plot search result statistics
aius-search-plot \
    --input $PLOS_PATH/search_$DATE.parquet \
    --fig-1 $PLOS_PATH/searchResultPagesPerYear.png \
    --fig-2 $PLOS_PATH/searchResultPagesPerQuery.png

# 3. Filter for papers indexed in OpenAlex
aius-filter-search-results \
    --email "$EMAIL" \
    --filter=field \
    --input $PLOS_PATH/search_$DATE.parquet \
    --output $PLOS_PATH/field_filteredSearch_$DATE.parquet \
    --output-doi $PLOS_PATH/search_doi_$DATE.parquet \
    --output-oa $PLOS_PATH/search_oa_$DATE.parquet

# 4. Download filtered papers
aius-download-papers \
    --input $PLOS_PATH/field_filteredSearch_$DATE.parquet \
    --output $PLOS_PATH/filtered_downloadedPapers_$DATE.parquet

# 5. Transform the downloaded papers into something usable
aius-transform-papers \
    --input $PLOS_PATH/filtered_downloadedPapers_$DATE.parquet \
    --output $PLOS_PATH/transformed_papers_$DATE.parquet

# 6. Evaluation: Count keywords
aius-evaluation-count-keywords \
    --input $PLOS_PATH/transformed_papers_$DATE.parquet \
    --output $PLOS_PATH/evaluation_countKeywords_$DATE.csv

# 7. Plot count keywords
aius-evaluation-plot-keywords \
    --input $PLOS_PATH/evaluation_countKeywords_$DATE.csv \
    --figure $PLOS_PATH/evaluation_countKeywords_$DATE.png \
    --output $PLOS_PATH/evaluation_zeroKeywords_$DATE.csv

# 8. Evaluation: Count tags
aius-evaluation-count-tags \
    --input $PLOS_PATH/transformed_papers_$DATE.parquet \
    --output $PLOS_PATH/evaluation_countTags_$DATE.csv

#9. Plot count tags
aius-evaluation-plot-tags \
    --input $PLOS_PATH/evaluation_countTags_$DATE.csv \
    --figure $PLOS_PATH/evaluation_countTags_$DATE.png
