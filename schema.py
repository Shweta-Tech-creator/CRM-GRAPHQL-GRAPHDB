import strawberry
from typing import List, Optional
from database import db
import uuid

@strawberry.type
class Account:
    id: strawberry.ID
    name: str = ""
    industry: Optional[str] = None
    revenue: Optional[float] = 0.0
    employees: Optional[int] = 0

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    @strawberry.field
    def contacts(self) -> List["Contact"]:
        query = "MATCH (a:Account {id: $id})<-[:WORKS_AT]-(c:Contact) RETURN c"
        with db.get_session() as session:
            result = session.run(query, id=self.id)
            return [Contact.from_dict(record["c"]) for record in result]

@strawberry.type
class Contact:
    id: strawberry.ID
    name: str = ""
    email: str = ""
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    @strawberry.field
    def account(self) -> Optional[Account]:
        query = "MATCH (c:Contact {id: $id})-[:WORKS_AT]->(a:Account) RETURN a"
        with db.get_session() as session:
            result = session.run(query, id=self.id).single()
            return Account.from_dict(result["a"]) if result else None

@strawberry.type
class Lead:
    id: strawberry.ID
    source: Optional[str] = None
    status: str = "NEW"
    
    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    @strawberry.field
    def contact(self) -> Optional[Contact]:
        query = "MATCH (l:Lead {id: $id})-[:HAS_CONTACT]->(c:Contact) RETURN c"
        with db.get_session() as session:
            result = session.run(query, id=self.id).single()
            return Contact.from_dict(result["c"]) if result else None

    @strawberry.field
    def deals(self) -> List["Deal"]:
        query = "MATCH (l:Lead {id: $id})-[:GENERATED_DEAL]->(d:Deal) RETURN d"
        with db.get_session() as session:
            result = session.run(query, id=self.id)
            return [Deal.from_dict(record["d"]) for record in result]

@strawberry.type
class Stage:
    id: strawberry.ID
    name: str
    order: Optional[int] = 0
    probability: float = 0.0

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@strawberry.type
class Deal:
    id: strawberry.ID
    value: float = 0.0
    expected_close_date: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    @strawberry.field
    def stage(self) -> Optional[Stage]:
        query = "MATCH (d:Deal {id: $id})-[:IN_STAGE]->(s:Stage) RETURN s"
        with db.get_session() as session:
            result = session.run(query, id=self.id).single()
            return Stage.from_dict(result["s"]) if result else None

@strawberry.type
class Activity:
    id: strawberry.ID
    type: str
    description: Optional[str] = None
    due_date: str

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    @strawberry.field
    def contact(self) -> Optional[Contact]:
        query = "MATCH (act:Activity {id: $id})-[:INVOLVES_CONTACT]->(c:Contact) RETURN c"
        with db.get_session() as session:
            result = session.run(query, id=self.id).single()
            return Contact.from_dict(result["c"]) if result else None

@strawberry.type
class DashboardMetrics:
    totalDealsValue: float
    conversionRate: float
    forecastedValue: float

