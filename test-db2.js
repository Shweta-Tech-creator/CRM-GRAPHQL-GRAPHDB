const neo4j = require('neo4j-driver');
require('dotenv').config();

const driver = neo4j.driver(
    process.env.NEO4J_URI,
    neo4j.auth.basic('neo4j', process.env.NEO4J_PASSWORD)
);

async function test() {
    console.log("Testing connection to:", process.env.NEO4J_URI);
    console.log("User: neo4j");
    try {
        await driver.verifyConnectivity();
        console.log("Connection successful");
    } catch (e) {
        console.error("Connection failed:", e.message);
    } finally {
        await driver.close();
    }
}
test();
