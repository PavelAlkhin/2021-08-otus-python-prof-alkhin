import log_analyzer


def data_test_():
    """набор строк для тестирования"""

    line16 = '1.99.174.176 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25949705 HTTP/1.1" 200 1262 "-" ' \
             '"python-requests/2.8.1" "-" "1498697422-32900793-4708-9752770" "-" 0.133 '
    line1 = '1.138.198.128 -  - [30/Jun/2017:03:28:22 +0300] "GET /api/v2/banner/25949705 HTTP/1.1" 200 1262 "-" ' \
            '"python-requests/2.8.1" "-" "1498782502-440360380-4708-10531110" "4e9627334" 0.673 '
    line2 = '1.138.198.128 -  - [30/Jun/2017:03:28:22 +0300] "GET ' \
            '/api/v2/banner/25949705 HTTP/1.1" 200 9214 "-" ' \
            '"python-requests/2.8.1" "-" "1498782502-440360380-4707-10488739" "4e9627334" 0.059 '
    line3 = '1.138.198.128 -  - [30/Jun/2017:03:28:22 +0300] "GET ' \
            '/api/v2/banner/25949705" 200 9137 "-" ' \
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


def test_pars_data_with_pandas():
    """ тест с несколькми строками лога """
    log_lines = data_test_()
    log = log_analyzer.log_parser(log_lines)
    result = log_analyzer.creation_result_with_pandas(log)
    # save_log_to_csv(result)
    log_analyzer.save_log_to_report_html(result)
    assert (len(result) == 12)


def test_pars_data_pure():
    log_lines = data_test_()
    log = log_analyzer.log_parser(log_lines)
    result = log_analyzer.creation_result_pure(log)
    # save_log_to_csv(result)
    log_analyzer.save_log_to_report_html(result)
    assert (len(result) == 10)
