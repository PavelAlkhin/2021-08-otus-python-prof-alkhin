#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

import bz2
import csv
import datetime
import fnmatch
import gzip
import json
import os
import re
import logging
import sys
import time
from optparse import OptionParser
from shutil import move, copy
from tempfile import mkstemp

CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "file_name": "nginx-access-ui.log",
    "NGINX_LOG_DIR": "./nginx_log"
}

COL_NAMES = (
    'remote_addr', 'remote_user', 'http_x_real_ip', 'time_local', 'plus', 'method', 'request', 'protocol',
    'status', 'body_bytes_sent', 'http_referer',
    'http_user_agent', 'http_x_forwarded_for', 'http_X_REQUEST_ID', 'http_X_RB_USER', 'request_time')

LOG_PAT = r'(\S+) (\S+)  (\S+) \[(?P<datetime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] "(\S+) (' \
          r'\S+) (\S+)" (\S+) (\S+) "(\S+)" "(\S+)" "(\S+)" "(\S+)" "(\S+)" (\S+)'


def gen_find(file_pat, top):
    for path, dir_list, file_list in os.walk(top):
        for name in fnmatch.filter(file_list, file_pat):
            yield os.path.join(path, name)


def gen_open(file_names):
    for name in file_names:
        if name.endswith(".gz"):
            yield gzip.open(name)
        elif name.endswith(".bz2"):
            yield bz2.BZ2File(name)
        else:
            yield open(name)


def gen_cat(sources):
    for s in sources:
        for item in s:
            yield item


def field_map(dict_seq, name, func):
    for d in dict_seq:
        d[name] = func(d[name])
        yield d


def return_line_str(line):
    if isinstance(line, str):
        return line
    else:
        return line.decode()


def log_parser(lines):
    logpats = LOG_PAT
    logpat = re.compile(logpats, re.IGNORECASE)

    log = []
    count_converted = 0
    count_fault = 0
    for l in lines:
        line = return_line_str(l)
        try:
            group_line = logpat.match(line)
            tuple_line = group_line.groups()
            dict_line = dict(zip(COL_NAMES, tuple_line))
            log.append(dict_line)
            count_converted += 1
        except:
            count_fault += 1

    logging.info(f'succesfully match: {count_converted}')
    logging.info(f'cannot match: {count_fault}')

    log = field_map(log, "status", int)
    log = field_map(log, "body_bytes_sent", lambda s: int(s) if s != '-' else 0)
    log = field_map(log, "request_time", lambda s: float(s) if s != '-' else 0)

    return log


def creation_result_with_pandas(log_list):
    import pandas as pd
    """
    *count - сĸольĸо раз встречается URL, абсолютное значение
    *count_perc - сĸольĸо раз встречается URL, в процентнах относительно общего числа запросов
    *time_sum - суммарный $request_time для данного URL'а, абсолютное значение
    time_perc - суммарный $request_time для данного URL'а, в процентах относительно общего $request_time всех запросов
    *time_avg - средний $request_time для данного URL'а
    *time_max - маĸсимальный $request_time для данного URL'а
    *time_med - медиана $request_time для данного URL'а
    """

    df = pd.DataFrame.from_records(log_list)

    all_counts_req = len(df)
    df_count_req = df['request'].value_counts().to_dict()
    sum_request_time = df.agg({'request_time': sum})['request_time']

    df_time_max = df.groupby('request').agg({'request_time': ['max']})
    df_time_sum = df.groupby('request').agg({'request_time': [sum]})

    df_time_sum = df_time_sum[:20]

    df_time_med = df.groupby('request').median()
    df_time_avg = df.groupby('request').mean()
    df_time_sum_sorted = df_time_sum.sort_values(by=('request_time', 'sum'), ascending=False).drop_duplicates()[:20]

    result = []

    # считаем count_perc
    for key, value in df_time_sum_sorted.iterrows():
        time_sum = value['request_time']['sum']
        time_max = df_time_max.loc[key]['request_time']['max']
        time_med = df_time_med.loc[key]['request_time']
        time_avg = df_time_avg.loc[key]['request_time']

        count = df_count_req.get(key)
        count_perc = count / all_counts_req * 100

        time_perc = time_sum / sum_request_time * 100

        row = {
            'request': key,
            'count': count,
            'count_perc': count_perc,
            'time_sum': time_sum,
            'time_perc': time_perc,
            'time_avg': time_avg,
            'time_max': time_max,
            'time_med': time_med,
        }

        result.append(row)

    return result


