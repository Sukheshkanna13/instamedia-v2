import 'dotenv/config';
import { GoogleGenerativeAIEmbeddings } from "@langchain/google-genai";

async function testConfig(config: any) {
    try {
        const embedder = new GoogleGenerativeAIEmbeddings(config);
        const res = await embedder.embedDocuments(["Hello world"]);
        console.log(`Config ${JSON.stringify(config).replace(process.env.GEMINI_API_KEY!, "HIDDEN")} => Vector length: ${res[0]?.length}`);
    } catch (e: any) {
        console.log(`Config => Error: ${e.message}`);
    }
}

async function run() {
    console.log("Key defined:", !!process.env.GEMINI_API_KEY);
    await testConfig({ apiKey: process.env.GEMINI_API_KEY, model: "text-embedding-004" });
    await testConfig({ apiKey: process.env.GEMINI_API_KEY, modelName: "text-embedding-004", taskType: "RETRIEVAL_DOCUMENT" });
    await testConfig({ apiKey: process.env.GEMINI_API_KEY, modelName: "embedding-001" });
}
run();
