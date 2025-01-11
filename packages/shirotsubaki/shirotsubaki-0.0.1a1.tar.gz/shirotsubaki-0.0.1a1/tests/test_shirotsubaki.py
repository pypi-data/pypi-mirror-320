import shirotsubaki.report
import shirotsubaki.utils
from shirotsubaki.style import Style as Sty
from shirotsubaki.element import Element as Elm
import os


def create_table():
    tbl = Elm('table')
    thead = Elm('thead')
    tbody = Elm('tbody')

    thead.append(Elm('tr'))
    for _ in range(5):
        thead.inner[-1].append(Elm('th', 'apple'))
        thead.inner[-1].append(Elm('th', 'banana'))
        thead.inner[-1].append(Elm('th', 'cherry'))
    for i in range(20):
        tbody.append(Elm('tr'))
        for _ in range(5):
            tbody.inner[-1].append(Elm('td', 'apple'))
            tbody.inner[-1].append(Elm('td', 'banana'))
            tbody.inner[-1].append(Elm('td', 'cherry'))

    tbl.append(thead)
    tbl.append(tbody)
    div = Elm('div', tbl).set_attr('class', 'table-container')
    return div


def test_lighten_color():
    color = shirotsubaki.utils.lighten_color('#336699')
    assert color == '#99B2CC'


def test_report():
    report = shirotsubaki.report.Report()
    report.style.set('h1', 'color', 'steelblue')
    report.style.add_scrollable_table()
    report.set('title', 'Fruits')
    report.append_to('content', Elm('h1', 'Fruits'))
    report.append_to('content', create_table())
    report.output('my_report.html')
    os.remove('my_report.html')


def test_report_with_tabs():
    report = shirotsubaki.report.ReportWithTabs()
    report.style.add_scrollable_table()
    report.set('title', 'Fruits Fruits Fruits')
    report.add_tab('apple', 'apple apple')
    report.add_tab('banana', 'banana banana')
    report.add_tab('cherry', 'cherry cherry')
    for _ in range(5):
        report.append_to_tab('cherry', Elm('h3', 'table'))
        report.append_to_tab('cherry', create_table())
    report.output('my_report_with_tabs.html')
    os.remove('my_report_with_tabs.html')


def test_style():
    sty0 = Sty({'body': {'color': 'red'}})
    sty1 = Sty({'body': {'background': 'pink'}})
    sty2 = Sty({'body': {'color': 'blue'}})

    sty0 += sty1
    assert sty0['body']['color'] == 'red'
    assert sty0['body']['background'] == 'pink'

    sty0 += sty2
    assert sty0['body']['color'] == 'blue'
    assert sty0['body']['background'] == 'pink'

    sty0.add_scrollable_table()
    print(str(sty0))
