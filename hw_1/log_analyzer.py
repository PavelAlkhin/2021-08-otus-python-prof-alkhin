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
import os
import re
import logging

CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "file_name": "nginx-access-ui.log",
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

    line16 = '1.99.174.176 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/1/photogenic_banne HTTP/1.1" 200 1262 "-" ' \
             '"python-requests/2.8.1" "-" "1498697422-32900793-4708-9752770" "-" 0.133 '
    line1 = '1.138.198.128 -  - [30/Jun/2017:03:28:22 +0300] "GET /api/v2/banner/25949705 HTTP/1.1" 200 1262 "-" ' \
            '"python-requests/2.8.1" "-" "1498782502-440360380-4708-10531110" "4e9627334" 0.673 '
    line2 = '1.138.198.128 -  - [30/Jun/2017:03:28:22 +0300] "GET ' \
            '/api/v2/banner/25020502/statistic/?date_from=2016-10-20&date_to=2017-06-30 HTTP/1.1" 200 9214 "-" ' \
            '"python-requests/2.8.1" "-" "1498782502-440360380-4707-10488739" "4e9627334" 0.059 '
    line3 = '1.138.198.128 -  - [30/Jun/2017:03:28:22 +0300] "GET ' \
            '/api/v2/banner/25020518/statistic/?date_from=2016-10-20&date_to=2017-06-30 HTTP/1.1" 200 9137 "-" ' \
            '"python-requests/2.8.1" "-" "1498782502-440360380-4707-10488741" "4e9627334" 0.077 '
    line4 = '1.170.209.160 -  - [30/Jun/2017:03:28:23 +0300] "GET /export/appinstall_raw/2017-06-30/ HTTP/1.0" 200 ' \
            '25652 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.0.12) Gecko/2009070611 Firefox/3.0.12 (' \
            '.NET CLR 3.5.30729)" "-" "-" "-" 0.002 '
    line5 = '1.170.209.160 -  - [30/Jun/2017:03:28:23 +0300] "GET /export/appinstall_raw/2017-07-01/ HTTP/1.0" 404 ' \
            '162 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.0.12) Gecko/2009070611 Firefox/3.0.12 (.NET ' \
            'CLR 3.5.30729)" "-" "-" "-" 0.001 '
    line6 = '1.138.198.128 -  - [30/Jun/2017:03:28:23 +0300] "GET ' \
            '/api/v2/banner/25020539/statistic/?date_from=2016-10-20&date_to=2017-06-30 HTTP/1.1" 200 9134 "-" ' \
            '"python-requests/2.8.1" "-" "1498782503-440360380-4707-10488743" "4e9627334" 0.054 '
    line7 = '1.169.137.128 -  - [30/Jun/2017:03:28:23 +0300] "GET /api/v2/group/1240146/banners HTTP/1.1" 200 994 "-" ' \
            '"Configovod" "-" "1498782502-2118016444-4707-10488733" "712e90144abee9" 0.643 '
    line9 = '1.159.236.144 -  - [30/Jun/2017:03:28:23 +0300] "GET ' \
            '/api/v2/banner/3118447/statistic/conversion/?date_from=2007-01-01&date_to=2017-06-29 HTTP/1.1" 200 328 ' \
            '"-" "Mozilla/5.0" "-" "1498782497-708638932-4707-10488660" "0ae935e4e7a96" 5.246 '
    line8 = '1.195.44.0 -  - [30/Jun/2017:03:28:23 +0300] "GET ' \
            '/api/v2/internal/revenue_share/service/276/partner/77624766/statistic/v2?date_from=2017-06-24&date_to' \
            '=2017-06-30&date_type=day HTTP/1.0" 200 2615 "-" "-" "-" "1498782502-1775774396-4707-10488742" ' \
            '"0d9e6ca2ba" 0.329 '
    line10 = '1.138.198.128 -  - [30/Jun/2017:03:28:23 +0300] "GET ' \
             '/api/v2/banner/25187824/statistic/?date_from=2016-10-20&date_to=2017-06-30 HTTP/1.1" 200 8237 "-" ' \
             '"python-requests/2.8.1" "-" "1498782503-440360380-4707-10488745" "4e9627334" 0.059 '
    line11 = '1.169.137.128 -  - [30/Jun/2017:03:28:23 +0300] "GET /api/v2/banner/5960595 HTTP/1.1" 200 992 "-" ' \
             '"Configovod" "-" "1498782503-2118016444-4707-10488744" "712e90144abee9" 0.147 '
    line12 = '1.199.4.96 -  - [30/Jun/2017:03:28:23 +0300] "GET ' \
             '/api/v2/banner/17572305/statistic/?date_from=2017-06-30&date_to=2017-06-30 HTTP/1.1" 200 115 "-" ' \
             '"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498782503-3800516057-4707-10488747" ' \
             '"c5d7e306f36c" 0.083 '
    line13 = '1.138.198.128 -  - [30/Jun/2017:03:28:23 +0300] "GET /api/v2/banner/25187824 HTTP/1.1" 200 1260 "-" ' \
             '"python-requests/2.8.1" "-" "1498782503-440360380-4707-10488749" "4e9627334" 0.203 '
    line14 = '1.195.44.0 -  - [30/Jun/2017:03:28:23 +0300] "GET ' \
             '/api/v2/internal/revenue_share/service/276/partner/77757278/statistic/v2?date_from=2017-06-24&date_to' \
             '=2017-06-30&date_type=day HTTP/1.0" 200 12 "-" "-" "-" "1498782503-1775774396-4707-10488750" ' \
             '"0d9e6ca2ba" 0.144 '
    line15 = '1.138.198.128 -  - [30/Jun/2017:03:28:23 +0300] "GET /api/v2/banner/25949683 HTTP/1.1" 200 1261 "-" ' \
             '"python-requests/2.8.1" "-" "1498782502-440360380-4707-10488740" "4e9627334" 0.863 '

    lines = [line1, line2, line3, line4, line5, line6, line7, line8, line9, line10, line11, line12, line13, line14,
             line15, line16]

    return lines


def test_pars_data():
    """ тест с несколькми строками лога """
    log_lines = data_test_()
    log = log_parser(log_lines)
    result = creation_result_with_pandas(log)
    # save_log_to_csv(result)
    save_log_to_report_html(result)
    assert (len(result) == 12)


def main(*args):
    """рабочий код. читает логи из файла:"""
    log_dir = CONFIG['LOG_DIR']
    filenames = gen_find("nginx-*.log*", log_dir)
    file = gen_open(filenames)
    log_lines = gen_cat(file)

    log = log_parser(log_lines)
    result = creation_result_with_pandas(log)
    # save_log_to_csv(result)
    save_log_to_report_html(result)


if __name__ == "__main__":
    logging.basicConfig(filename='./log/log_analizer.log', encoding='utf-8', level=logging.DEBUG)
    logging.info(f'#### started at {datetime.datetime.today()} [')
    main()
    logging.info(f'#### ended at {datetime.datetime.today()} ]')
