import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import YourModel 
import plotly.express as px
import polars as pl

st.set_page_config(layout="wide", page_title="MDNA YIELD DASHBOARD", initial_sidebar_state = "expanded")

# st.title("MDNA YIELD DASHBOARD")
engine = create_engine('sqlite:///example.db') 
Session = sessionmaker(bind=engine)
session = Session()

@st.cache_data(ttl=7200, show_spinner="Fetching data from DB...")
def load_data():
    query = session.query(YourModel.interface_bin, 
                    YourModel.program_name, 
                    YourModel.visual_id, 
                    YourModel.lot, 
                    YourModel.functional_bin, 
                    YourModel.operation, 
                    YourModel.lots_end_ww,
                    YourModel.test_name,
                    YourModel.test_result,
                    YourModel.parameter_group,
                    YourModel.lvm_address,
                    ).all()

    data = [{'INTERFACE_BIN': result.interface_bin, 
        'PROGRAM_NAME': result.program_name, 
        'VISUAL_ID': result.visual_id, 
        'LOT': result.lot, 
        'FUNCTIONAL_BIN': result.functional_bin, 
        'OPERATION': result.operation, 
        'LOTS_END_WW': result.lots_end_ww,
        'TEST_NAME': result.test_name,
        'TEST_RESULT': result.test_result,
        'PARAMETER_GROUP': result.parameter_group,
        'LVM_ADDRESS': result.lvm_address,
        } for result in query]

    schema = {
        'INTERFACE_BIN': pl.Utf8,
        'PROGRAM_NAME': pl.Utf8,
        'VISUAL_ID': pl.Utf8,
        'LOT': pl.Utf8,
        'FUNCTIONAL_BIN': pl.Utf8,
        'OPERATION': pl.Utf8,
        'LOTS_END_WW': pl.Int32,
        'TEST_NAME': pl.Utf8,
        'TEST_RESULT': pl.Utf8,
        'PARAMETER_GROUP': pl.Utf8,
        'LVM_ADDRESS': pl.Utf8,
    }
    
    return pl.DataFrame(data, schema=schema)

custom_binning_list = ["B44 LTTC"]

custom_binning_dict = {
    "B44 LTTC" : {
        "OPERATION" : ["6262"],
        "FUNCTIONAL_BIN" : ["9140","9141","9142","9143","9144","9145","9146","9147","9148","9149"]
    }
}

## Initial Dataframe
initial_df = load_data()
# df = initial_df.unique(subset=['VISUAL_ID', 'LOT', 'OPERATION'])
filtered_df = initial_df
filter_for_percentage = initial_df

############################## SIDEBAR ##############################

## Sidebar for selecting Interface Bin
sorted_interface_bins = initial_df["INTERFACE_BIN"].unique()
sorted_interface_bins = [int(bin) for bin in sorted_interface_bins]
sorted_interface_bins = sorted(sorted_interface_bins)
sorted_interface_bins = [str(bin) for bin in sorted_interface_bins]
interface_bins_with_all = ['ALL'] + sorted_interface_bins
selected_bins = st.sidebar.multiselect('Select Interface Bins', interface_bins_with_all, default=['ALL'])

## Sidebar for selecting operation
sorted_operations = initial_df["OPERATION"].unique().sort().to_list()
operations_with_all = ['ALL'] + sorted_operations
selected_operations = st.sidebar.multiselect('Select Operations', operations_with_all, default=['ALL'])

st.markdown("""
    <style>
        .stMultiSelect [data-baseweb=select] span{
            max-width: 500px;
        }
    </style>
    """, unsafe_allow_html=True)

## Sidebar for selecting program name
sorted_program_name = initial_df["PROGRAM_NAME"].unique().sort().to_list()
program_name_with_all = ['ALL'] + sorted_program_name
selected_program_name = st.sidebar.multiselect('Select Program Name', program_name_with_all, default=['ALL'])

## Sidebar for selecting Custom Binning
selected_custom_binning = st.sidebar.selectbox('Select Custom Binning', custom_binning_list, index=None, help="If custom binning is selected, interface bin and operation selection will be ignored")

## Sidebar for selecting Work Week
all_work_week = initial_df["LOTS_END_WW"].unique().sort().to_list()
selected_start_ww, selected_end_ww = st.sidebar.select_slider(
    "Select a range of Work Week",
    options=all_work_week,
    value=(all_work_week[-20],all_work_week[-1])
)

