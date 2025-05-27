from sqlalchemy import DateTime, Float, create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///data.db', echo=True)

Base = declarative_base()

class MDNADB(Base):
    __tablename__ = 'raw_data'  
    
    id = Column(Integer, Sequence('raw_data_id_seq'), primary_key=True)
    visual_id = Column(String) 
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
    decoded_status = Column(String)
    decoded_group = Column(String)
    decoded_fail_info = Column(String)

# Create tables in the database
Base.metadata.create_all(engine)