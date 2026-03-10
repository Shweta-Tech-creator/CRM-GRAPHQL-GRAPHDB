const typeDefs = `#graphql
    type Account @node {
        id: ID! @id
        name: String!
        industry: String
        revenue: Float
        employees: Int
        contacts: [Contact!]! @relationship(type: "WORKS_AT", direction: IN)
    }

    type Contact @node {
        id: ID! @id
        firstName: String!
        lastName: String!
        email: String!
        phone: String
        company: String
        position: String
        account: [Account!]! @relationship(type: "WORKS_AT", direction: OUT)
        leads: [Lead!]! @relationship(type: "HAS_CONTACT", direction: IN)
        activities: [Activity!]! @relationship(type: "INVOLVES_CONTACT", direction: IN)
    }

    type Lead @node {
        id: ID! @id
        firstName: String!
        lastName: String!
        email: String!
        company: String
        contact: [Contact!]! @relationship(type: "HAS_CONTACT", direction: OUT)
        source: String
        status: String! @default(value: "new") # new, contacted, qualified, proposal, negotiation
        assigned_to: String
        created_at: DateTime! @timestamp(operations: [CREATE])
        deals: [Deal!]! @relationship(type: "GENERATED_DEAL", direction: OUT)
    }

    type Stage @node {
        id: ID! @id
        name: String!
        order: Int!
        probability: Float! # 0.0 to 1.0
        deals: [Deal!]! @relationship(type: "IN_STAGE", direction: IN)
    }

    type Deal @node {
        id: ID! @id
        lead: [Lead!]! @relationship(type: "GENERATED_DEAL", direction: IN)
        value: Float!
        stage: [Stage!]! @relationship(type: "IN_STAGE", direction: OUT)
        expected_close_date: DateTime
        won_date: DateTime
    }

    type Activity @node {
        id: ID! @id
        contact: [Contact!]! @relationship(type: "INVOLVES_CONTACT", direction: OUT)
        type: String! # call, email, meeting, task
        description: String
        due_date: DateTime
        completed_at: DateTime
    }

    type DashboardMetrics {
        totalDealsValue: Float!
        conversionRate: Float!
        forecastedValue: Float!
    }

    type Query {
        salesDashboard: DashboardMetrics!
    }
`;

const resolvers = {
    Query: {
        salesDashboard: async (_root, _args, context) => {
            if (!context.driver) {
                throw new Error("Neo4j driver not available in context");
            }

            const session = context.driver.session(context.sessionConfig || {});
            try {
                // Calculate Total Pipeline logic and forecasted value
                const pipelineQuery = `
                    MATCH (d:Deal)-[:IN_STAGE]->(s:Stage)
                    RETURN coalesce(sum(d.value), 0.0) AS totalDealsValue,
                           coalesce(sum(d.value * s.probability), 0.0) AS forecastedValue
                `;

                // Conversion rate: (Leads that generated a won deal / Total Leads) * 100
                const conversionQuery = `
                    MATCH (l:Lead)
                    WITH count(l) AS totalLeads
                    OPTIONAL MATCH (l)-[:GENERATED_DEAL]->(d:Deal)-[:IN_STAGE]->(s:Stage)
                    WHERE s.probability = 1.0
                    WITH totalLeads, count(d) AS wonDeals
                    RETURN CASE WHEN totalLeads > 0 THEN (toFloat(wonDeals) / totalLeads) * 100 ELSE 0.0 END AS conversionRate
                `;

                const pipelineRes = await session.run(pipelineQuery);
                const pipelineRecord = pipelineRes.records[0];
                const totalDealsValue = pipelineRecord ? pipelineRecord.get('totalDealsValue') : 0;
                const forecastedValue = pipelineRecord ? pipelineRecord.get('forecastedValue') : 0;

                const conversionRes = await session.run(conversionQuery);
                const conversionRecord = conversionRes.records[0];
                const conversionRate = conversionRecord ? conversionRecord.get('conversionRate') : 0;

                return {
                    totalDealsValue,
                    conversionRate,
                    forecastedValue
                };
            } finally {
                await session.close();
            }
        }
    }
};

module.exports = { typeDefs, resolvers };