if st.sidebar.button('Reset Cache'):
    load_data.clear()
    st.sidebar.write('Cache cleared!')
    df = load_data()


############################## SIDEBAR SELECTION LOGIC ##############################

if selected_custom_binning:
    custom_filters = custom_binning_dict[selected_custom_binning]
    
    if 'OPERATION' in custom_filters:
        filtered_df = filtered_df.filter(pl.col('OPERATION').is_in(custom_filters["OPERATION"]))
        filter_for_percentage = filtered_df
    
    if 'FUNCTIONAL_BIN' in custom_filters:
        filtered_df = filtered_df.filter(pl.col('FUNCTIONAL_BIN').is_in(custom_filters["FUNCTIONAL_BIN"]))
        
    if 'INTERFACE_BIN' in custom_filters:
        filtered_df = filtered_df.filter(pl.col('INTERFACE_BIN').is_in(custom_filters["INTERFACE_BIN"]))
        filter_for_percentage = filtered_df
        
else:
    if 'ALL' not in selected_bins:
        filtered_df = filtered_df.filter(pl.col('INTERFACE_BIN').is_in(selected_bins))

    if 'ALL' not in selected_operations:
        filtered_df = filtered_df.filter(pl.col('OPERATION').is_in(selected_operations))
        filter_for_percentage = filtered_df

if 'ALL' not in selected_program_name:
    filtered_df = filtered_df.filter(pl.col('PROGRAM_NAME').is_in(selected_program_name))
    filter_for_percentage = filtered_df

filtered_df = filtered_df.filter(pl.col("LOTS_END_WW").is_between(selected_start_ww,selected_end_ww))
filter_for_percentage = filtered_df
    
tab1, tab2, tab3 = st.tabs(["Yield Summary", "Fail Signature","String Signature"])

