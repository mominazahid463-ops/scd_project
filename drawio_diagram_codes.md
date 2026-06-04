# Draw.io Import Codes (PlantUML)

You can generate these diagrams directly in Draw.io! 
To do this in Draw.io, go to **Arrange > Insert > Advanced > PlantUML...** and paste the code for the respective diagram.

## 1. Use Case Diagram
```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
actor "User" as User

rectangle "Personal Finance Tracker" {
  usecase "Manage Transactions" as UC_MT
  usecase "Add Transaction" as UC_AT
  usecase "Edit Transaction" as UC_ET
  usecase "Delete Transaction" as UC_DT
  usecase "View Transactions" as UC_VT
  
  usecase "Manage Categories" as UC_MC
  usecase "Add Custom Category" as UC_ACC
  usecase "Delete Category" as UC_DC
  
  usecase "Manage Budget" as UC_MB
  usecase "Set Budget Limit" as UC_SBL
  usecase "View Budget Status" as UC_VBS
  usecase "Receive Budget Alert" as UC_RBA
  
  usecase "View Dashboard" as UC_VD
  
  usecase "View Reports" as UC_VR
  usecase "View Pie Chart" as UC_VPC
  usecase "View Bar Chart" as UC_VBC
  usecase "Filter by Date Range" as UC_FDR
  
  usecase "Export CSV" as UC_EC
}

User --> UC_MT
User --> UC_MC
User --> UC_MB
User --> UC_VD
User --> UC_VR
User --> UC_EC

UC_MT ..> UC_AT : <<include>>
UC_MT ..> UC_ET : <<include>>
UC_MT ..> UC_DT : <<include>>
UC_MT ..> UC_VT : <<include>>

UC_MC ..> UC_ACC : <<include>>
UC_MC ..> UC_DC : <<include>>

UC_MB ..> UC_SBL : <<include>>
UC_MB ..> UC_VBS : <<include>>
UC_VBS <.. UC_RBA : <<extend>>

UC_VR ..> UC_VPC : <<include>>
UC_VR ..> UC_VBC : <<include>>
UC_VR ..> UC_FDR : <<include>>
@enduml
```

## 2. Class Diagram
```plantuml
@startuml
class Transaction {
  id: int
  amount: float
  date: str
  category_id: int
  type: str
  note: str
  add()
  edit()
  delete()
  get_all()
  filter_by_date()
  filter_by_category()
}

class Category {
  id: int
  name: str
  is_custom: bool
  add()
  delete()
  get_all()
}

class Budget {
  id: int
  category_id: int
  monthly_limit: float
  current_spent: float
  set_limit()
  get_status()
  calculate_percentage()
}

class DatabaseManager {
  db_path: str
  connect()
  disconnect()
  execute_query()
  fetch_all()
  fetch_one()
}

class ReportGenerator {
  generate_pie_chart()
  generate_bar_chart()
  filter_by_date_range()
}

class CSVExporter {
  file_path: str
  export()
  choose_path()
}

class AlertService {
  check_threshold()
  trigger_warning()
  trigger_exceeded()
}

Transaction "*" --> "1" Category : many-to-one
Budget "1" --> "1" Category : one-to-one
Transaction ..> DatabaseManager : dependency
Budget ..> DatabaseManager : dependency
Category ..> DatabaseManager : dependency
ReportGenerator ..> Transaction : dependency
AlertService -- Budget : association
CSVExporter ..> Transaction : dependency
@enduml
```

## 3. Sequence Diagram (Add New Transaction)
```plantuml
@startuml
actor User
participant UI_Form
participant TransactionController
participant Validator
participant DatabaseManager
participant AlertService

User -> UI_Form : fills form and clicks Save
activate UI_Form
UI_Form -> TransactionController : add_transaction(data)
activate TransactionController
TransactionController -> Validator : validate(data)
activate Validator
Validator --> TransactionController : returns valid/invalid
deactivate Validator

alt invalid
    TransactionController --> UI_Form : error
    UI_Form --> User : shows error message
else valid
    TransactionController -> DatabaseManager : execute_query()
    activate DatabaseManager
    DatabaseManager --> TransactionController : returns success
    deactivate DatabaseManager
    
    TransactionController -> AlertService : check_threshold(category_id)
    activate AlertService
    AlertService --> TransactionController : returns alert level (none / warning / exceeded)
    deactivate AlertService
    
    TransactionController --> UI_Form : success and alert status
    UI_Form --> User : displays success message and alert if triggered
end
deactivate TransactionController
deactivate UI_Form
@enduml
```

## 4. Activity Diagram (Budget Setting and Alert Flow)
```plantuml
@startuml
|User|
start
:User opens Budget Screen;
repeat
  :Enters category and monthly limit;
  |System|
  if (Decision: Input valid?) then (No)
    :Show validation error;
    |User|
  else (Yes)
    |System|
    :Save budget to database;
    |User|
    break
  endif
repeat while ()

|User|
:User navigates to Add Transaction;
repeat
  :User enters transaction details;
  |System|
  if (Decision: Transaction input valid?) then (No)
    :Show error;
    |User|
  else (Yes)
    |System|
    :Save transaction to database;
    break
  endif
repeat while ()

|System|
:System calculates % spent in that category;

if (Decision: % spent >= 100%?) then (Yes)
  :Show "Budget Exceeded" alert;
  stop
else (No)
  if (Decision: % spent >= 80%?) then (Yes)
    :Show "Approaching Limit" warning;
    stop
  else (No)
    :Show success message;
    stop
  endif
endif
@enduml
```

## 5. Entity Relationship Diagram (ERD)
```plantuml
@startuml
entity "CATEGORY" as cat {
  *category_id : PK
  --
  name
  is_custom : boolean
}

entity "TRANSACTION" as tx {
  *transaction_id : PK
  --
  amount
  date
  type
  note
  category_id : FK
}

entity "BUDGET" as bud {
  *budget_id : PK
  --
  monthly_limit
  current_spent
  category_id : FK
}

cat ||--o{ tx : "categorizes"
cat ||--|| bud : "has"
@enduml
```
