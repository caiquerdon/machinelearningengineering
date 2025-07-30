import boto3
import os
import re

def lambda_handler(event, context):
    glue = boto3.client('glue')
    s3 = boto3.client('s3')

    bucket = 'b3-dados-pregao-fiap-2025'
    prefix = 'b3/index=IBOV/'
    job_name = os.environ['GLUE_JOB_NAME']

    print("🔎 Listando objetos do S3 para encontrar última partição...")

    paginator = s3.get_paginator('list_objects_v2')
    result = paginator.paginate(Bucket=bucket, Prefix=prefix)

    partitions = []

    for page in result:
        for obj in page.get('Contents', []):
            key = obj['Key']
            match = re.search(r'year=(\d{4})/month=(\d{2})/day=(\d{2})', key)
            if match:
                year, month, day = match.groups()
                partitions.append((year, month, day))

    if not partitions:
        print("Nenhuma partição encontrada.")
        return { 'statusCode': 404, 'body': 'Nenhuma partição encontrada no S3.' }

    # Ordena as partições pela data mais recente
    latest = sorted(partitions, reverse=True)[0]
    year, month, day = latest

    print(f"Última partição encontrada: {year}-{month}-{day}")

    # Inicia o Glue Job visual com os argumentos da partição
    response = glue.start_job_run(
        JobName=job_name,
        Arguments={
            '--year': year,
            '--month': month,
            '--day': day
        }
    )

    print(f"🚀 Glue Job {job_name} iniciado com sucesso!")
    return {
        'statusCode': 200,
        'body': f'Glue Job {job_name} iniciado com sucesso para {year}-{month}-{day}.'
    }