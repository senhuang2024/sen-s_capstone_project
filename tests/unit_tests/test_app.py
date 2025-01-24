import os
import sys
import pytest
from unittest import mock
from etl.extract.app import get_weather_data
from unittest.mock import MagicMock, ANY


def test_function_calls_pandas_read_sql_query(mocker):
    mock_read_sql = mocker.patch('pandas.read_sql')
    query = f"""
    SELECT city, date, avgtemp_c, maxtemp_c, mintemp_c, totalprecip_mm, uv_index
    FROM student.de11_fehu_capstone
    WHERE city = 'Bristol'
    ORDER BY date ASC;
    """

    get_weather_data("Bristol")

    mock_read_sql.assert_called_once_with(query, ANY)