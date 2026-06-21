from billingdept import BillingDepartment
from techdept import TechnicalDepartment
from ticketanalyzer import TicketClassifier
class OmniMaster:
    def __init__(self,fast_model,heavy_model):
        self.classifier=TicketClassifier(fast_model)
        self.billing_dept=BillingDepartment(heavy_model)
        self.tech_dept=TechnicalDepartment(heavy_model)

    def analyze_and_route(self,email):
        category_obj = self.classifier.categorize(email)
        dept_name = category_obj.department
        if dept_name == "Technical":
            return self.tech_dept.process_ticket(email)
        if dept_name == "Billing":
            return self.billing_dept.process_ticket(email)
        else:
            return {"status": "General inquiry routed to human support."}