with tab1:
    filtered_df1 = filtered_df.unique(subset=['VISUAL_ID', 'LOT', 'OPERATION'])
    filter_for_percentage = filtered_df1

    all_work_weeks = pl.DataFrame(initial_df['LOTS_END_WW'].unique().sort())
    work_week_counts = filtered_df1.group_by('LOTS_END_WW').agg(pl.len().alias('Count'))
    work_week_counts = work_week_counts.sort(by=["LOTS_END_WW"])
    # work_week_counts = all_work_weeks.join(work_week_counts, on='LOTS_END_WW', how='left').fill_null(0).sort(by="LOTS_END_WW")

    st.subheader('Count per Work Week')

    fig = px.bar(work_week_counts, x='LOTS_END_WW', y='Count', text='Count')
    fig.update_traces(textposition='outside')
    fig.update_xaxes(type='category')

    total_count = work_week_counts['Count'].sum()
    total_row = pl.DataFrame(
        {'LOTS_END_WW': ['Total'], 'Count': [total_count]},
        schema={"LOTS_END_WW": pl.String, "Count": pl.UInt32})
    work_week_counts = work_week_counts.cast({"LOTS_END_WW": pl.String})
    work_week_counts_table = pl.concat([work_week_counts, total_row])

    st.plotly_chart(fig)

    with st.expander("View Data Table"):
        st.write(work_week_counts_table)
        
    total_counts_per_week_all = filter_for_percentage.group_by('LOTS_END_WW').agg(pl.col("LOTS_END_WW").count().alias("Total Count"))
    
    percentage_df = filtered_df1.group_by(['LOTS_END_WW', 'INTERFACE_BIN']).agg(pl.len().alias('Count')).sort(['LOTS_END_WW', 'INTERFACE_BIN'])
    
    percentage_df = percentage_df.join(total_counts_per_week_all, on='LOTS_END_WW', how='left')
    # all_unique_bin = percentage_df['INTERFACE_BIN'].unique().cast({"INTERFACE_BIN" : pl.UInt32}).sort
    
    percentage_df = percentage_df.with_columns((((pl.col('Count') / pl.col('Total Count')) * 100).round(2)).alias('Percentage'))
    percentage_df = percentage_df.with_columns(pl.format("{}.2f %", pl.col('Percentage')).alias('Percentage Text'))
    
    sorted_interface_bins = [int(bin_name) for bin_name in percentage_df['INTERFACE_BIN'].unique().to_list()]
    sorted_interface_bins.sort()
    sorted_interface_bins = [str(bin_name) for bin_name in sorted_interface_bins]
    
    st.subheader('Percentage of Interface Bin per Work Week')
    
    fig_line = px.line(percentage_df, x='LOTS_END_WW', y='Percentage', color='INTERFACE_BIN', 
                    text='Percentage',
                    category_orders={'INTERFACE_BIN': sorted_interface_bins})
    fig_line.update_xaxes(type='category')
    fig_line.update_traces(mode='lines+markers+text', textposition='top center')
    st.plotly_chart(fig_line)
    
    pivot_df = percentage_df.pivot(index='INTERFACE_BIN', on='LOTS_END_WW', values='Percentage')
    sorted_pivot = pivot_df.cast({"INTERFACE_BIN" : pl.UInt32})
    sorted_pivot = sorted_pivot.sort("INTERFACE_BIN")
    with st.expander("View Data Table"):
        st.dataframe(sorted_pivot)
        
    ############################## FUNCTIONAL BIN ##############################
        
    functional_percentage_df = filtered_df1.group_by(['LOTS_END_WW', 'FUNCTIONAL_BIN']).agg(pl.len().alias("Count"))
    functional_percentage_df = functional_percentage_df.join(total_counts_per_week_all, on='LOTS_END_WW', how='left')
    functional_percentage_df = functional_percentage_df.with_columns((((pl.col('Count') / pl.col('Total Count')) * 100).round(2)).alias('Percentage'))
    
    sorted_functional_bins = [int(bin_name) for bin_name in functional_percentage_df['FUNCTIONAL_BIN'].unique().to_list()]
    sorted_functional_bins.sort()
    sorted_functional_bins = [str(bin_name) for bin_name in sorted_functional_bins]
    
    st.subheader('Percentage of Functional Bin per Work Week')
        
    sorted_work_week_array = [int(ww) for ww in functional_percentage_df['LOTS_END_WW'].unique().to_list()]
    sorted_work_week_array.sort()
    sorted_work_week_array = [str(ww) for ww in sorted_work_week_array]
    
    functional_percentage_df = functional_percentage_df.sort(["LOTS_END_WW","FUNCTIONAL_BIN"])
    
    @st.cache_resource
    def render_functional_bin_chart(functional_percentage_df,sorted_work_week_array,sorted_functional_bins):
        fig_functional_line = px.line(functional_percentage_df, 
                                    x='LOTS_END_WW', y='Percentage', 
                                    color='FUNCTIONAL_BIN', text='Percentage', 
                                    category_orders={"LOTS_END_WW":sorted_work_week_array,
                                    "FUNCTIONAL_BIN":sorted_functional_bins},
                                    render_mode="SVG"
                                    )

        fig_functional_line.update_xaxes(type='category')
        fig_functional_line.update_traces(mode='lines+markers+text', textposition='top center')
        return st.plotly_chart(fig_functional_line)
    
    plotly_graph = render_functional_bin_chart(functional_percentage_df,sorted_work_week_array,sorted_functional_bins)
    
    pivot_df2 = functional_percentage_df.pivot(index='FUNCTIONAL_BIN', on='LOTS_END_WW', values='Percentage')
    pivot_df2 = pivot_df2.cast({"FUNCTIONAL_BIN":pl.UInt32})
    pivot_df2 = pivot_df2.sort(["FUNCTIONAL_BIN"])
    with st.expander("View Data Table"):
        st.write(pivot_df2)
    
    with st.expander("View Functional Bin Distribution"):
        functional_bin_counts = filtered_df1.group_by("FUNCTIONAL_BIN").agg(pl.len().alias("Count"))
        functional_bin_counts = functional_bin_counts.sort(["FUNCTIONAL_BIN","Count"])
        fig_functional_pie = px.pie(functional_bin_counts, names='FUNCTIONAL_BIN', values='Count', title='Functional Bin Distribution')
        fig_functional_pie.update_layout(height=500)
        st.plotly_chart(fig_functional_pie)

        st.dataframe(functional_bin_counts, hide_index=True)
        
    program_percentage_df = filtered_df1.group_by(['PROGRAM_NAME', 'INTERFACE_BIN']).agg(pl.len().alias("Count"))
    total_counts_per_program = filter_for_percentage.group_by('PROGRAM_NAME').agg(pl.len().alias("Total Count"))
    program_percentage_df = program_percentage_df.join(total_counts_per_program, on='PROGRAM_NAME', how='left')
    program_percentage_df = program_percentage_df.with_columns((((pl.col('Count') / pl.col('Total Count')) * 100).round(2)).alias('Percentage'))
    
    sorted_program_name = [program_name for program_name in program_percentage_df['PROGRAM_NAME'].unique().to_list()]
    sorted_program_name.sort()
    
    sorted_interface_bins = [int(bin_name) for bin_name in program_percentage_df['INTERFACE_BIN'].unique().to_list()]
    sorted_interface_bins.sort()
    sorted_interface_bins = [str(bin_name) for bin_name in sorted_interface_bins]

    program_percentage_df = program_percentage_df.sort(["PROGRAM_NAME","Count"])
    
    st.subheader('Percentage of Interface Bin per Program Name')
    
    fig_functional_program_line = px.line(program_percentage_df, 
                                        x='PROGRAM_NAME', y='Percentage', 
                                        color='INTERFACE_BIN', text='Percentage',
                                        category_orders={"PROGRAM_NAME":sorted_program_name,'INTERFACE_BIN': sorted_interface_bins})
    fig_functional_program_line.update_xaxes(type='category')
    fig_functional_program_line.update_traces(mode='lines+markers+text', textposition='top center')
    st.plotly_chart(fig_functional_program_line)
    
    pivot_df3 = program_percentage_df.pivot(index='INTERFACE_BIN', on='PROGRAM_NAME', values='Percentage', sort_columns= True)
    pivot_df3 = pivot_df3.cast({"INTERFACE_BIN": pl.UInt32})
    pivot_df3 = pivot_df3.sort("INTERFACE_BIN")
    
    with st.expander("View Data Table"):
        st.write(pivot_df3)
    
