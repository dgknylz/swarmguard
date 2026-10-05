from __future__ import annotations

import csv
import io
import json

import pyarrow as pa
import pyarrow.parquet as pq

from .experiments import RESULT_METRICS

RUN_COLUMNS = ("method", "seed", *RESULT_METRICS)


def runs_to_csv(result: dict[str, object]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=RUN_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(result["runs"])
    return stream.getvalue().encode("utf-8-sig")


def runs_to_parquet(result: dict[str, object]) -> bytes:
    rows = [{column: run[column] for column in RUN_COLUMNS} for run in result["runs"]]
    table = pa.Table.from_pylist(rows)
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink, compression="snappy")
    return sink.getvalue().to_pybytes()


def manifest_to_json(result: dict[str, object]) -> bytes:
    return json.dumps(result["manifest"], ensure_ascii=False, sort_keys=True, indent=2).encode(
        "utf-8"
    )
