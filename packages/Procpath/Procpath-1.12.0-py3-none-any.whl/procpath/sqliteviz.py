import hashlib
import http.server
import io
import json
import logging
import textwrap
import zipfile
from functools import partial
from pathlib import Path
from urllib.request import urlopen

from . import procret


__all__ = 'get_visualisation_bundle', 'install_sqliteviz', 'serve_dir', 'symlink_database'

logger = logging.getLogger(__package__)


def install_sqliteviz(zip_url: str, target_dir: Path):
    response = urlopen(zip_url)
    with zipfile.ZipFile(io.BytesIO(response.read())) as z:
        z.extractall(target_dir)

    bundle = json.dumps(get_visualisation_bundle(), sort_keys=True)
    (target_dir / 'inquiries.json').write_text(bundle)


def _get_line_chart_config(title: str) -> dict:
    return {
        'data': [{
            'meta': {'columnNames': {'x': 'ts', 'y': 'value'}},
            'mode': 'lines',
            'type': 'scatter',
            'x': None,
            'xsrc': 'ts',
            'y': None,
            'ysrc': 'value',
            'transforms': [{
                'groups': None,
                'groupssrc': 'pid',
                'meta': {'columnNames': {'groups': 'pid'}},
                'styles': [],
                'type': 'groupby',
            }],
        }],
        'frames': [],
        'layout': {
            'autosize': True,
            'title': {'text': title},
            'xaxis': {
                'autorange': True,
                'range': [],
                'type': 'date'
            },
            'yaxis': {
                'autorange': True,
                'range': [],
                'type': 'linear'
            },
        },
    }


