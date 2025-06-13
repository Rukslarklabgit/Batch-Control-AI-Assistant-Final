from app.models import models
from app.core.database import SessionLocal

# Create a new DB session
db = SessionLocal()

#  Departments
departments = [
    models.Department(name="Packaging"),
    models.Department(name="Quality Control"),
    models.Department(name="Storage"),
    models.Department(name="Delivery")
]
db.add_all(departments)
db.commit()

#  Employees
employees = [
    models.Employee(name="John", department_id=departments[0].id),  # Packaging
    models.Employee(name="Sara", department_id=departments[1].id),  # QC
    models.Employee(name="Mike", department_id=departments[2].id),  # Storage
    models.Employee(name="Anna", department_id=departments[3].id),  # Delivery
    models.Employee(name="Vikram", department_id=departments[0].id),
    models.Employee(name="Riya", department_id=departments[2].id)
]
db.add_all(employees)
db.commit()

#  Products
products = [
    models.Product(name="Vitamin D Tablets", code="VDT"),
    models.Product(name="Pain Relief Gel", code="PRG"),
    models.Product(name="Cough Syrup", code="CSY")
]
db.add_all(products)
db.commit()

#  Batches
batches = [
    models.Batch(batch_code="VDT-052025-A", product_id=products[0].id),
    models.Batch(batch_code="PRG-052025-B", product_id=products[1].id),
    models.Batch(batch_code="CSY-052025-C", product_id=products[2].id)
]
db.add_all(batches)
db.commit()

#  Batch Tracking Records
tracking_logs = [
    # Vitamin D Batch
    models.BatchTracking(batch_id=batches[0].id, department_id=departments[0].id, employee_id=employees[0].id, status="Packed"),
    models.BatchTracking(batch_id=batches[0].id, department_id=departments[1].id, employee_id=employees[1].id, status="Inspected"),
    models.BatchTracking(batch_id=batches[0].id, department_id=departments[2].id, employee_id=employees[2].id, status="Stored"),
    models.BatchTracking(batch_id=batches[0].id, department_id=departments[3].id, employee_id=employees[3].id, status="Dispatched"),

    # Pain Relief Gel Batch
    models.BatchTracking(batch_id=batches[1].id, department_id=departments[0].id, employee_id=employees[4].id, status="Packed"),
    models.BatchTracking(batch_id=batches[1].id, department_id=departments[1].id, employee_id=employees[1].id, status="Inspected"),
    models.BatchTracking(batch_id=batches[1].id, department_id=departments[2].id, employee_id=employees[5].id, status="Stored"),

    # Cough Syrup Batch
    models.BatchTracking(batch_id=batches[2].id, department_id=departments[0].id, employee_id=employees[0].id, status="Packed"),
    models.BatchTracking(batch_id=batches[2].id, department_id=departments[3].id, employee_id=employees[3].id, status="Dispatched")
]
db.add_all(tracking_logs)
db.commit()

#  Done
db.close()
print(" Sample data inserted successfully with multiple entries!")