with tab2:
    st.subheader('Pattern Failure Distribution')
    st.text('Choose desired bins to see the chart clearer')
    
    filtered_df2 = filtered_df.filter(pl.col("PARAMETER_GROUP") == "PATTERN")
    filtered_df2 = filtered_df2.unique(subset=[
        'VISUAL_ID', 
        'LOT', 
        'OPERATION',
        'INTERFACE_BIN',
        'PROGRAM_NAME',
        'FUNCTIONAL_BIN',
        'LOTS_END_WW',
        'TEST_NAME',
        'TEST_RESULT',
        'PARAMETER_GROUP',
        'LVM_ADDRESS',
        ])
    filtered_df2 = filtered_df2.select(["TEST_NAME","TEST_RESULT","LVM_ADDRESS"])
    count_df2 = filtered_df2.group_by(["TEST_NAME", "TEST_RESULT", "LVM_ADDRESS"]).agg(pl.len().alias("Count"))
    test_name_counts = filtered_df2.group_by(["TEST_NAME"]).agg(pl.len().alias("Count"))
    
    fig = px.pie(test_name_counts, names='TEST_NAME', values='Count')
    fig.update_layout(height=600)
    st.plotly_chart(fig)
    
    st.subheader('Fail Signature Details')
    st.dataframe(count_df2,
                 hide_index=True,
                 row_height=70)
        
with tab3:
    st.subheader('String Signature Distribution')
    st.text('Choose desired bins to see the chart clearer')
    
    filtered_df3 = filtered_df.filter(pl.col("PARAMETER_GROUP") == "STRING")
    filtered_df3 = filtered_df3.unique(subset=[
        'VISUAL_ID', 
        'LOT', 
        'OPERATION',
        'INTERFACE_BIN',
        'PROGRAM_NAME',
        'FUNCTIONAL_BIN',
        'LOTS_END_WW',
        'TEST_NAME',
        'TEST_RESULT',
        'PARAMETER_GROUP',
        'LVM_ADDRESS',
        ])
    
    filtered_df3 = filtered_df3.select(["TEST_NAME","TEST_RESULT"])
    count_df3 = filtered_df3.group_by(["TEST_NAME", "TEST_RESULT"]).agg(pl.len().alias("Count"))
    test_name_counts = filtered_df3.group_by(["TEST_NAME"]).agg(pl.len().alias("Count"))
    
    fig = px.pie(test_name_counts, names='TEST_NAME', values='Count')
    fig.update_layout(height=600)
    st.plotly_chart(fig)
    
    st.subheader('String Signature Details')
    st.dataframe(count_df3,
                 hide_index=True,
                 row_height=70)