def _get_sqliteviz_only_charts():
    return [
        # Process Timeline PID
        {
            'id': 'csfOTEpzlFfYz7OUc2aGI',
            'createdAt': '2023-09-03T12:00:00Z',
            'name': 'Process Timeline, PID',
            'query': textwrap.dedent('''
                WITH RECURSIVE tree(pid, ppid, pid_comm) AS (
                    SELECT stat_pid, stat_ppid, stat_pid || ' ' || stat_comm
                    FROM record
                    GROUP BY 1
                    UNION
                    SELECT pid, stat_ppid, stat_pid || ' ' || stat_comm
                    FROM record, tree
                    WHERE record.stat_pid = tree.ppid
                ), lookup AS (
                    SELECT pid, group_concat(pid_comm, ' / ') path_to_root
                    FROM tree
                    GROUP BY 1
                )
                SELECT
                    ts * 1000 AS ts,
                    stat_pid,
                    stat_pid || ' ' || stat_comm AS pid_comm,
                    iif(
                        length(cmdline) > 0,
                        substr(cmdline, 0, 75) || iif(length(cmdline) > 75, '...', ''),
                        stat_comm
                    ) || '<br>' || path_to_root AS cmd
                FROM record
                JOIN lookup ON stat_pid = pid
            ''').strip(),
            'viewType': 'chart',
            'viewOptions': {
                'data': [{
                    'type': 'scattergl',
                    'mode': 'markers',
                    'meta': {'columnNames': {'x': 'ts', 'y': 'stat_pid', 'text': 'cmd'}},
                    'transforms': [{
                        'type': 'groupby',
                        'styles': [],
                        'meta': {'columnNames': {'groups': 'pid_comm'}},
                        'groups': None,
                        'groupssrc': 'pid_comm',
                    }],
                    'y': None,
                    'ysrc': 'stat_pid',
                    'x': None,
                    'xsrc': 'ts',
                    'text': None,
                    'textsrc': 'cmd',
                    'marker': {'size': 12, 'maxdisplayed': 0},
                    'line': {'width': 3},
                    'hoverinfo': 'x+text',
                }],
                'layout': {
                    'xaxis': {
                        'type': 'date',
                        'range': [],
                        'autorange': True,
                    },
                    'yaxis': {
                        'type': 'category',
                        'range': [],
                        'autorange': True,
                        'showticklabels': False,
                    },
                    'title': {'text': 'Process Timeline, PID'},
                    'hovermode': 'closest',
                },
                'frames': [],
            },
        },
        # Process Timeline CPU
        {
            'id': '4PBtpi7inEAe-yjtRHCi0',
            'createdAt': '2023-09-03T12:00:00Z',
            'name': 'Process Timeline, CPU',
            'query': textwrap.dedent('''
                WITH RECURSIVE tree(pid, ppid, pid_comm) AS (
                    SELECT stat_pid, stat_ppid, stat_pid || ' ' || stat_comm
                    FROM record
                    GROUP BY 1
                    UNION
                    SELECT pid, stat_ppid, stat_pid || ' ' || stat_comm
                    FROM record, tree
                    WHERE record.stat_pid = tree.ppid
                ), path_lookup AS (
                    SELECT pid, group_concat(pid_comm, ' / ') path_to_root
                    FROM tree
                    GROUP BY 1
                ), cpu_diff AS (
                    SELECT
                        ts,
                        stat_pid,
                        stat_ppid,
                        stat_priority,
                        stat_comm,
                        cmdline,
                        stat_utime + stat_stime - LAG(stat_utime + stat_stime) OVER (
                            PARTITION BY stat_pid
                            ORDER BY record_id
                        ) tick_diff,
                        ts - LAG(ts) OVER (
                            PARTITION BY stat_pid
                            ORDER BY record_id
                        ) ts_diff
                    FROM record
                ), record_ext AS (
                    SELECT
                        *,
                        100.0 * tick_diff / (
                            SELECT value FROM meta WHERE key = 'clock_ticks'
                        ) / ts_diff cpu_usage
                    FROM cpu_diff
                    WHERE tick_diff IS NOT NULL
                )
                SELECT
                    ts * 1000 AS ts,
                    stat_pid,
                    stat_pid || ' ' || stat_comm AS pid_comm,
                    power(1.02, -r.stat_priority) priority_size,
                    cpu_usage,
                    iif(
                        length(cmdline) > 0,
                        substr(cmdline, 0, 75) || iif(length(cmdline) > 75, '...', ''),
                        stat_comm
                    )
                    || '<br>' || path_to_root
                    || '<br>' || 'CPU, %: ' || printf('%.2f', cpu_usage)
                    || '<br>' || 'priority: ' || stat_priority AS cmd
                FROM record_ext r
                JOIN path_lookup p ON r.stat_pid = p.pid
                -- Tune the following CPU usage inequality for a clearer figure
                WHERE cpu_usage > 0
            ''').strip(),
            'viewType': 'chart',
            'viewOptions': {
                'data': [{
                    'type': 'scattergl',
                    'mode': 'markers',
                    'meta': {
                        'columnNames': {
                            'text': 'cmd',
                            'x': 'ts',
                            'y': 'stat_pid',
                            'marker': {
                                'color': 'cpu_usage',
                                'size': 'priority_size',
                            },
                        },
                    },
                    'y': None,
                    'ysrc': 'stat_pid',
                    'x': None,
                    'xsrc': 'ts',
                    'text': None,
                    'textsrc': 'cmd',
                    'marker': {
                        'maxdisplayed': 0,
                        'color': None,
                        'colorsrc': 'cpu_usage',
                        'size': None,
                        'sizesrc': 'priority_size',
                        'sizeref': 0.00667,
                        'sizemode': 'area',
                        'showscale': True,
                        'colorbar': {'title': {'text': 'CPU, %'}},
                    },
                    'line': {'width': 3},
                    'hoverinfo': 'x+text',
                }],
                'layout': {
                    'xaxis': {
                        'type': 'date',
                        'range': [],
                        'autorange': True,
                    },
                    'yaxis': {
                        'type': 'category',
                        'range': [],
                        'autorange': True,
                        'showticklabels': False,
                    },
                    'title': {'text': 'Process Timeline, CPU'},
                    'hovermode': 'closest',
                },
                'frames': [],
            },
        },
        # Process Tree
        {
            'id': '3XXe7a80GvD6Trk9FyXRz',
            'name': 'Process Tree',
            'createdAt': '2023-09-03T12:00:00Z',
            'query': textwrap.dedent('''
                WITH lookup(pid, num) AS (
                    SELECT stat_pid, ROW_NUMBER() OVER(ORDER BY stat_pid) - 1
                    FROM record
                    GROUP BY 1
                ), nodes AS (
                  SELECT
                    stat_pid,
                    -- Opt-in for special bare column processing to prefer the
                    -- first values (the minimum value is not used per se)
                    MIN(ts),
                    stat_ppid,
                    stat_pid || ' ' || stat_comm AS pid_comm,
                    iif(
                        length(cmdline) > 0,
                        substr(cmdline, 0, 75) || iif(length(cmdline) > 75, '...', ''),
                        stat_comm
                    ) cmd
                  FROM record
                  GROUP BY 1
                )
                SELECT p.num p_num, pp.num pp_num, pid_comm, cmd, 1 value
                FROM nodes
                JOIN lookup p ON stat_pid = p.pid
                LEFT JOIN lookup pp ON stat_ppid = pp.pid
                ORDER BY p.num
            ''').strip(),
            'viewType': 'chart',
            'viewOptions': {
                'data': [
                    {
                        'type': 'sankey',
                        'mode': 'markers',
                        'node': {'labelsrc': 'pid_comm'},
                        'link': {
                            'valuesrc': 'value',
                            'targetsrc': 'p_num',
                            'sourcesrc': 'pp_num',
                            'labelsrc': 'cmd'
                        },
                        'meta': {
                            'columnNames': {
                                'node': {'label': 'pid_comm'},
                                'link': {
                                    'source': 'pp_num',
                                    'target': 'p_num',
                                    'value': 'value',
                                    'label': 'cmd'
                                }
                            }
                        },
                        'orientation': 'h',
                        'hoverinfo': 'name',
                        'arrangement': 'freeform'
                    }
                ],
                'layout': {
                    'xaxis': {'range': [], 'autorange': True},
                    'yaxis': {'range': [], 'autorange': True},
                    'autosize': True,
                    'title': {'text': 'Process Tree'}
                },
                'frames': []
            }
        },
        # Total Memory Consumption
        {
            'id': 'boSs15w7Endl5V9bABjXv',
            'createdAt': '2023-09-03T12:00:00Z',
            'name': 'Total Resident Set Size, MiB',
            'query': textwrap.dedent('''
                WITH lookup(ts, total) AS (
                    SELECT
                        ts,
                        SUM(stat_rss)
                            / 1024.0 / 1024 * (SELECT value FROM meta WHERE key = 'page_size')
                    FROM record
                    GROUP BY 1
                )
                SELECT
                    record.ts * 1000 ts,
                    -- Comment "stat_pid" group and uncomment this to have coarser grouping
                    -- CASE
                    --     WHEN cmdline LIKE '%firefox%' THEN '1. firefox'
                    --     WHEN cmdline LIKE '%chromium%' THEN '2. chromium'
                    --     ELSE '3. other'
                    -- END "group",
                    stat_pid || ' ' || stat_comm "group",
                    SUM(stat_rss)
                        / 1024.0 / 1024 * (SELECT value FROM meta WHERE key = 'page_size') value,
                    'total: ' || round(total, 1) || ' MiB' total
                FROM record
                JOIN lookup ON record.ts = lookup.ts
                GROUP BY 1, 2
                ORDER BY 2
            ''').strip(),
            'viewType': 'chart',
            'viewOptions': {
                'data': [{
                    'type': 'scatter',
                    'mode': 'lines',
                    'meta': {'columnNames': {'x': 'ts', 'y': 'rss'}},
                    'transforms': [{
                        'type': 'groupby',
                        'groupssrc': 'group',
                        'groups': None,
                        'styles': [],
                        'meta': {'columnNames': {'groups': 'group'}},
                    }],
                    'stackgroup': 1,
                    'x': None,
                    'xsrc': 'ts',
                    'y': None,
                    'ysrc': 'value',
                    'text': None,
                    'textsrc': 'total',
                    'hoverinfo': 'x+text',
                }],
                'layout': {
                    'xaxis': {
                        'type': 'date',
                        'range': [],
                        'autorange': True,
                    },
                    'yaxis': {
                        'type': 'linear',
                        'range': [],
                        'autorange': True,
                        'separatethousands': True,
                    },
                    'title': {'text': 'Total Resident Set Size, MiB'},
                    'hovermode': 'closest',
                },
                'frames': []
            },
        }
    ]


