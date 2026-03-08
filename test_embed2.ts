import { GoogleGenerativeAIEmbeddings } from "@langchain/google-genai";

async function testConfig(config: any) {
    try {
        const embedder = new GoogleGenerativeAIEmbeddings(config);
        const res = await embedder.embedDocuments(["Hello world"]);
        console.log(`Config ${JSON.stringify(config)} => Vector length: ${res[0].length}`);
    } catch (e: any) {
        console.log(`Config ${JSON.stringify(config)} => Error: ${e.message}`);
    }
}

async function run() {
    await testConfig({ apiKey: process.env.GEMINI_API_KEY, model: "text-embedding-004", taskType: "RETRIEVAL_DOCUMENT" });
    await testConfig({ apiKey: process.env.GEMINI_API_KEY, model: "models/text-embedding-004" });
    await testConfig({ apiKey: process.env.GEMINI_API_KEY, modelName: "text-embedding-004" });
    await testConfig({ apiKey: process.env.GEMINI_API_KEY, modelName: "embedding-001" });
}
run();
