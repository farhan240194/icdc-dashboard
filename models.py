from sqlalchemy import DateTime, Float, create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create an engine with a file-based SQLite database
engine = create_engine('sqlite:///example.db', echo=True)

# Define a model
Base = declarative_base()

class YourModel(Base):
    __tablename__ = 'raw_data'  # Replace with your actual table name

    # Define columns
    id = Column(Integer, Sequence('raw_data_id_seq'), primary_key=True)
    visual_id = Column(String)  # Assuming VISUAL_ID is unique
    substructure_id = Column(String)
    sort_lot = Column(String)
    sort_wafer = Column(String)
    sort_x = Column(Integer)
    sort_y = Column(Integer)
    lotfromfs = Column(String)
    opergroup = Column(String)
    lot = Column(String)
    lots_end_date_time = Column(DateTime)
    program_name = Column(String)
    dev_rev_step = Column(String)
    facility = Column(String)
    lots_end_ww = Column(String)
    lots_start_date_time = Column(DateTime)
    module_level_unit_id = Column(String)
    operation = Column(String)
    summary_name = Column(String)
    within_lots_sequence_num = Column(Integer)
    lots_seq_key = Column(String)
    lato_start_ww = Column(String)
    unit_testing_seq_key = Column(String)
    interface_bin = Column(Integer)
    data_bin = Column(Integer)
    functional_total_bin = Column(Integer)
    data_total_bin = Column(Integer)
    interface_total_bin = Column(Integer)
    functional_bin = Column(Integer)
    test_name = Column(String)
    distinctive_value = Column(String)
    categorizing_value = Column(String)
    test_result_numeric = Column(Float)
    test_result = Column(String)
    test_result_order_num = Column(Integer)
    string_distinctive_value = Column(String)
    parameter_group = Column(String)
    lvm_address = Column(String)

# Create tables in the database
Base.metadata.create_all(engine)