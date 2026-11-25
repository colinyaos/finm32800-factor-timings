# Manually-Created Data

This folder is used to hold manually created data that cannot be easily replicated.
You may keep data here and keep it under version control if it is small enough.
Keeping this data under version control can provide some peace of mind
that the data is not inadvertently modified.
Also, keep in mind that Git LFS is a good option if the data is large.

## `anomaly_map.csv`

The 50 anomalies of Haddad, Kozak and Santosh (2020), one row each, in the
order of the paper's Table 3. We build these anomalies ourselves from CRSP and
Compustat; Kozak's posted deciles (`_data/kozak_ft_monthly/`, pulled by
`src/pull_kozak.py`) are only for validating them. Definitions follow
`anom_doc.pdf`, which comes with Kozak's data.

Columns:

- `paper_order`, `paper_name`: the row number and name in Table 3.
- `kozak_name`: the anomaly's name in Kozak's files (`ret10_<kozak_name>.csv`
  and so on).
- `long_leg`: `high` or `low`, the end of the characteristic that sits in p10,
  the long decile, or `check` where it is not established. `anom_doc.pdf`
  gives the direction for none of the 50. Size (`low`), Value (A) and Value (M)
  (`high`) are set from Kozak's own files, which measure the sort variable
  directly (`totalme10_size`, `bmc10_value`, `bmc10_valuem`); the evidence is
  in `notes`. All other rows are `check`.
- `definition`: a one-line summary of the characteristic.
- `inputs`: the raw data needed, as `source: fields`, with sources separated by
  `; `. `BE items` is the Compustat book-equity set (seq, ceq, pstk, pstkrv,
  pstkl, at, lt, txditc).
- `notes`: discrete characteristics, ambiguities in the doc, and how a name was
  matched when it was not obvious.

Sources named in `inputs`:

- `crsp_monthly`, `crsp_daily`, `crsp_daily_index`: CRSP stock files and the
  daily index file (`ewretd`).
- `comp_annual`, `comp_quarterly`: Compustat fundamentals. Every row that uses
  them also needs the CRSP-Compustat link table, which is not repeated per row.
- `short_interest`: the Compustat supplemental short interest file.
- `ff_daily`: the daily Fama-French factors. This needs its own pull; the
  current `pull_CRSP_Compustat.py` pulls only the monthly factors.
- `ff49`: the Fama-French 49 industries. This needs an SIC to FF49 mapping
  (Kenneth French's `Siccodes49`), applied to CRSP `siccd`.

Kozak's data has 55 anomalies. These 5 are not in the paper:

- `divp`: dividend yield, defined in `anom_doc.pdf` (#13).
- `divg`, `exchsw`, `invaci`, `ipo`: not defined in `anom_doc.pdf`. Their names
  suggest dividend growth, exchange switching, abnormal capital investment and
  IPOs, but that is not confirmed. `exchsw` and `ipo` are about 80% empty.