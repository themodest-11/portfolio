from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BLUE = Font(name="Arial", size=10, color="0000FF")
BLACK = Font(name="Arial", size=10, color="000000")
BOLD = Font(name="Arial", size=10, bold=True)
HEADER_FONT = Font(name="Arial", size=11, bold=True, color="FFFFFF")
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
YELLOW = PatternFill("solid", fgColor="FFFF00")
LABEL_FONT = Font(name="Arial", size=10)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

wb = Workbook()

# ---------------------------------------------------------------
# Sheet 1: Assumptions (baseline pulled from the loan portfolio)
# ---------------------------------------------------------------
ws = wb.active
ws.title = "Assumptions"
ws.column_dimensions["A"].width = 34
ws.column_dimensions["B"].width = 16
ws.column_dimensions["C"].width = 50

ws["A1"] = "Bank Loan Portfolio — Scenario Model: Assumptions"
ws["A1"].font = Font(name="Arial", size=13, bold=True, color="1F4E79")
ws.merge_cells("A1:C1")

rows = [
    ("Base disbursed volume ($)", 445_602_650, "Source: sql/02_management_reporting.sql, sum(loan_amount), real portfolio (39,717 loans, data/financial_loan.csv)"),
    ("Base interest rate (annual, %)", 0.1202, "Source: loans.int_rate, real portfolio average"),
    ("Base default rate (%)", 0.1417, "Source: share of loan_status = 'Charged Off', real portfolio"),
    ("Loss given default, LGD (%)", 0.60, "Assumption — typical unsecured personal loan LGD; replace with the bank's own figure"),
    ("Cost of funds (annual, %)", 0.05, "Assumption — placeholder funding cost; replace with treasury rate"),
    ("Operating cost ratio (% of volume)", 0.02, "Assumption — placeholder opex ratio; replace with actual cost allocation"),
]
r = 3
ws.cell(row=r, column=1, value="Assumption").font = BOLD
ws.cell(row=r, column=2, value="Value").font = BOLD
ws.cell(row=r, column=3, value="Source / note").font = BOLD
r += 1
first_data_row = r
for label, val, note in rows:
    ws.cell(row=r, column=1, value=label).font = LABEL_FONT
    c = ws.cell(row=r, column=2, value=val)
    c.font = BLUE
    c.fill = YELLOW
    c.number_format = "0.00%" if val < 1 and "$" not in label else "$#,##0"
    ws.cell(row=r, column=3, value=note).font = Font(name="Arial", size=9, italic=True, color="595959")
    r += 1

# named-ish references by row number for formulas in other sheets
VOL_ROW, RATE_ROW, DEF_ROW, LGD_ROW, COF_ROW, OPEX_ROW = range(first_data_row, first_data_row + 6)

ws.cell(row=r + 1, column=1, value="Legend: yellow = editable input. Black = formula, recalculates automatically.").font = \
    Font(name="Arial", size=9, italic=True, color="595959")

# ---------------------------------------------------------------
# Sheet 2: Scenarios (Base / Optimistic / Pessimistic)
# ---------------------------------------------------------------
ws2 = wb.create_sheet("Scenarios")
headers = [
    "Scenario", "Volume change (%)", "Rate change (pp)", "Default rate change (pp)",
    "Scenario volume ($)", "Scenario rate (%)", "Scenario default rate (%)",
    "Revenue ($)", "Expected credit loss ($)", "Cost of funds ($)",
    "Operating cost ($)", "Net profit ($)", "Net margin (% of volume)",
]
for i, h in enumerate(headers, start=1):
    c = ws2.cell(row=1, column=i, value=h)
    c.font = HEADER_FONT
    c.fill = HEADER_FILL
    c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws2.column_dimensions[get_column_letter(i)].width = 15

scenario_rows = [
    ("Base", 0.00, 0.000, 0.000),
    ("Optimistic", 0.15, -0.010, -0.02),
    ("Pessimistic", -0.15, 0.015, 0.04),
]

