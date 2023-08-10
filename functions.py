import pandas as pd
import sys
from matplotlib import pyplot as plt

def create_master_turnstile_file(filenames, output_file):
    """
    Combine all the file to a single master file
    
    Args:
    - filenames list: List of files to be concatenated to a single one
    - output_file str: Output file to save the combined result
    
    Returns:
    None
    """
    with open(output_file, 'w') as master_file:
        # create header
        master_file.write('C/A,UNIT,SCP,STATION, LINENAME, DIVISION, \
        DATEn,TIMEn,DESCn,ENTRIESn,EXITSn\n')
        for filename in filenames:
            # write file content to master_file
            with open(filename) as f:
                # skip first line because header is already specified in line 14
                next(f)
                for line in f:
                    master_file.write(line)

def filter_by_regular(filename):
    """
    Filters data containing only DESCn = "REGULAR"
    
    Args:
    - filename str: TXT file which contains turnstile data
    
    Returns:
    - turnstile_data pandas.DataFrame: Filtered data frame containing only rows
    for which column `DESCn` = "REGULAR"
    """
    # read
    turnstile_data = pd.read_csv(filename, error_bad_lines=False)
    turnstile_data = turnstile_data.query(" DESCn == 'REGULAR' ")
    return turnstile_data

def get_hourly_entries(df):
    """
    Creates a new column and stores hourly entries in it.
    
    Args:
    - df pandas.DataFrame: Data frame from which the new column will be
    created
    
    Returns:
    - df pandas.DataFrame: Same data frame with "ENTRIESn_hourly" column added
    """
    
    # calculate hourly difference for entries
    df["ENTRIESn_hourly"] = pd.to_numeric(df["ENTRIESn"]) - \
                            pd.to_numeric(df["ENTRIESn"].shift())
    # nan handling
    df["ENTRIESn_hourly"] = df["ENTRIESn_hourly"].fillna(1).astype(int)

    return df

def get_hourly_exits(df):
    """
    Creates a new column and stores hourly exits in it.
    
    Args:
    - df pandas.DataFrame: Data frame from which the new column will be
    created
    
    Returns:
    - df pandas.DataFrame: Same data frame with "EXITSn_hourly" column added
    """
    
    # calculate hourly difference for entries
    df["EXITSn_hourly"] = pd.to_numeric(df["EXITSn"]) - \
                          pd.to_numeric(df["EXITSn"].shift())
    
    # nan handling
    df["EXITSn_hourly"] = df["EXITSn_hourly"].fillna(1).astype(int)
    return df


def mapper(input_file, output_file):
    """
    Parses "UNIT" and "ENTRIESn_hourly" for each row and writes to output file
    """
    with open(input_file) as f_in, open(output_file, 'w') as f_out:
        next(f_in)
        for line in f_in:
            observation = line.strip().split(",")
            if len(observation) >= 7:
                unit = observation[2]
                entriesn_hourly = observation[12]
                print("%s\t%s" % (unit, entriesn_hourly), file=f_out)

def reducer():
    """
    Reads mapper result from stdin and prints "UNIT" and total hourly entries \
    for that unit
    Since UNIT appear at multiple lines in mapper result, we will take sum of \
    all entries for each UNIT
    """
    old_key = None
    entries_count = 0

    for line in sys.stdin:
        
        row = line.strip().split("\t")
        
        if len(row) != 2:
            continue
        
        this_key, this_entry = row
        try:
            if (old_key) and (old_key != this_key):
                print("%s\t%s" % (old_key, entries_count))
                old_key = this_key
                entries_count = 0
            old_key = this_key
            entries_count += float(this_entry)
        except:
            continue
    print("%s\t%s" %(old_key, entries_count))
        

filenames = ['turnstile_030617.txt', 'turnstile_100617.txt', 'turnstile_170617.txt', 'turnstile_240617.txt']
output_file = 'master_turnstile_file.csv'
create_master_turnstile_file(filenames, output_file)

output_data=filter_by_regular(r"C:\Users\fairy\OneDrive\Desktop\DSProj\master_turnstile_file.csv")
print("Step2:\n",output_data)

dataFrame= get_hourly_entries(output_data)
print("Step3:\n",dataFrame)

dataFrame2= get_hourly_exits(output_data)
print("Step4\n",dataFrame2)

dataFrame2.to_csv('dataFrame2.csv')

input_file1 = 'dataFrame2.csv'
output_file1 = 'mapper_result.txt'
mapper(input_file1, output_file1)

sys.stdin = open('mapper_result.txt')
sys.stdout = open('reducer_result.txt', 'w')
reducer()

# plt.scatter(dataFrame2['UNIT'],dataFrame2['ENTRIESn_hourly'])
# plt.xlabel('UNIT')
# plt.ylabel('ENTRIESn_hourly')
# plt.show()

dataFrame2['UNIT'].hist()
plt.show()

# f=dataFrame2['UNIT'].value_counts()
# f.plot(kind='bar')
# plt.show()

# fa=pd.crosstab(dataFrame2['UNIT'],dataFrame2['ENTRIESn_hourly'])
# fa.plot(kind='bar')
