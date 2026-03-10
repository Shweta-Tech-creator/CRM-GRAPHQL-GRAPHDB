require('dotenv').config();
const { ApolloServer } = require('@apollo/server');
const { startStandaloneServer } = require('@apollo/server/standalone');
const neo4j = require('neo4j-driver');
const { Neo4jGraphQL } = require('@neo4j/graphql');
const { typeDefs, resolvers } = require('./src/schema');

async function startServer() {
    // 1. Create a Neo4j driver instance using the credentials from .env
    const driver = neo4j.driver(
        process.env.NEO4J_URI,
        neo4j.auth.basic(process.env.NEO4J_USERNAME || process.env.NEO4J_USER, process.env.NEO4J_PASSWORD)
    );

    // 2. Initialize the Neo4j/GraphQL integration
    const neoSchema = new Neo4jGraphQL({ typeDefs, resolvers, driver });

    // 3. Generate executable schema
    const schema = await neoSchema.getSchema();

    // Validate database constraints and indexes based on GraphQL type definitions
    await neoSchema.assertIndexesAndConstraints({
        sessionConfig: { database: process.env.NEO4J_DATABASE || 'neo4j' }
    });

    // 4. Setup Apollo Server
    const server = new ApolloServer({
        schema,
    });

    // 5. Start the server
    const { url } = await startStandaloneServer(server, {
        // Inject the driver and sessionConfig into the context
        context: async ({ req }) => ({
            req,
            driver,
            sessionConfig: { database: process.env.NEO4J_DATABASE || 'neo4j' }
        }),
        listen: { port: process.env.PORT || 4000 },
    });

    console.log(`🚀 CRM Backend API ready at ${url}`);
}

startServer().catch(error => {
    console.error("Failed to start server:", error);
});