@strawberry.type
class Query:
    @strawberry.field
    def account(self, id: strawberry.ID) -> Optional[Account]:
        query = "MATCH (a:Account {id: $id}) RETURN a"
        with db.get_session() as session:
            result = session.run(query, id=id).single()
            return Account.from_dict(result["a"]) if result else None

    @strawberry.field
    def lead(self, id: strawberry.ID) -> Optional[Lead]:
        query = "MATCH (l:Lead {id: $id}) RETURN l"
        with db.get_session() as session:
            result = session.run(query, id=id).single()
            return Lead.from_dict(result["l"]) if result else None

    @strawberry.field
    def activities(self, dueDate: Optional[str] = None) -> List[Activity]:
        query = "MATCH (act:Activity) "
        params = {}
        if dueDate:
            query += "WHERE act.due_date = $dueDate "
            params["dueDate"] = dueDate
        query += "RETURN act"
        with db.get_session() as session:
            result = session.run(query, **params)
            return [Activity.from_dict(record["act"]) for record in result]

    @strawberry.field
    def sales_dashboard(self) -> DashboardMetrics:
        with db.get_session() as session:
            pipeline_query = """
            MATCH (d:Deal)-[:IN_STAGE]->(s:Stage)
            RETURN coalesce(sum(d.value), 0.0) AS totalDealsValue,
                   coalesce(sum(d.value * s.probability), 0.0) AS forecastedValue
            """
            pipeline_res = session.run(pipeline_query).single()
            conversion_query = """
            MATCH (l:Lead) WITH count(l) AS totalLeads
            OPTIONAL MATCH (l)-[:GENERATED_DEAL]->(d:Deal)-[:IN_STAGE]->(s:Stage) WHERE s.probability = 1.0
            WITH totalLeads, count(d) AS wonDeals
            RETURN CASE WHEN totalLeads > 0 THEN (toFloat(wonDeals) / totalLeads) * 100 ELSE 0.0 END AS conversionRate
            """
            conversion_res = session.run(conversion_query).single()
            return DashboardMetrics(
                totalDealsValue=pipeline_res["totalDealsValue"],
                forecastedValue=pipeline_res["forecastedValue"],
                conversionRate=conversion_res["conversionRate"]
            )

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_account(self, name: str, industry: Optional[str] = None) -> Account:
        new_id = str(uuid.uuid4())
        query = "CREATE (a:Account {id: $id, name: $name, industry: $industry}) RETURN a"
        with db.get_session() as session:
            result = session.run(query, id=new_id, name=name, industry=industry).single()
            return Account.from_dict(result["a"])

    @strawberry.mutation
    def create_contact(self, name: str, email: str, accountId: Optional[strawberry.ID] = None, position: Optional[str] = None) -> Contact:
        new_id = str(uuid.uuid4())
        query = """
        CREATE (c:Contact {id: $id, name: $name, email: $email, position: $position})
        WITH c
        OPTIONAL MATCH (a:Account {id: $accountId})
        FOREACH (x IN CASE WHEN a IS NOT NULL THEN [1] ELSE [] END |
            CREATE (c)-[:WORKS_AT]->(a)
        )
        RETURN c
        """
        with db.get_session() as session:
            result = session.run(query, id=new_id, name=name, email=email, position=position, accountId=accountId).single()
            return Contact.from_dict(result["c"])

    @strawberry.mutation
    def create_lead(self, contactId: strawberry.ID, source: str) -> Lead:
        new_id = str(uuid.uuid4())
        query = """
        MATCH (c:Contact {id: $contactId})
        CREATE (l:Lead {id: $id, source: $source, status: 'NEW', created_at: datetime()})
        CREATE (l)-[:HAS_CONTACT]->(c)
        RETURN l
        """
        with db.get_session() as session:
            result = session.run(query, id=new_id, contactId=contactId, source=source).single()
            return Lead.from_dict(result["l"])

    @strawberry.mutation
    def update_lead_status(self, leadId: strawberry.ID, status: str) -> Lead:
        query = """
        MATCH (l:Lead {id: $leadId})
        SET l.status = $status
        RETURN l
        """
        with db.get_session() as session:
            result = session.run(query, leadId=leadId, status=status).single()
            if not result:
                raise Exception(f"Lead with id {leadId} not found")
            return Lead.from_dict(result["l"])

    @strawberry.mutation
    def create_stage(self, name: str, order: int, probability: float) -> Stage:
        new_id = str(uuid.uuid4())
        query = "CREATE (s:Stage {id: $id, name: $name, order: $order, probability: $probability}) RETURN s"
        with db.get_session() as session:
            result = session.run(query, id=new_id, name=name, order=order, probability=probability).single()
            return Stage.from_dict(result["s"])

    @strawberry.mutation
    def create_deal(self, leadId: strawberry.ID, value: float, stageId: strawberry.ID) -> Deal:
        new_id = str(uuid.uuid4())
        query = """
        MATCH (l:Lead {id: $leadId})
        MATCH (s:Stage {id: $stageId})
        CREATE (d:Deal {id: $id, value: $value})
        CREATE (l)-[:GENERATED_DEAL]->(d)
        CREATE (d)-[:IN_STAGE]->(s)
        RETURN d
        """
        with db.get_session() as session:
            result = session.run(query, id=new_id, leadId=leadId, value=value, stageId=stageId).single()
            return Deal.from_dict(result["d"])

    @strawberry.mutation
    def update_deal_stage(self, dealId: strawberry.ID, stageId: strawberry.ID) -> Deal:
        query = """
        MATCH (d:Deal {id: $dealId})
        MATCH (s:Stage {id: $stageId})
        OPTIONAL MATCH (d)-[r:IN_STAGE]->(:Stage)
        DELETE r
        CREATE (d)-[:IN_STAGE]->(s)
        RETURN d
        """
        with db.get_session() as session:
            result = session.run(query, dealId=dealId, stageId=stageId).single()
            return Deal.from_dict(result["d"])

    @strawberry.mutation
    def create_activity(self, contactId: strawberry.ID, type: str, description: str, dueDate: str) -> Activity:
        new_id = str(uuid.uuid4())
        query = """
        MATCH (c:Contact {id: $contactId})
        CREATE (act:Activity {id: $id, type: $type, description: $description, due_date: $dueDate})
        CREATE (act)-[:INVOLVES_CONTACT]->(c)
        RETURN act
        """
        with db.get_session() as session:
            result = session.run(query, id=new_id, contactId=contactId, type=type, description=description, dueDate=dueDate).single()
            return Activity.from_dict(result["act"])

schema = strawberry.Schema(query=Query, mutation=Mutation)
