if [ $# != 3 ]; then
    echo "at least 3 params with filepath, database_name and tab_name" && exit 1
fi
tsv_path=$1
database_name=$2
tab_name=$3


sql=$(python -c "
import sys
sql=\"CREATE TABLE IF NOT EXISTS ${database_name}.${tab_name}(\"
for col in sys.argv[1].split():
    col = col.strip('\"')
    sql += '\n' + '\t' + col + ' VARCHAR(40),'
sql = sql.strip(',') + '\n)'
print(sql)
" "$(head -n 1 $tsv_path)")

echo "$sql"