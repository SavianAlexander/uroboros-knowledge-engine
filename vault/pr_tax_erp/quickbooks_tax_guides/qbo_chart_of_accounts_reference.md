# Puerto Rico Chart of Accounts (COA) for QuickBooks Online

## Statutory SURI Mapping & Account Classifications

`csv
Account Number,Account Name,Type,Detail Type,Description
1000,Operating Bank Account,Bank,Checking,Main operating bank account
1010,ATH Movil Clearing Account,Bank,Checking,Clearing account for ATH Movil Business deposits
1020,Credit Card Merchant Clearing,Bank,Checking,Clearing account for credit card processor deposits
1030,Petty Cash,Bank,CashOnHand,Petty cash for office incidentals
1100,Accounts Receivable (Patient Billing),Accounts Receivable,AccountsReceivable,Outstanding balances from patients
1150,Insurance Claims Clearing Account,Other Current Assets,OtherCurrentAssets,Clearing account for submitted insurance claims (Triple-S, MCS, etc.)
1200,SURI 10% Withholding Receivable,Other Current Assets,OtherCurrentAssets,10% tax credit withheld by insurance companies and clients
1500,Dental Equipment,Fixed Assets,MachineryEquipment,Dental Equipment Parent Account
1500-1,Dental Equipment:Dental Equipment - Cost,Fixed Assets,MachineryEquipment,Dental equipment cost basis (minimum 10% CRIM residual value)
1500-2,Dental Equipment:Dental Equipment - Accum Dep,Fixed Assets,MachineryEquipment,Accumulated depreciation for dental equipment
1510,Office Furniture & Fixtures,Fixed Assets,FurnitureFixtures,Office Furniture & Fixtures Parent Account
1510-1,Office Furniture & Fixtures:Office Furniture - Cost,Fixed Assets,FurnitureFixtures,Office furniture cost basis (minimum 10% CRIM residual value)
1510-2,Office Furniture & Fixtures:Office Furniture - Accum Dep,Fixed Assets,FurnitureFixtures,Accumulated depreciation for office furniture
1520,Computer Hardware,Fixed Assets,OtherFixedAssets,Computer Hardware Parent Account
1520-1,Computer Hardware:Computer Hardware - Cost,Fixed Assets,OtherFixedAssets,Computer hardware cost basis (minimum 20% CRIM residual value)
1520-2,Computer Hardware:Computer Hardware - Accum Dep,Fixed Assets,OtherFixedAssets,Accumulated depreciation for computer hardware
1530,Leasehold Improvements,Fixed Assets,LeaseholdImprovements,Leasehold Improvements Parent Account
1530-1,Leasehold Improvements:Leasehold Improvements - Cost,Fixed Assets,LeaseholdImprovements,Cost basis for leasehold improvements
1530-2,Leasehold Improvements:Leasehold Improvements - Accum Dep,Fixed Assets,LeaseholdImprovements,Accumulated depreciation for leasehold improvements
2000,Accounts Payable,Accounts Payable,AccountsPayable,Outstanding vendor bills
2090,Federal Payroll Taxes Payable,Other Current Liabilities,OtherCurrentLiabilities,Clearing account for federal payroll tax deposits (FICA/FUTA)
2095,Direct Deposit Clearing,Other Current Liabilities,OtherCurrentLiabilities,Clearing account for employee net payroll direct deposits
2100,SURI 10% Withholding Payable,Other Current Liabilities,OtherCurrentLiabilities,10% tax withheld from contractors/dental labs (Form 480.9B)
2200,IVU Payable,Other Current Liabilities,SalesTaxPayable,IVU collected on retail sales (10.5% state IVU)
2210,IVU B2B Payable (4%),Other Current Liabilities,SalesTaxPayable,4% B2B IVU collected on chair rentals or other services
2300,CRIM Payable,Other Current Liabilities,OtherCurrentLiabilities,Estimated personal property tax liability due to CRIM
2400,Patente Municipal Payable,Other Current Liabilities,OtherCurrentLiabilities,Estimated municipal license tax liability
2500,SURI Patronal Withholding Payable,Other Current Liabilities,PayrollTaxPayable,PR income tax withheld from employee wages (Form 499 R-1B)
2510,PR SUTA Payable,Other Current Liabilities,PayrollTaxPayable,Puerto Rico Unemployment Insurance tax payable
2520,PR SINOT Payable,Other Current Liabilities,PayrollTaxPayable,SINOT disability insurance tax payable
2530,PR Chofres Payable,Other Current Liabilities,PayrollTaxPayable,Chofres driver temporary disability tax payable
2540,CFSE Payable,Other Current Liabilities,OtherCurrentLiabilities,Liability account for CFSE worker's compensation premiums
3000,Owner's Equity,Equity,OwnerEquity,Owner's capital contribution
3010,Owner's Draw,Equity,OwnerEquity,Owner's personal draws
3020,Capital Stock,Equity,CommonStock,PSC corporate stock value (Planilla 482)
3030,Retained Earnings,Equity,RetainedEarnings,Accumulated corporate earnings (Planilla 482)
4000,Clinical Exempt Revenue,Income,ServiceFeeIncome,Dental services and diagnostics, exempt from IVU
4100,Retail Taxable Revenue (OTC Products),Income,SalesOfProductIncome,Retail sales of OTC products subject to 11.5% IVU
4200,Retail Exempt Revenue (Prescriptions),Income,SalesOfProductIncome,Retail sales of prescribed medicines (neuropathic pills), exempt from IVU
4300,Rental Income / B2B Services (4% IVU),Income,ServiceFeeIncome,Chair rental income from associate dentists subject to 4% B2B IVU
5000,Dental Lab Fees,Cost of Goods Sold,SuppliesMaterialsCogs,Payments to dental labs (subject to 10% withholding)
5010,Dental & Medical Supplies,Cost of Goods Sold,SuppliesMaterialsCogs,Clinical supplies (anesthetics, gloves, composite)
6000,Salaries & Wages (W-2),Expense,Wages,Gross wages paid to W-2 employees (including hygienists, assistants)
6010,Payroll Taxes - FICA Employer,Expense,PayrollTaxes,Employer's portion of Social Security and Medicare taxes
6020,Payroll Taxes - FUTA (Federal),Expense,PayrollTaxes,Federal Unemployment Tax
6030,Payroll Taxes - PR SUTA,Expense,PayrollTaxes,Puerto Rico Unemployment Insurance
6040,Payroll Taxes - PR SINOT,Expense,PayrollTaxes,SINOT disability insurance tax
6050,Payroll Taxes - PR Chofres,Expense,PayrollTaxes,Chofres driver temporary disability tax
6060,CFSE Worker's Comp Insurance,Expense,PayrollTaxes,Corporacion del Fondo del Seguro del Estado insurance premium
6070,Medical Malpractice Insurance,Expense,Insurance,Mandatory medical malpractice insurance premiums
6080,Laundry & Uniforms,Expense,OtherBusinessExpenses,OSHA compliant clinical protective wear laundering and uniforms
6100,CRIM Expense,Expense,TaxesPaid,CRIM personal property tax expense
6110,Patente Municipal Expense,Expense,TaxesPaid,Patente Municipal volume of business tax expense
6200,Rent Expense (Office),Expense,RentOrLeaseOfBuildings,Monthly office rent (NOT subject to 10% withholding)
6210,Utilities (Water & Power),Expense,Utilities,Water (PRASA) and Power (LUMA) payments
6220,Biohazardous Waste Disposal,Expense,OtherBusinessExpenses,Licensed biomedical waste disposal services (DRNA/EPA compliance)
6300,Legal & Professional Services,Expense,LegalProfessionalFees,Payments to lawyers, CPAs, consultants (subject to 10% withholding)
6310,B2B Service Tax Expense (IVU Paid),Expense,TaxesPaid,IVU paid on business services (4% or 11.5%), booked as expense
6400,Meals - 50% Deducible,Expense,TravelMeals,Business meals subject to 50% deduction rule
6410,Meals - 50% Non-Deducible,Expense,TravelMeals,Portion of meals disallowed for tax purposes (booked separately)
6430,Patient Refreshments,Expense,TravelMeals,Patient refreshments (water coffee snacks) - 100% deductible
6435,Employee Break Room Supplies,Expense,TravelMeals,Employee break room supplies (water coffee sodas snacks) - 100% deductible
6500,Continuing Education & Seminars,Expense,OtherBusinessExpenses,Continuing education dental courses
6600,Licenses & Permits,Expense,OtherBusinessExpenses,Dental licenses and radiologic permits (excluding CCDPR colegiación)
6610,CCDPR Dues & Professional Memberships,Expense,OtherBusinessExpenses,Colegio de Cirujanos Dentistas de Puerto Rico mandatory dues
6700,Merchant & Processing Fees,Expense,BankCharges,Credit card processing fees and ATH Movil transaction fees

`
