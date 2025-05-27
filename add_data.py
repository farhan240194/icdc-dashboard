import pandas as pd
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import DateTime, Float, create_engine
from models import MDNADB
from dateutil.parser import parse

engine = create_engine('sqlite:///data.db', echo=True)
# Assuming 'engine' is already created as per your SQLAlchemy setup
Session = sessionmaker(bind=engine)
session = Session()

# Read the CSV file
csv_file_path = 'WLW_A15_6262_DRV_RESET_EMCA-DRV_RESET_ICM-DRV_RESET_MCP_WW5-WW15.csv'  # Replace with your actual CSV file path
df = pd.read_csv(csv_file_path)

# Iterate over the rows in the DataFrame and insert them into the database
for index, row in df.iterrows():
    # Create an instance of YourModel
    record = MDNADB(
        visual_id=row['VISUAL_ID'],
        substructure_id=row['SUBSTRUCTURE_ID'],
        sort_lot=row['SORT_LOT'],
        sort_wafer=row['SORT_WAFER'],
        sort_x=row['SORT_X'],
        sort_y=row['SORT_Y'],
        lotfromfs=row['LOTFROMFS'],
        opergroup=row['OPERGROUP'],
        lot=row['Lot'],
        lots_end_date_time=parse(row['LOTS End Date Time']),
        program_name=row['Program Name'],
        dev_rev_step=row['DevRevStep'],
        facility=row['Facility'],
        lots_end_ww=row['LOTS End WW'],
        lots_start_date_time=parse(row['LOTS Start Date Time']),
        module_level_unit_id=row['Module Level Unit Id'],
        operation=row['Operation'],
        summary_name=row['Summary Name'],
        within_lots_sequence_num=row['Within LOTS Sequence Num'],
        lots_seq_key=row['LOTS Seq Key'],
        lato_start_ww=row['LATO Start WW'],
        unit_testing_seq_key=row['Unit Testing Seq Key'],
        interface_bin=row['INTERFACE_BIN'],
        data_bin=row['DATA_BIN'],
        functional_total_bin=row['FUNCTIONAL_TOTAL_BIN'],
        data_total_bin=row['DATA_TOTAL_BIN'],
        interface_total_bin=row['INTERFACE_TOTAL_BIN'],
        functional_bin=row['FUNCTIONAL_BIN'],
        test_name=row['TEST_NAME'],
        distinctive_value=row['DISTINCTIVE_VALUE'],
        categorizing_value=row['CATEGORIZING_VALUE'],
        test_result_numeric=row['TEST_RESULT_NUMERIC'],
        test_result=row['TEST_RESULT'],
        test_result_order_num=row['TEST_RESULT_ORDER_NUM'],
        string_distinctive_value=row['STRING_DISTINCTIVE_VALUE'],
        parameter_group=row['PARAMETER_GROUP'],
        lvm_address=row['LVM_ADDRESS']
    )
    
    # Add the record to the session
    session.add(record)

# Commit the session to save the records in the database
session.commit()

# Close the session
session.close()