def creation_result_pure(log_list):
    """
    *count - сĸольĸо раз встречается URL, абсолютное значение
    *count_perc - сĸольĸо раз встречается URL, в процентнах относительно общего числа запросов
    *time_sum - суммарный $request_time для данного URL'а, абсолютное значение
    time_perc - суммарный $request_time для данного URL'а, в процентах относительно общего $request_time всех запросов
    *time_avg - средний $request_time для данного URL'а
    *time_max - маĸсимальный $request_time для данного URL'а
    *time_med - медиана $request_time для данного URL'а
    """
    result = []

    unique_requests_list = []
    all_counts = 0
    all_time = 0
    requests_obj = {}
    for line in log_list:
        all_counts += 1
        all_time += line['request_time']

        try:
            list_times = requests_obj[line['request']].copy()
            list_times.append(line['request_time'])
        except KeyError:
            list_times = [line['request_time']]

        requests_obj.update({line['request']: list_times})
        if line['request'] in unique_requests_list:
            continue
        unique_requests_list.append(line['request'])

    for key in requests_obj:
        time_list = requests_obj[key]
        count = len(time_list)
        time_sum = 0
        time_max = 0

        for time in time_list:
            time_sum += time
            if time_max < time:
                time_max = time
        count_med = int(count / 2)
        time_med = time_list[count_med]

        count_perc = (count / all_counts) * 100
        time_perc = (time_sum / all_time) * 100
        time_avg = time_sum / count

        row = fill_in_result(count, count_perc, key, time_avg, time_max, time_med, time_perc, time_sum)

        result.append(row)

    return result


def fill_in_result(count, count_perc, key, time_avg, time_max, time_med, time_perc, time_sum):
    row = {
        'request': key,
        'count': count,
        'count_perc': count_perc,
        'time_sum': time_sum,
        'time_perc': time_perc,
        'time_avg': time_avg,
        'time_max': time_max,
        'time_med': time_med,
    }

    return row


def save_log_to_csv(log):
    with open('./reports/report.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=COL_NAMES)
        writer.writeheader()

        for xx in log:
            writer.writerow(xx)


def save_log_to_report_html(result):
    rep_dir = CONFIG['REPORT_DIR']
    file_name = f'{rep_dir}/report.html'
    with open(file_name, 'w', newline='', encoding='utf-8') as f:
        f.write("""
                <html>
                <head>
                    <link href="http://mottie.github.io/tablesorter/css/theme.default.css" rel="stylesheet">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/css/bootstrap.min.css" 
                        rel="stylesheet" 
                        integrity="sha384-F3w7mX95PdgyTmZZMECAngseQB83DfGTowi0iMjiWaeVhAn4FJkqJByhZMI3AhiU" 
                        crossorigin="anonymous">
                    <script type="text/javascript" 
                        src="http://cdnjs.cloudflare.com/ajax/libs/jquery/1.9.1/jquery.min.js">
                    </script>
                    <script type="text/javascript" 
                        src="http://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.9.1/jquery.tablesorter.min.js">
                    </script>

                    <script>
                        $(function(){
                          $("#myTable").tablesorter({widgets: ['zebra']});
                        });
                    </script>                
                </head>
                <body class="table-striped table-hover">
                <div class="container-fluid">
                <p>Query Analysis Report</p>
                <table id="myTable" class="tablesorter table">
                  <thead>
                    <tr>
                      <th>Request</th>
                      <th>count</th>
                      <th>count perc</th>
                      <th>time sum</th>
                      <th>time perc</th>
                      <th>time avg</th>
                      <th>time max</th>
                      <th>time med</th>
                    </tr>
                  </thead>
                  <tbody>
                """)

        for xx in result:
            f.write('<tr>')
            f.write(f'<td>{xx["request"]}</td>')
            f.write(f'<td>{xx["count"]}</td>')
            f.write(f'<td>{xx["count_perc"]}</td>')
            f.write(f'<td>{xx["time_sum"]}</td>')
            f.write(f'<td>{xx["time_perc"]}</td>')
            f.write(f'<td>{xx["time_avg"]}</td>')
            f.write(f'<td>{xx["time_max"]}</td>')
            f.write(f'<td>{xx["time_med"]}</td>')
            f.write('</td>')
            f.write('</tr>')

        f.write(""" """)

        f.write("""  
                    </tbody>
                  </table>
                  </div>
                </body>
                </html>
                """)


def save_log_to_report_html_2(result):
    rep_dir = CONFIG['REPORT_DIR']
    file_name = 'report.html'
    substring = json.dumps(result)
    fill_in_replace_file(file_name, rep_dir, '$table_json', substring)


def fill_in_replace_file(source_file_path, rep_dir, pattern, substring):
    d = datetime.datetime.today()
    day = d.day
    month = d.month
    year = d.year
    fh, target_file_path = mkstemp()
    with open(target_file_path, 'w') as target_file:
        with open(source_file_path, 'r') as source_file:
            for line in source_file:
                target_file.write(line.replace(pattern, substring))
    target_file.close()
    # os.remove(source_file_path)
    copy(target_file_path, f'{rep_dir}/report-{year}.{month}.{day}.html')


def main():
    """рабочий код. читает логи из файла:"""
    try:

        log_dir = CONFIG['NGINX_LOG_DIR']
        filenames = gen_find("nginx-*.log*", log_dir)
        file = gen_open(filenames)
        log_lines = gen_cat(file)

        log = log_parser(log_lines)

        # with pandas
        # result = creation_result_with_pandas(log)

        # with pure python
        result = creation_result_pure(log)

        # if we want to save csv
        # save_log_to_csv(result)

        save_log_to_report_html_2(result)

    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    op = OptionParser()
    op.add_option('-l', '--log', action='store', default='./log/log_analizer.log')
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, encoding='utf-8', level=logging.DEBUG)
    logging.info(f'#### started at {datetime.datetime.today()} [')
    main()
    logging.info(f'#### ended at {datetime.datetime.today()} ]')
