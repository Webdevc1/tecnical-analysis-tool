# tecnical-analysis-tool

    This is copied code for a technical screener that I built to learn like the name of the folder suggests.
    I copied this from Part time Larry. I had to work a little harder because that video was 5 years old, 
    so I needed to go through some dependency hell with the TA-Lib and the y-finanace library. 
    
    The Y-finance library now gives the data in a multi-level header form  at which makes it difficult to use talib library
    as is there is a dire need to use the abstract function and then you most likely will need to remove the NaN values
    using dropna() and then do dat.column.get_level_values(). You would also need to use 
    pd.read_csv('__/{}.csv'.format(),header=[0,1], index_col=0).
    You would also need to filter and cleanse the data as some files might be empty leading to segmentation 
    fault errors with the library leading to silent server crashes.
