#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

"""count - сĸольĸо раз встречается URL, абсолютное значение
count_perc - сĸольĸо раз встречается URL, в процентнах относительно общего числа запросов
time_sum - суммарный $request_time для данного URL'а, абсолютное значение
time_perc - суммарный $request_time для данного URL'а, в процентах относительно общего $request_time всех запросов
time_avg - средний $request_time для данного URL'а
time_max - маĸсимальный $request_time для данного URL'а
time_med - медиана $request_time для данного URL'а"""

import bz2
import csv
import fnmatch
import gzip
import os
import re
from itertools import tee

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "file_name": "nginx-access-ui.log",
}

COL_NAMES = (
    'remote_addr', 'remote_user', 'http_x_real_ip', 'time_local', 'plus', 'method', 'request', 'protocol',
    'status', 'body_bytes_sent', 'http_referer',
    'http_user_agent', 'http_x_forwarded_for', 'http_X_REQUEST_ID', 'http_X_RB_USER', 'request_time')


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


def request_time_summ(summ, dict_seq):
    for d in dict_seq:
        summ = summ + d['request_time']
        yield summ


def all_requests(new_list, dict_seq):
    for d in dict_seq:
        if d['request'] not in new_list:
            new_list.append(d['request'])
            yield new_list


def log_parser(lines):
    logpats = r'(\S+) (\S+)  (\S+) \[(?P<datetime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] "(\S+) (\S+) (\S+)" (\S+) (\S+) "(\S+)" "(\S+)" "(\S+)" "(\S+)" "(\S+)" (\S+)'
    logpat = re.compile(logpats, re.IGNORECASE)

    groups = (logpat.match(line) for line in iter(lines))
    tuples = (g.groups() for g in groups if g)

    log = (dict(zip(COL_NAMES, t)) for t in tuples)
    log = field_map(log, "status", int)
    log = field_map(log, "body_bytes_sent", lambda s: int(s) if s != '-' else 0)
    log = field_map(log, "request_time", lambda s: float(s) if s != '-' else 0)

    return log


def creation_result(g_log):
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
    df = pd.DataFrame.from_records(g_log)

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


def save_log_to_csv(log):
    with open('./reports/report.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=COL_NAMES)
        writer.writeheader()

        for xx in log:
            writer.writerow(xx)


def save_log_to_report_html(result):
    with open('./reports/report.html', 'w', newline='', encoding='utf-8') as f:
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


def data_test_():
    """набор строк для тестирования"""

    line1 = '1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET ' \
            '/api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" ' \
            '"1498697422-32900793-4708-9752770" "-" 0.133 '
    line2 = '2.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET /api/1/photogenic_banners/list/?server_n ' \
            'HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.233 '
    line3 = '2.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET /api/1/photogenic_banners/list/?server_n ' \
            'HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.333 '
    line4 = '2.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET /api/1/photogenic_banners/list/?server_n ' \
            'HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.433 '

    lines = [line1, line2, line3, line4]

    return lines


def test_pars_data():
    """ тест с несколькми строками лога """
    log_lines = data_test_()
    log = log_parser(log_lines)
    result = creation_result(log)
    # save_log_to_csv(result)
    save_log_to_report_html(result)
    assert (len(result) == 2)


def main(*args):
    """рабочий код. читает логи из файла:"""

    log_dir = config['LOG_DIR']
    filenames = gen_find("nginx-*.log*", log_dir)
    logfiles = gen_open(filenames)
    log_lines = gen_cat(logfiles)

    log = log_parser(log_lines)
    result = creation_result(log)
    # save_log_to_csv(result)
    save_log_to_report_html(result)


if __name__ == "__main__":
    main()
