import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsgluedq.transforms import EvaluateDataQuality
from awsglue.dynamicframe import DynamicFrame
import gs_concat
from pyspark.sql import functions as SqlFuncs

def sparkAggregate(glueContext, parentFrame, groups, aggs, transformation_ctx) -> DynamicFrame:
    aggsFuncs = []
    for column, func in aggs:
        aggsFuncs.append(getattr(SqlFuncs, func)(column))
    result = parentFrame.toDF().groupBy(*groups).agg(*aggsFuncs) if len(groups) > 0 else parentFrame.toDF().agg(*aggsFuncs)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Default ruleset used by all target nodes with data quality enabled
DEFAULT_DATA_QUALITY_RULESET = """
    Rules = [
        ColumnCount > 0
    ]
"""

# Script generated for node AWS Glue Data Catalog
AWSGlueDataCatalog_node1753904732398 = glueContext.create_dynamic_frame.from_catalog(database="b3", table_name="b3-carteiraindex_ibov", transformation_ctx="AWSGlueDataCatalog_node1753904732398")

# Script generated for node Rename Field - Codigo
RenameFieldCodigo_node1753902717895 = RenameField.apply(frame=AWSGlueDataCatalog_node1753904732398, old_name="cdigo", new_name="codigo", transformation_ctx="RenameFieldCodigo_node1753902717895")

# Script generated for node Rename Field - Acao
RenameFieldAcao_node1753902734092 = RenameField.apply(frame=RenameFieldCodigo_node1753902717895, old_name="ao", new_name="acao", transformation_ctx="RenameFieldAcao_node1753902734092")

# Script generated for node Concatenate Columns
ConcatenateColumns_node1754001612332 = RenameFieldAcao_node1753902734092.gs_concat(colName="Anomesdia", colList=["year", "month", "day"], spacer=".")

# Script generated for node Aggregate
Aggregate_node1754001787706 = sparkAggregate(glueContext, parentFrame = ConcatenateColumns_node1754001612332, groups = [], aggs = [["Anomesdia", "max"]], transformation_ctx = "Aggregate_node1754001787706")

# Script generated for node Aggregate_Count_Por_acao
Aggregate_Count_Por_acao_node1753280436018 = sparkAggregate(glueContext, parentFrame = ConcatenateColumns_node1754001612332, groups = ["acao", "Anomesdia"], aggs = [["acao", "count"]], transformation_ctx = "Aggregate_Count_Por_acao_node1753280436018")

# Script generated for node Rename Field - Quantidade
RenameFieldQuantidade_node1753902910263 = RenameField.apply(frame=Aggregate_Count_Por_acao_node1753280436018, old_name="`count(acao)`", new_name="Quantidade", transformation_ctx="RenameFieldQuantidade_node1753902910263")

# Script generated for node Amazon S3 - Export tabela final
EvaluateDataQuality().process_rows(frame=RenameFieldQuantidade_node1753902910263, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1753902632086", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
AmazonS3Exporttabelafinal_node1753903547661 = glueContext.getSink(path="s3://b3-dados-pregao-fiap-2025/refined/", connection_type="s3", updateBehavior="UPDATE_IN_DATABASE", partitionKeys=["acao", "Anomesdia"], enableUpdateCatalog=True, transformation_ctx="AmazonS3Exporttabelafinal_node1753903547661")
AmazonS3Exporttabelafinal_node1753903547661.setCatalogInfo(catalogDatabase="b3",catalogTableName="Refined_Papeis_Final")
AmazonS3Exporttabelafinal_node1753903547661.setFormat("glueparquet", compression="snappy")
AmazonS3Exporttabelafinal_node1753903547661.writeFrame(RenameFieldQuantidade_node1753902910263)
job.commit()