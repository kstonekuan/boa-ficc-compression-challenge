echo "----------Bank of America Code to Connect FICC Challenge----------"

while getopts s:e: flag
do
    case "${flag}" in
        s) start=${OPTARG};;
        e) end=${OPTARG};;
        *) echo "provide testcase range with -s -e"
            exit 1;;
    esac
done

if [ -n "$start" ]
then 
    if [ -n "$end" ]
    then
        for i in $(seq $start $end)
        do
            python3 main.py $i
            echo "Testcase $i completed"
            if [ $i != $end ]
            then
                echo "------------------------------------------------------------------"
            fi
        done
    else
        echo "provide testcase range with -s -e"
        exit 1
    fi
else
    echo "provide testcase range with -s -e"
    exit 1
fi

echo "----------Bank of America Code to Connect FICC Challenge----------"
