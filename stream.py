import streamlit as lit
import cx_oracle
import altair
import pandas
import subprocess

subprocess.call(shlex.split(f"streamlit hello --global.developmentMode=false"))
