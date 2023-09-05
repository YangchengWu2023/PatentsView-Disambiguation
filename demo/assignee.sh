# load and deal with data from the following link:
# https://s3.amazonaws.com/data.patentsview.org/download/g_assignee_not_disambiguated.tsv.zip

# or you could download it by choosing "g_assignee_not_disambiguated" under https://patentsview.org/download/data-download-tables
PASSWORD=aeolus

filepath=/home/ubuntu/workspace/PatentsView-Disambiguation/resources/g_assignee_not_disambiguated.tsv
database_name=granted
tab_name=tmp_$(basename $filepath | sed "s#\.tsv##g")
create_sql=$(. ./gen_tab_by_tsv.sh $filepath $database_name $tab_name)
load_sql="LOAD DATA LOCAL INFILE '$filepath'
INTO TABLE $database_name.$tab_name
FIELDS TERMINATED BY '\t'
IGNORE 1 ROWS;
"

# LOAD may failed, see this: https://stackoverflow.com/a/65548915
mysql --local-infile=1 --connect-expired-password -u root -p"$PASSWORD" <<EOF
$create_sql;
$load_sql
quit
EOF

## Note: The following step need to be modified manually
target_table=rawassignee
# | uuid | patent_id | assignee_id | rawlocation_id | type | name_first | name_last | organization | sequence |
create_target_sql="
CREATE TABLE $database_name.$target_table(
    uuid VARCHAR(30),
    patent_id VARCHAR(40),
    assignee_id VARCHAR(40),
    rawlocation_id VARCHAR(40),
    type VARCHAR(40),
    name_first VARCHAR(40),
    name_last VARCHAR(40),
    organization VARCHAR(40),
    sequence VARCHAR(40)
)
"
echo "$create_target_sql"
# patent_id assignee_sequence assignee_id raw_assignee_individual_name_first raw_assignee_individual_name_last raw_assignee_organization assignee_type rawlocation_id
get_sql="
TRUNCATE TABLE $database_name.$target_table;
INSERT INTO $database_name.$target_table
SELECT 
    @rn:= @rn+1 as rn, 
    TRIM(BOTH '\"' FROM patent_id),
    TRIM(BOTH '\"' FROM assignee_id),
    TRIM(BOTH '\"' FROM rawlocation_id),
    TRIM(BOTH '\"' FROM assignee_type),
    TRIM(BOTH '\"' FROM raw_assignee_individual_name_first),
    TRIM(BOTH '\"' FROM raw_assignee_individual_name_last),
    TRIM(BOTH '\"' FROM raw_assignee_organization),
    TRIM(BOTH '\"' FROM assignee_sequence)
FROM $database_name.$tab_name, (SELECT @rn := 0) AS x
LIMIT 3000000;
"
echo "$get_sql"


