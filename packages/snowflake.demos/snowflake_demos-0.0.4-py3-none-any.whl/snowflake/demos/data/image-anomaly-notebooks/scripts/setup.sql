/*
Initial Setup - Run the following SQL commands  to create Snowflake objects (database, schema, tables).
*/
use role ACCOUNTADMIN;


create OR REPLACE database PCB_DATASET;
create OR REPLACE warehouse BUILD_WH WAREHOUSE_SIZE=SMALL;

use database PCB_DATASET;
use schema PUBLIC;
use warehouse BUILD_WH;

create compute pool IF NOT EXISTS NOTEBOOK_POOL
min_nodes = 1
max_nodes = 2
instance_family = GPU_NV_S
auto_suspend_secs = 7200;

create stage DATA_STAGE;