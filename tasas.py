import os
import pandas as pd
from sodapy import Socrata
from google.cloud import bigquery

# Socrata
client = Socrata(
    "www.datos.gov.co",
    os.getenv("SOCRATA_TOKEN"),
    username=os.getenv("SOCRATA_USER"),
    password=os.getenv("SOCRATA_PASSWORD")
)

client.timeout = 500

# Consulta principal
results2 = client.get(
    "qzsc-9esp",
    query="""
    SELECT nombre_entidad, fecha_corte,producto_de_cr_dito,plazo_de_cr_dito,tasa_efectiva_promedio,montos_desembolsados,numero_de_creditos,rango_monto_desembolsado,codigo_municipio	
        WHERE Tipo_de_persona = 'Natural' AND tipo_de_cr_dito ='Vivienda' 
                     AND NOT producto_de_cr_dito = 'Construcción de vivienda individual no vis (colocación en pesos)'
                     AND NOT producto_de_cr_dito = 'Construcción de vivienda individual vis (colocación en pesos)'
                     AND NOT producto_de_cr_dito = 'Construcción de vivienda individual no vis (colocación en uvr)'
                     AND NOT producto_de_cr_dito = 'Construcción de vivienda individual vis (colocación en uvr)'
                     AND NOT producto_de_cr_dito = 'Vivienda empleados'
                     AND NOT producto_de_cr_dito = 'Adquisición leasing habitacional no vis (colocación en pesos)'
                     AND NOT producto_de_cr_dito = 'Adquisición leasing habitacional no vis (colocación en uvr)'
                     AND NOT producto_de_cr_dito = 'Adquisición leasing habitacional vis (colocación en pesos)'
                     AND NOT producto_de_cr_dito = 'Adquisición leasing habitacional vis (colocación en uvr)'
                     AND NOT producto_de_cr_dito = 'Libranza adquisición de vivienda diferente de vis (colocación en pesos)'
                     AND NOT producto_de_cr_dito = 'Libranza adquisición de vivienda vis (colocación en pesos)'
        LIMIT 30000
        """
)

results_df2 = pd.DataFrame.from_records(results2)

for col in [
    'tasa_efectiva_promedio',
    'montos_desembolsados',
    'numero_de_creditos'
]:
    results_df2[col] = pd.to_numeric(
        results_df2[col],
        errors='coerce'
    )

results_df2['tipo_de_vivienda'] = 'VIS'
results_df2.loc[
    results_df2['producto_de_cr_dito']
    .str.contains('no vis', case=False, na=False),
    'tipo_de_vivienda'
] = 'NO VIS'

results_df2['tipo_de_credito'] = 'Pesos'
results_df2.loc[
    results_df2['producto_de_cr_dito']
    .str.contains('uvr', case=False, na=False),
    'tipo_de_credito'
] = 'UVR'

# DIVIPOLA
divipola = pd.DataFrame.from_records(
    client.get("gdxc-w37w", limit=2000)
)

df_final = pd.merge(
    results_df2,
    divipola[["cod_mpio", "nom_mpio"]],
    left_on="codigo_municipio",
    right_on="cod_mpio",
    how="left"
)

df_final.drop(columns=["cod_mpio"], inplace=True)

google_creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")

info = json.loads(google_creds_json)
credentials = service_account.Credentials.from_service_account_info(info)
client = bigquery.Client(credentials=credentials, project=info.get("project_id"))

job = client.load_table_from_dataframe(
    df_final,
    "test-n8n-450317.Intereses.Créditos",
    job_config=bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )
)