A = "Assumptions"
for i, (name, dvol, drate, ddef) in enumerate(scenario_rows, start=2):
    ws2.cell(row=i, column=1, value=name).font = BOLD

    c = ws2.cell(row=i, column=2, value=dvol)
    c.font = BLUE; c.fill = YELLOW; c.number_format = "0.0%"
    c = ws2.cell(row=i, column=3, value=drate)
    c.font = BLUE; c.fill = YELLOW; c.number_format = "0.00%"
    c = ws2.cell(row=i, column=4, value=ddef)
    c.font = BLUE; c.fill = YELLOW; c.number_format = "0.00%"

    # Scenario volume / rate / default rate
    c = ws2.cell(row=i, column=5, value=f"='{A}'!$B${VOL_ROW}*(1+B{i})")
    c.font = BLACK; c.number_format = "$#,##0"
    c = ws2.cell(row=i, column=6, value=f"='{A}'!$B${RATE_ROW}+C{i}")
    c.font = BLACK; c.number_format = "0.00%"
    c = ws2.cell(row=i, column=7, value=f"='{A}'!$B${DEF_ROW}+D{i}")
    c.font = BLACK; c.number_format = "0.00%"

    # Revenue, expected loss, cost of funds, opex, net profit, margin
    c = ws2.cell(row=i, column=8, value=f"=E{i}*F{i}")
    c.font = BLACK; c.number_format = "$#,##0"
    c = ws2.cell(row=i, column=9, value=f"=E{i}*G{i}*'{A}'!$B${LGD_ROW}")
    c.font = BLACK; c.number_format = "$#,##0"
    c = ws2.cell(row=i, column=10, value=f"=E{i}*'{A}'!$B${COF_ROW}")
    c.font = BLACK; c.number_format = "$#,##0"
    c = ws2.cell(row=i, column=11, value=f"=E{i}*'{A}'!$B${OPEX_ROW}")
    c.font = BLACK; c.number_format = "$#,##0"
    c = ws2.cell(row=i, column=12, value=f"=H{i}-I{i}-J{i}-K{i}")
    c.font = BOLD; c.number_format = "$#,##0"
    c = ws2.cell(row=i, column=13, value=f"=L{i}/E{i}")
    c.font = BLACK; c.number_format = "0.00%"

    for col in range(1, 14):
        ws2.cell(row=i, column=col).border = BORDER

ws2.freeze_panes = "A2"

# ---------------------------------------------------------------
# Sheet 3: Sensitivity grid — Net profit by Volume change x Rate change
# (Pessimistic default-rate held at Base; edit B2 to stress-test it)
# ---------------------------------------------------------------
ws3 = wb.create_sheet("Sensitivity_Grid")
ws3["A1"] = "Net profit ($) sensitivity — Volume change (rows) x Rate change in pp (columns)"
ws3["A1"].font = BOLD
ws3.merge_cells("A1:G1")

ws3["A2"] = "Default rate change held at (pp):"
ws3["A2"].font = LABEL_FONT
ws3["B2"] = 0.00
ws3["B2"].font = BLUE
ws3["B2"].fill = YELLOW
ws3["B2"].number_format = "0.00%"

vol_changes = [-0.20, -0.10, 0.00, 0.10, 0.20]
rate_changes = [-0.02, -0.01, 0.00, 0.01, 0.02]

header_row = 4
ws3.cell(row=header_row, column=1, value="Volume change \\ Rate change").font = BOLD
for j, rc in enumerate(rate_changes, start=2):
    c = ws3.cell(row=header_row, column=j, value=rc)
    c.font = BOLD
    c.number_format = "0.00%"
    ws3.column_dimensions[get_column_letter(j)].width = 14
ws3.column_dimensions["A"].width = 26

for i, vc in enumerate(vol_changes, start=header_row + 1):
    c = ws3.cell(row=i, column=1, value=vc)
    c.font = BOLD
    c.number_format = "0.0%"
    for j, rc in enumerate(rate_changes, start=2):
        col_letter = get_column_letter(j)
        # Full formula per cell: recompute net profit directly from Assumptions
        # using this cell's volume/rate deltas and the sheet-level default delta ($B$2)
        formula = (
            f"=('{A}'!$B${VOL_ROW}*(1+$A{i}))*('{A}'!$B${RATE_ROW}+{col_letter}${header_row})"
            f"-('{A}'!$B${VOL_ROW}*(1+$A{i}))*('{A}'!$B${DEF_ROW}+$B$2)*'{A}'!$B${LGD_ROW}"
            f"-('{A}'!$B${VOL_ROW}*(1+$A{i}))*'{A}'!$B${COF_ROW}"
            f"-('{A}'!$B${VOL_ROW}*(1+$A{i}))*'{A}'!$B${OPEX_ROW}"
        )
        cell = ws3.cell(row=i, column=j, value=formula)
        cell.font = BLACK
        cell.number_format = "$#,##0"
        cell.border = BORDER

wb.save("/home/claude/bank-loan-portfolio/excel/scenario_model.xlsx")
print("saved")
