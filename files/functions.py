# Import modules
import os
import urllib
from urllib.parse import urlparse
from IPython.display import display, JSON, HTML
import subprocess
import shutil
import json
import pandas as pd
import requests
import io
import pygame
import cairosvg
import PIL.Image
import ipywidgets as widgets
import psycopg2
from sqlalchemy import create_engine
from fhirpathpy import evaluate
from fhirpathpy.models import models
from dotenv import load_dotenv


# Define functions
def change_working_dir(working_dir):
    pwd = os.getcwd()

    if pwd == working_dir:
        print("INFO: Already in the {} project directory...".format(working_dir))
    else:
        print("INFO: Changing to the {} working directory...".format(working_dir))
        try:
            os.chdir(working_dir)
        except FileNotFoundError:
            print("ERROR: {} does not exist...".format(working_dir))


def render_svg(svg_data, scale):
    svg_data = cairosvg.svg2svg(svg_data, dpi=(96 / scale))
    png_data = cairosvg.svg2png(svg_data)
    byte_io = io.BytesIO(png_data)
    return pygame.image.load(byte_io)


def create_dir(target_dir):
    # requires import os
    if os.path.exists(target_dir):
        print("INFO: {} exists...".format(target_dir))
    else:
        print("INFO: Creating directory {}...".format(target_dir))
        os.mkdir(target_dir)


def extract_specific_resourcetype_data(entry_data: str, resourceType: str):
    extracted_data = [
        d.get("resource")
        for d in entry_data
        if d.get("resource", {}).get("resourceType") == resourceType
    ]

    return extracted_data


def fhir_path_query(data, fhir_path: str):
    r4_model = models["r4"]
    result = evaluate(data, fhir_path, {}, r4_model)

    return list(map(str, result))


def get_test_from_sdtm_terminology(codelist_code: str, iteme_code: str) -> str:
    endpoint_url = f"https://api.library.cdisc.org/api/mdr/ct/packages/sdtmct-2025-03-28/codelists/{codelist_code}/terms/{iteme_code}"

    headers = {
        "api-key": os.getenv("CDISC_API_KEY"),
        "accept": "application/json",
    }

    response = requests.get(endpoint_url, headers=headers)
    response_json = response.json()

    return response_json["submissionValue"]


def get_domain_var_hrefs(sdtm_domain: str) -> list:
    headers = {
        "api-key": os.getenv("CDISC_API_KEY"),
        "accept": "application/json",
    }
    endpoint_url = f"https://api.library.cdisc.org/api/mdr/sdtmig/3-4/datasets/{sdtm_domain}/variables"

    response = requests.get(endpoint_url, headers=headers)

    var_list = response.json().get("_links").get("datasetVariables")
    var_hrefs = [dict["href"] for dict in var_list]

    return var_hrefs


def get_vars_md(domain_var_hrefs: list) -> list:
    headers = {
        "api-key": os.getenv("CDISC_API_KEY"),
        "accept": "application/json",
    }

    vars_md = []
    for href in domain_var_hrefs:
        endpoint_url = f"https://api.library.cdisc.org/api{href}"
        response = requests.get(endpoint_url, headers=headers)
        response_json = response.json()

        vars_md.append(
            {
                "core": response_json.get("core"),
                "name": response_json.get("name"),
                "ordinal": int(response_json.get("ordinal")),
                "simpleDatatype": response_json.get("simpleDatatype"),
            }
        )

    return vars_md


def create_blank_df(sdtm_domain: str) -> pd.DataFrame:
    lb_vars = get_domain_var_hrefs(sdtm_domain)
    var_md = get_vars_md(lb_vars)
    md_mandatory_vars = [d for d in var_md if d["core"] != "Perm"]
    md_mandatory_vars_ = sorted(md_mandatory_vars, key=lambda x: x["ordinal"])

    vars = [d.get("name") for d in md_mandatory_vars_]

    df = pd.DataFrame(columns=vars)
    return df


def get_study_id() -> str:
    raise NotImplementedError("get_study_id is not yet implemented. Please provide the required logic.")


def get_dataset_by_vlm_id(
    metadata_df: pd.DataFrame,
    vlm_id: str,
    lb_blank_df: pd.DataFrame,
    research_study: str,
    observations: str,
) -> pd.DataFrame:
    temp_metadata_df = metadata_df[metadata_df["vlm_group_id"] == vlm_id]

    lbtestcd_codelist_code = temp_metadata_df[
        temp_metadata_df["sdtm_variable"] == "LBTESTCD"
    ]["codelist_code"].iloc[0]
    lbtest_codelist_code = temp_metadata_df[
        temp_metadata_df["sdtm_variable"] == "LBTEST"
    ]["codelist_code"].iloc[0]

    lbtestcd_bc_id = temp_metadata_df[temp_metadata_df["sdtm_variable"] == "LBTESTCD"][
        "bc_id"
    ].iloc[0]
    lbtest_bc_id = temp_metadata_df[temp_metadata_df["sdtm_variable"] == "LBTEST"][
        "bc_id"
    ].iloc[0]

    lbtestcd = get_test_from_sdtm_terminology(lbtestcd_codelist_code, lbtestcd_bc_id)
    lbtest = get_test_from_sdtm_terminology(lbtest_codelist_code, lbtest_bc_id)

    filtered_metadata_df = temp_metadata_df[
        temp_metadata_df["fhirPath_origin"].notnull()
    ]
    temp_df = lb_blank_df
    for index, row in filtered_metadata_df.iterrows():
        sdtm_variable = row["sdtm_variable"]
        temp_df[sdtm_variable] = fhir_path_query(observations, row["fhirPath_origin"])

    temp_df["STUDYID"] = fhir_path_query(
        research_study, "ResearchStudy.identifier.where(use='usual').value"
    )[0]
    temp_df["LBTESTCD"] = lbtestcd
    temp_df["LBTEST"] = lbtest
    temp_df["DOMAIN"] = "LB"

    return temp_df