def get_visualisation_bundle() -> dict:
    """Get Sqliteviz import-able visualisation bundle."""

    inquiries = []
    result = {'version': 2, 'inquiries': inquiries}

    for query in procret.registry.values():
        query_text = query.get_short_query(ts_as_milliseconds=True)
        inquiries.append({
            'id': hashlib.md5(query_text.encode()).hexdigest()[:21],
            'createdAt': '2023-09-03T12:00:00Z',
            'name': query.title,
            'query': textwrap.dedent(query_text).strip(),
            'viewType': 'chart',
            'viewOptions': _get_line_chart_config(query.title),
        })

    inquiries.extend(_get_sqliteviz_only_charts())

    return result


class HttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        # Disable cache validation based on modified timestamp of the
        # file because it's a symlink pointing to different files, and
        # next one can easily be older than current one
        if self.path == '/db.sqlite':
            del self.headers['If-Modified-Since']

        return super().send_head()

    def end_headers(self):
        if self.path == '/db.sqlite':
            # The "no-store" response directive indicates that caches
            # should not store this response. No point to try to cache
            # big database files
            self.send_header('Cache-Control', 'no-store')
        else:
            # The "no-cache" response directive indicates that the
            # response can be stored in caches, but the response must
            # be validated with the origin server before each reuse
            self.send_header('Cache-Control', 'no-cache')

        super().end_headers()


def serve_dir(bind: str, port: int, directory: str):
    server_cls = http.server.ThreadingHTTPServer
    handler_cls = partial(HttpRequestHandler, directory=directory)
    with server_cls((bind, port), handler_cls) as httpd:
        httpd.serve_forever()


def symlink_database(database_file: str, sqliteviz_dir: Path) -> Path:
    db_path = Path(database_file).absolute()
    if not db_path.exists():
        raise FileNotFoundError

    sym_path = sqliteviz_dir / 'db.sqlite'
    sym_path.unlink(missing_ok=True)
    sym_path.symlink_to(db_path)
    return sym_path
